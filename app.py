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
            objetivo = st.radio("2.1. ¿Cuál es tu objetivo principal al invertir?", 
                              ["Preservar el capital (riesgo bajo)", "Obtener rentabilidad ligeramente por encima del tipo de interés de mercado (riesgo bajo-medio)", "Obtener rentabilidad significativamente por encima del tipo de interés de mercado (riesgo medio-alto)", "Obtener la máxima rentabilidad posible (riesgo muy alto)"], 
                              index=None)
            horizonte = st.radio("2.2. ¿Cuál es tu horizonte temporal de inversión?", 
                                ["Menos de 1 año", "Entre 1 y 3 años", "Entre 3 y 5 años", "Más de 5 años"],
                                index=None)
            
            formación = st.radio("2.3. ¿Cuál es tu nivel de formación?", 
                                ["Educación no universitaria", "Educación universitaria o superior", "Educación universitaria o superior relacionada con los mercados financieros o la economía"], 

                                index=None)

            cargo = st.radio("2.4. ¿Trabajas o has trabajado en contacto directo con instrumentos o mercados financieros?", 
                                ["Nunca","Menos de 1 año", "Entre 1 y 3 años", "Más de 3 años"],  
                                index=None)
            
            conocimiento = st.radio("2.5. ¿Que conocimiento tienes sobre los mercados financieros?", 
                                ["No estoy familiarizado", "Entiendo los conceptos básicos como la inflación, el tipo de interés", "Entiendo conceptos financieros complejos como volatilidad, riesgo de liquidez, convertibilidad en acciones"],  
                                index=None)
            
            productos = st.multiselect("3.1. ¿Qué productos financieros has utilizado?", 
                                ["Acciones Cotizadas de Renta Variable o Fondos Cotizados (ETFs) o IICs (Fondos o SICAVS)", "Renta Fija Privada simple o Cédulas hipotecarias", "Rentas vitalicias o seguros de vida ahorro garantizados", "Instrumentos de Mercado Monetario (letras, pagarés) o Bonos y Obligaciones del Estado", "Derivados (futuros, opciones)", "Criptomonedas"])
            productos_str = ", ".join(productos) if productos else ""

            volatilidad = st.radio("3.2. ¿Ante una pérdida de valor inesperada de menos de un 10% como se comportaría?", 
                                 ["Mantendría la inversión", "Mantendría la inversión pero haría mas seguimiento", "Vendería una parte de la inversión", "Vendería toda la inversión"], 
                                 index=None)
            corto_plazo = st.radio("3.3. ¿Qué porcentaje de pérdidas está dispuesto a soportar en el plazo de un año?", 
                                   ["0%", "Hasta un 5%", "Hasta un 10%", "Hasta un 25%", "Más del 25%"],
                                  index=None)

            patrimonio = st.radio("4.1. ¿Qué porcentaje de su patrimonio tiene invertido en instrumentos financieros?", 
                                ["Menos del 25%", "Entre el 25% y el 50%", "Más del 50%"], 
                                index=None)
            
            necesidad = st.radio("4.2. ¿Qué porcentaje de sus inversiones cree que va a necesitar en un periodo de un año?", 
                                ["Menos del 25%", "Entre el 25% y el 50%", "Más del 50%"], 
                                index=None)
            
            edad = st.radio("4.3. ¿A que rango de edad pertenece?", 
                                ["18-35 años", "36-50 años", "51-65 años", "Más de 65 años"], 
                                index=None)



            sostenibilidad = st.radio("6.1. ¿Te interesa que tus inversiones consideren criterios de sostenibilidad?", 
                                     ["Sí", "No"], 
                                     index=None)
            
            fondo_clima = st.radio("6.2. ¿Cual de los siguientes aspectos te interesan que se tengan en cuenta?", 
                                       ["Relacionadas con el clima y el medioambiente", "Relacionadas con asuntos sociales y de gobernanza", "Ambas","Ninguna"], 
                                       index=None)
            porcentaje = st.radio("6.3. ¿Quieres incluir en tu cartera inversiones ESG?", 
                                           ["Si, al menos un 5%", "Si, al menos un 15%", "Si, al menos un 35%", "No"], 
                                           index=None)
           

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
                        objetivo or "", horizonte or "", formación or "", cargo or "", conocimiento or "",
                        productos  or "", productos_str  or "", volatilidad  or "", corto_plazo  or "",
                        patrimonio  or "", necesidad  or "", edad  or "", sostenibilidad or "", fondo_clima or "", porcentaje or ""
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
