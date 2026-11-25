import streamlit as st
import fitz  # PyMuPDF
import openai
import matplotlib.pyplot as plt
import numpy as np
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)


def limpiar_json(texto):
    """Quita bloques ```json ... ``` por si el modelo los incluye."""
    texto = (texto or "").strip()
    if texto.startswith("```"):
        texto = texto.strip("`")
        if texto.lower().startswith("json"):
            texto = texto[4:]
    return texto.strip()


def analizar_candidato(texto_cv, descripcion_puesto):
    """Evalúa la compatibilidad del CV contra el puesto."""
    prompt = (
        f"Actúa como un reclutador experto. Analiza el CV frente a esta descripción del puesto: '{descripcion_puesto}'\n\n"
        "Responde SOLO con un JSON con estos campos:\n"
        "- 'puntuacion': número entero del 1 al 100.\n"
        "- 'analisis': resumen técnico breve.\n"
        "- 'habilidades': lista de 5 a 8 objetos con el formato "
        "[{\"nombre\": \"Python\", \"nivel\": 7}], donde 'nivel' es un número del 1 al 10.\n"
        "- 'es_potencial': booleano (true si la puntuación > 60).\n\n"
        f"CV del candidato: {texto_cv[:3000]}"
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        contenido = response.choices[0].message.content
        return json.loads(limpiar_json(contenido))
    except Exception as e:
        return {
            "puntuacion": 0,
            "analisis": f"Error: {e}",
            "habilidades": [],
            "es_potencial": False,
        }


def normalizar_habilidades(h):
    """Acepta lista o diccionario y devuelve [{'nombre', 'nivel'}] con nivel de 0 a 10."""
    if isinstance(h, dict):
        h = [{"nombre": k, "nivel": v} for k, v in h.items()]
    if not isinstance(h, list):
        return []

    limpias = []
    for item in h:
        if not isinstance(item, dict):
            continue
        nombre = str(item.get("nombre", "")).strip()
        try:
            nivel = float(item.get("nivel"))
        except (TypeError, ValueError):
            continue
        if nombre:
            if nivel > 10:  # si vino en escala 0-100
                nivel = nivel / 10
            limpias.append({"nombre": nombre, "nivel": max(0, min(10, nivel))})
    return limpias


def crear_grafico_habilidades(lista_habilidades):
    habilidades = normalizar_habilidades(lista_habilidades)
    if len(habilidades) < 3:
        st.warning("No hay datos suficientes para el gráfico.")
        return

    nombres = [h["nombre"] for h in habilidades]
    valores = [h["nivel"] for h in habilidades]
    angles = np.linspace(0, 2 * np.pi, len(nombres), endpoint=False).tolist()
    valores += valores[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
    ax.fill(angles, valores, color="#1f77b4", alpha=0.3)
    ax.plot(angles, valores, color="#1f77b4", linewidth=2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(nombres, fontsize=8)
    ax.set_ylim(0, 10)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# --- Interfaz ---
st.set_page_config(page_title="Pro-Recruiter AI", layout="wide")
st.title("📊 Sistema Inteligente de Análisis de Candidatos")

job_desc = st.text_area("Descripción del Puesto:")
files = st.file_uploader("Subir CVs", accept_multiple_files=True, type="pdf")
debug = st.checkbox("Mostrar respuesta cruda del modelo (debug)")

if st.button("Analizar y Filtrar") and job_desc and files:
    for f in files:
        pdf_bytes = f.read()

        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            texto = doc[0].get_text() if len(doc) > 0 else ""

        if not texto.strip():
            st.warning(f"{f.name}: no se pudo extraer texto (¿PDF escaneado?).")
            continue

        resultado = analizar_candidato(texto, job_desc)

        try:
            puntuacion = float(resultado.get("puntuacion", 0))
        except (TypeError, ValueError):
            puntuacion = 0
        es_potencial = puntuacion > 60

        tipo = "✅ Potencial" if es_potencial else "❌ No Apto"

        with st.expander(f"{tipo}: {f.name} (Score: {int(puntuacion)})", expanded=True):
            col_texto, col_grafico = st.columns([1, 1.5])

            with col_texto:
                st.write("**Análisis:**", resultado.get("analisis"))

                pdf_data = base64.b64encode(pdf_bytes).decode("utf-8")
                pdf_display = (
                    f'<a href="data:application/pdf;base64,{pdf_data}" target="_blank">'
                    "📄 Ver CV Original (PDF)</a>"
                )
                st.markdown(pdf_display, unsafe_allow_html=True)

            with col_grafico:
                if es_potencial:
                    crear_grafico_habilidades(resultado.get("habilidades"))
                else:
                    st.info("No hay gráfico de habilidades disponible.")

            if debug:
                st.json(resultado)