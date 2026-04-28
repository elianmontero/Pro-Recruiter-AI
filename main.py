import streamlit as st
import fitz
import openai
import matplotlib.pyplot as plt
import numpy as np
import os
from dotenv import load_dotenv
import json
import base64

load_dotenv()
client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY") 
)

def analizar_candidato(texto_cv, descripcion_puesto):
    """Evalúa la compatibilidad del CV contra el puesto."""
    prompt = (
        f"Actúa como un reclutador experto. Analiza el CV frente a esta descripción del puesto: '{descripcion_puesto}'\n\n"
        "Genera un JSON con los siguientes campos:\n"
        "- 'puntuacion': número del 1 al 100.\n"
        "- 'analisis': resumen técnico breve.\n"
        "- 'habilidades': lista de objetos [{'nombre': '...', 'nivel': ...}].\n"
        "- 'es_potencial': booleano (true si la puntuación > 60).\n\n"
        f"CV del candidato: {texto_cv[:2000]}"
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"puntuacion": 0, "analisis": f"Error: {e}", "habilidades": [], "es_potencial": False}

def crear_grafico_habilidades(lista_habilidades):
    if not lista_habilidades or not isinstance(lista_habilidades, list):
        st.warning("No hay datos suficientes.")
        return

    nombres = [h['nombre'] for h in lista_habilidades]
    valores = [h['nivel'] for h in lista_habilidades]
    num_vars = len(nombres)
    
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    valores += valores[:1]
    angles += angles[:1]

    # Ajustar tamaño del grafico
    fig, ax = plt.subplots(figsize=(4.5, 4.5), subplot_kw=dict(polar=True))
    
    ax.fill(angles, valores, color='#1f77b4', alpha=0.3)
    ax.plot(angles, valores, color='#1f77b4', linewidth=2)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(nombres, fontsize=8)
    ax.set_ylim(0, 10)
    
    plt.tight_layout()
    st.pyplot(fig)

# --- Interfaz única ---
st.set_page_config(page_title="Pro-Recruiter AI", layout="wide")
st.title("📊 Sistema Inteligente de Análisis de Candidatos")

job_desc = st.text_area("Descripción del Puesto:")
files = st.file_uploader("Subir CVs", accept_multiple_files=True, type="pdf")


if st.button("Analizar y Filtrar") and job_desc and files:
    for f in files:
        with fitz.open(stream=f.read(), filetype="pdf") as doc:
            texto = doc[0].get_text()
            resultado = analizar_candidato(texto, job_desc)
            
            es_potencial = resultado.get("es_potencial", False)
            tipo = "✅ Potencial" if es_potencial else "❌ No Apto"
            
            with st.expander(f"{tipo}: {f.name} (Score: {resultado.get('puntuacion')})", expanded=True):
                col_texto, col_grafico = st.columns([1, 1.5]) 
                
                with col_texto:
                    st.write("**Análisis:**", resultado.get("analisis"))
                    
                    f.seek(0)
                    pdf_data = base64.b64encode(f.read()).decode("utf-8")
                    pdf_display = f'<a href="data:application/pdf;base64,{pdf_data}" target="_blank">📄 Ver CV Original (PDF)</a>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                    # ----------------------------------------------------
                
                with col_grafico:
                    if es_potencial:
                        crear_grafico_habilidades(resultado.get("habilidades"))
                    else:
                        st.info("No hay gráfico de habilidades disponible.")