📊 Pro-Recruiter AI: Filtro Inteligente de Talento
Pro-Recruiter AI es una solución automatizada diseñada para optimizar los procesos de reclutamiento técnico. A través de la Inteligencia Artificial, este sistema analiza y filtra currículums (CVs) de manera eficiente, comparándolos con las necesidades reales de una descripción de puesto, permitiendo a los reclutadores tomar decisiones basadas en datos.

🛠 Tecnologías Utilizadas
Python: Lenguaje principal para la lógica de backend y procesamiento.

Streamlit: Framework de alto nivel para crear la interfaz web de forma rápida y profesional.

Groq API (Llama-3.3-70b-versatile): Motor de inferencia de IA que permite un análisis semántico ultrarrápido.

PyMuPDF (fitz): Librería especializada para la extracción precisa de texto desde documentos PDF.

Matplotlib & NumPy: Herramientas de ciencia de datos utilizadas para generar gráficos de radar (visualización de habilidades).

🧠 ¿Cómo funciona el programa?
El flujo de trabajo está diseñado para ser directo y eficiente:

Carga de Candidatos: El usuario sube uno o múltiples CVs en formato PDF y pega la descripción del puesto deseado.

Extracción de Información: El sistema utiliza PyMuPDF para convertir los archivos PDF en texto plano legible para la IA.

Análisis Comparativo (IA): El motor de Groq actúa como un reclutador experto, comparando las habilidades detectadas en el CV contra los requisitos de la descripción.

Clasificación y Scoring: El sistema devuelve una puntuación (0-100) y clasifica automáticamente al candidato como "Potencial" o "No Apto" según su compatibilidad.

Visualización y Verificación:

Los candidatos potenciales muestran un gráfico de radar con sus fortalezas técnicas.

Se proporciona una opción de Previsualización de PDF para que el reclutador pueda verificar el documento original al instante.

Desarrollado por: Elian Montero | Computing Technician & Backend Developer
