import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from langchain import LLMChain, PromptTemplate
from langchain_groq import ChatGroq
import os
import re
import json
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# Cargar variables de entorno
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Configurar LLM
llm = ChatGroq(
    model="gemma2-9b-it",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Preguntas iniciales al inversor
preguntas_inversor = [
    "¿Cuál es tu objetivo principal al invertir?",
    "¿Cuál es tu horizonte temporal de inversión?",
    "¿Tienes experiencia previa invirtiendo en activos de mayor riesgo como acciones, criptomonedas o fondos alternativos?",
    "¿Estás dispuesto a sacrificar parte de la rentabilidad potencial a cambio de un impacto social o ambiental positivo?",
    "¿Qué opinas sobre el cambio climático?"
]

# Noticias para análisis
noticias = [
    "Repsol, entre las 50 empresas que más responsabilidad histórica tienen en el calentamiento global",
    "Amancio Ortega crea un fondo de 100 millones de euros para los afectados de la dana",
    "Freshly Cosmetics despide a 52 empleados en Reus, el 18% de la plantilla",
    "Wall Street y los mercados globales caen ante la incertidumbre por la guerra comercial y el temor a una recesión",
    "El mercado de criptomonedas se desploma: Bitcoin cae a 80.000 dólares, las altcoins se hunden en medio de una frenética liquidación"
]

# Plantillas de LLM
plantilla_evaluacion = """
Evalúa si esta respuesta del usuario es suficientemente detallada para un análisis ESG. 
Criterios:
- Claridad de la opinión
- Especificidad respecto a la noticia
- Mención de aspectos ESG (ambiental, social, gobernanza o riesgo)
- Identificación de preocupaciones o riesgos

Respuesta del usuario: {respuesta}

Si es vaga o superficial, responde "False".
Si contiene opinión sustancial y analizable, responde "True".

Solo responde "True" o "False".
"""
prompt_evaluacion = PromptTemplate(template=plantilla_evaluacion, input_variables=["respuesta"])
cadena_evaluacion = LLMChain(llm=llm, prompt=prompt_evaluacion)

plantilla_reaccion = """
Reacción del inversor: {reaccion}
Genera ÚNICAMENTE una pregunta de seguimiento enfocada en profundizar en su opinión.
Ejemplo:  
"¿Consideras que la existencia de mecanismos robustos de control interno y transparencia podría mitigar tu preocupación por la gobernanza corporativa en esta empresa?"
"""
prompt_reaccion = PromptTemplate(template=plantilla_reaccion, input_variables=["reaccion"])
cadena_reaccion = LLMChain(llm=llm, prompt=prompt_reaccion)

plantilla_perfil = """
Análisis de respuestas: {analisis}
Genera un perfil detallado del inversor basado en sus respuestas, enfocándote en los pilares ESG (Ambiental, Social y Gobernanza) y su aversión al riesgo. 
Asigna una puntuación de 0 a 100 para cada pilar ESG y para el riesgo, donde 0 indica ninguna preocupación y 100 máxima preocupación o aversión.
Devuelve las 4 puntuaciones en formato: Ambiental: [puntuación], Social: [puntuación], Gobernanza: [puntuación], Riesgo: [puntuación]
"""
prompt_perfil = PromptTemplate(template=plantilla_perfil, input_variables=["analisis"])
cadena_perfil = LLMChain(llm=llm, prompt=prompt_perfil)

# Función para procesar respuestas válidas a las noticias
def procesar_respuesta_valida(user_input):
    pregunta_seguimiento = cadena_reaccion.run(reaccion=user_input).strip()
    if st.session_state.contador_preguntas == 0:
        with st.chat_message("bot", avatar="🤖"):
            st.write(pregunta_seguimiento)
        st.session_state.historial.append({"tipo": "bot", "contenido": pregunta_seguimiento})
        st.session_state.pregunta_pendiente = True
        st.session_state.contador_preguntas += 1
    else:
        st.session_state.reacciones.append(user_input)
        st.session_state.contador += 1
        st.session_state.mostrada_noticia = False
        st.session_state.contador_preguntas = 0
        st.session_state.pregunta_pendiente = False
        st.rerun()

# Inicializar estados
if "historial" not in st.session_state:
    st.session_state.historial = []
    st.session_state.contador = 0
    st.session_state.reacciones = []
    st.session_state.mostrada_noticia = False
    st.session_state.contador_preguntas = 0
    st.session_state.pregunta_general_idx = 0
    st.session_state.pregunta_pendiente = False
    st.session_state.cuestionario_enviado = False
    st.session_state.perfil_valores = {}

# Interfaz
st.title("Chatbot de Análisis de Inversor ESG")
st.markdown("""
**Primero interactuarás con un chatbot para evaluar tu perfil ESG.** 
**Al final, completarás un test tradicional de perfilado.**
""")

# Mostrar historial
for mensaje in st.session_state.historial:
    with st.chat_message(mensaje["tipo"], avatar="🤖" if mensaje["tipo"] == "bot" else None):
        st.write(mensaje["contenido"])

# Preguntas iniciales al inversor
if st.session_state.pregunta_general_idx < len(preguntas_inversor):
    pregunta_actual = preguntas_inversor[st.session_state.pregunta_general_idx]
    if not any(p["contenido"] == pregunta_actual for p in st.session_state.historial if p["tipo"] == "bot"):
        st.session_state.historial.append({"tipo": "bot", "contenido": pregunta_actual})
        with st.chat_message("bot", avatar="🤖"):
            st.write(pregunta_actual)

    user_input = st.chat_input("Escribe tu respuesta aquí...")
    if user_input:
        st.session_state.historial.append({"tipo": "user", "contenido": user_input})
        st.session_state.reacciones.append(user_input)
        st.session_state.pregunta_general_idx += 1
        st.rerun()

# Noticias ESG
elif st.session_state.contador < len(noticias):
    if not st.session_state.mostrada_noticia:
        noticia = noticias[st.session_state.contador]
        texto_noticia = f"¿Qué opinas sobre esta noticia? {noticia}"
        st.session_state.historial.append({"tipo": "bot", "contenido": texto_noticia})
        with st.chat_message("bot", avatar="🤖"):
            st.write(texto_noticia)
        st.session_state.mostrada_noticia = True

    user_input = st.chat_input("Escribe tu respuesta aquí...")
    if user_input:
        st.session_state.historial.append({"tipo": "user", "contenido": user_input})
        if st.session_state.pregunta_pendiente:
            st.session_state.reacciones.append(user_input)
            st.session_state.contador += 1
            st.session_state.mostrada_noticia = False
            st.session_state.contador_preguntas = 0
            st.session_state.pregunta_pendiente = False
            st.rerun()
        else:
            evaluacion = cadena_evaluacion.run(respuesta=user_input).strip().lower()
            if evaluacion == "false":
                pregunta_ampliacion = cadena_reaccion.run(reaccion=user_input).strip()
                with st.chat_message("bot", avatar="🤖"):
                    st.write(pregunta_ampliacion)
                st.session_state.historial.append({"tipo": "bot", "contenido": pregunta_ampliacion})
                st.session_state.pregunta_pendiente = True
            else:
                procesar_respuesta_valida(user_input)

# Perfil final y test tradicional
else:
    # Generar perfil (si no está ya generado)
    if not st.session_state.perfil_valores:
        analisis_total = "\n".join(st.session_state.reacciones)
        perfil = cadena_perfil.run(analisis=analisis_total)

        puntuaciones = {
            "Ambiental": int(re.search(r"Ambiental: (\d+)", perfil).group(1)),
            "Social": int(re.search(r"Social: (\d+)", perfil).group(1)),
            "Gobernanza": int(re.search(r"Gobernanza: (\d+)", perfil).group(1)),
            "Riesgo": int(re.search(r"Riesgo: (\d+)", perfil).group(1)),
        }
        st.session_state.perfil_valores = puntuaciones
    # Mostrar perfil y gráfico siempre
    with st.chat_message("bot", avatar="🤖"):
        st.write(f"**Perfil del inversor:** Ambiental: {st.session_state.perfil_valores['Ambiental']}, " +
                f"Social: {st.session_state.perfil_valores['Social']}, " +
                f"Gobernanza: {st.session_state.perfil_valores['Gobernanza']}, " +
                f"Riesgo: {st.session_state.perfil_valores['Riesgo']}")

    fig, ax = plt.subplots()
    ax.bar(st.session_state.perfil_valores.keys(), st.session_state.perfil_valores.values(), color="skyblue")
    ax.set_ylabel("Puntuación (0-100)")
    ax.set_title("Perfil del Inversor")
    st.pyplot(fig)

    # Mostrar cuestionario si no se ha enviado
    if not st.session_state.cuestionario_enviado:
        st.header("Cuestionario Final de Perfilado")

        with st.form("formulario_final"):

    st.subheader("1. Conocimiento y Experiencia del Inversor")
    productos_familiar = st.text_input("¿Con qué tipos de productos financieros (acciones, bonos, derivados, fondos) está familiarizado?")
    experiencia_tiempo = st.radio("¿Cuánto tiempo lleva invirtiendo?", 
                                  ["Nunca", "Menos de 1 año", "1-3 años", "Más de 3 años"], index=None)
    frecuencia_operaciones = st.radio("¿Con qué frecuencia realiza operaciones de inversión?", 
                                      ["Nunca", "Ocasionalmente", "Regularmente"], index=None)
    comprende_riesgos = st.text_input("¿Comprende los riesgos inherentes a la inversión en algún producto financiero? (especificar)")

    st.subheader("2. Situación Financiera del Inversor")
    ingresos = st.selectbox("¿Cuál es su nivel de ingresos anuales?", 
                            ["<20.000€", "20.000€ - 50.000€", "50.000€ - 100.000€", ">100.000€"])
    activos = st.text_input("¿Cuáles son sus activos totales (efectivo, valores, inmuebles, etc.) y pasivos?")
    tolerancia_perdidas = st.radio("¿Qué porcentaje de su inversión inicial estaría dispuesto a perder sin afectar su situación financiera?", 
                                   ["<5%", "5-10%", "10-20%", ">20%"], index=None)
    necesidades_liquidez = st.radio("¿Tiene necesidades de liquidez a corto o medio plazo que puedan afectar sus inversiones?", 
                                    ["Sí", "No"], index=None)
    estado_civil = st.selectbox("Estado civil:", ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a"])
    dependientes = st.number_input("Número de dependientes económicos:", min_value=0, step=1)
    edad = st.number_input("Edad:", min_value=18, max_value=100)
    situacion_laboral = st.selectbox("Situación laboral:", ["Empleado/a", "Autónomo/a", "Desempleado/a", "Jubilado/a", "Otro"])

    st.subheader("3. Objetivos de Inversión y Tolerancia al Riesgo")
    proposito = st.selectbox("¿Cuál es el propósito principal de esta inversión?", 
                             ["Preservación del capital", "Generación de ingresos estables", "Crecimiento a largo plazo", "Crecimiento agresivo"])
    horizonte_inversion = st.selectbox("¿Cuál es su horizonte de inversión?", 
                                       ["<1 año", "1-2 años", "3-4 años", "5-10 años", ">10 años"])
    apetito_riesgo = st.radio("¿Cómo describiría su apetito por el riesgo?", 
                              ["No quiero asumir riesgo", "Acepto riesgo moderado", "Busco altos rendimientos a pesar del riesgo"], index=None)
    reaccion_volatilidad = st.radio("Si su cartera cayera un 25%, ¿cómo reaccionaría?", 
                                    ["Vendería todo", "Esperaría a que se recupere", "Invertiría más"], index=None)
    comodidad_fluctuacion = st.radio("Si tuviera 100.000€, ¿con qué fluctuación se sentiría más cómodo?", 
                                     ["+/-5%", "+/-10%", "+/-20%", "Más del +/-20%"], index=None)

    st.subheader("4. Preferencias de Sostenibilidad")
    interes_sostenibilidad = st.radio("¿Tiene alguna preferencia de sostenibilidad para sus inversiones?", 
                                      ["Sí", "No"], index=None)

    if interes_sostenibilidad == "Sí":
        proporción_taxonomía = st.selectbox("¿Qué proporción mínima desea invertir en actividades medioambientalmente sostenibles (Taxonomía UE)?", 
                                            ["20%", "25%", "50%", "Más del 50%"])
        proporción_sfdr = st.selectbox("¿Qué proporción mínima desea invertir en inversiones sostenibles según el SFDR?", 
                                       ["20%", "25%", "50%", "Más del 50%"])
        considera_PIA = st.radio("¿Desea considerar los principales impactos adversos (PIA)?", ["Sí", "No"], index=None)
        if considera_PIA == "Sí":
            elementos_PIA = st.text_area("¿Qué elementos desea considerar (emisiones, derechos humanos, residuos, etc.)?")
        exclusiones = st.text_area("¿Tiene alguna preferencia de exclusión (combustibles fósiles, tabaco, armas, etc.)?")
        preferencia_E_S_G = st.radio("¿Prefiere priorizar criterios Ambientales (E), Sociales (S) o de Gobernanza (G)?", 
                                     ["Ambientales", "Sociales", "Gobernanza", "Todos por igual"], index=None)
        concesiones = st.text_area("¿Está dispuesto a aceptar concesiones si una inversión sostenible también genera impacto negativo en otros aspectos?")

    enviar = st.form_submit_button("Enviar respuestas")

            if enviar:
                try:
                    creds_json_str = st.secrets["gcp_service_account"]
                    creds_json = json.loads(creds_json_str)
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
                    client = gspread.authorize(creds)
                    sheet = client.open('BBDD_RESPUESTAS').sheet1

                    fila = st.session_state.reacciones + [
                        str(st.session_state.perfil_valores.get("Ambiental", "")),
                        str(st.session_state.perfil_valores.get("Social", "")),
                        str(st.session_state.perfil_valores.get("Gobernanza", "")),
                        str(st.session_state.perfil_valores.get("Riesgo", "")),
                        objetivo or "", horizonte or "", productos_str, volatilidad or "", largo_plazo or "",
                        frecuencia or "", experiencia or "", reaccion_20 or "", combinacion or "",
                        sostenibilidad or "", fondo_clima or "", importancia or ""
                    ]

                    sheet.append_row(fila)
                    st.success("Respuestas enviadas y guardadas exitosamente")
                    st.session_state.cuestionario_enviado = True
                    st.rerun()  # Refrescar para ocultar el formulario
                except Exception as e:
                    st.error(f"❌ Error al guardar datos: {str(e)}")

    # Mostrar mensaje final si el cuestionario fue enviado
    if st.session_state.cuestionario_enviado:
        st.markdown("### ¡Gracias por completar tu perfil de inversor!")
        st.balloons()
