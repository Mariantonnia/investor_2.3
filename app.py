import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Perfil del Inversor", layout="centered")

# Título principal
st.title("Evaluación del Perfil del Inversor")
st.markdown("Por favor, complete el siguiente formulario para ayudarnos a conocer mejor su perfil de inversión.")

# Formulario principal
with st.form("formulario_final"):

    st.subheader("1. Conocimiento y Experiencia del Inversor")
    tipos_productos = st.text_input("¿Con qué tipos de productos financieros está familiarizado?")
    experiencia_inversion = st.radio("¿Cuánto tiempo lleva invirtiendo?", ["Nunca", "Menos de 1 año", "1 a 5 años", "Más de 5 años"])
    comprension_riesgos = st.radio("¿Comprende los riesgos inherentes a la inversión en acciones?", ["Sí", "No", "No estoy seguro"])

    st.subheader("2. Situación Financiera del Inversor")
    ingresos = st.radio("¿Cuál es su nivel de ingresos anuales?", ["<20.000€", "20.000€ - 50.000€", "50.000€ - 100.000€", ">100.000€"])
    activos = st.text_input("¿Cuáles son sus activos totales (efectivo, valores, inmuebles, inversiones)?")
    tolerancia_perdidas = st.radio("¿Qué porcentaje de su inversión inicial podría perder sin afectar significativamente su situación financiera?", ["<5%", "5-10%", "10-20%", ">20%"])
    liquidez = st.radio("¿Tiene necesidades de liquidez a corto o medio plazo?", ["Sí", "No"])
    edad = st.number_input("¿Cuál es su edad?", min_value=18, max_value=100)
    dependientes = st.number_input("¿Cuántas personas dependen económicamente de usted?", min_value=0, max_value=10)
    estado_laboral = st.radio("¿Cuál es su situación laboral?", ["Empleado", "Desempleado", "Autónomo", "Jubilado", "Estudiante", "Otro"])

    st.subheader("3. Objetivos de Inversión")
    objetivo_inversion = st.radio("¿Cuál es su principal objetivo de inversión?", ["Crecimiento de capital", "Obtención de ingresos", "Preservación del capital", "Especulación"])
    horizonte_temporal = st.radio("¿Cuál es su horizonte temporal de inversión?", ["Menos de 1 año", "1 a 3 años", "3 a 5 años", "Más de 5 años"])
    rentabilidad_esperada = st.text_input("¿Qué rentabilidad esperada tiene en mente para sus inversiones?")
    nivel_riesgo = st.radio("¿Qué nivel de riesgo está dispuesto a asumir?", ["Bajo", "Moderado", "Alto", "Muy alto"])

    st.subheader("4. Tolerancia al Riesgo (Psicológica)")
    reaccion_perdidas = st.radio("¿Cómo reaccionaría si su inversión perdiera un 20% en un corto período?", ["Vendería todo", "Esperaría", "Comprar más", "Consultar asesor"])
    decisiones_pasadas = st.text_input("Describa una decisión financiera difícil que haya tomado en el pasado:")
    confianza_autogestion = st.radio("¿Qué tan cómodo se siente gestionando sus propias inversiones?", ["Muy incómodo", "Incómodo", "Neutral", "Cómodo", "Muy cómodo"])

    st.subheader("5. Aspectos Éticos y de Sostenibilidad")
    interes_inversion_impacto = st.radio("¿Está interesado en inversiones con impacto social o ambiental positivo?", ["Sí", "No", "Indiferente"])
    excluir_industrias = st.multiselect("¿Qué industrias prefiere evitar por razones éticas?", ["Armamento", "Tabaco", "Petróleo", "Juegos de azar", "Ninguna"])
    importancia_sostenibilidad = st.radio("¿Qué tan importante es para usted que las empresas en las que invierte cumplan con criterios ESG?", ["Nada importante", "Poco importante", "Neutral", "Importante", "Muy importante"])

    # Botón de envío
    submitted = st.form_submit_button("Enviar")

    if submitted:
        st.success("Formulario enviado correctamente.")

        # Mostrar resumen
        st.subheader("Resumen de Respuestas")
        st.write("**Tipos de productos:**", tipos_productos)
        st.write("**Experiencia en inversión:**", experiencia_inversion)
        st.write("**Comprensión de riesgos:**", comprension_riesgos)
        st.write("**Ingresos anuales:**", ingresos)
        st.write("**Activos totales:**", activos)
        st.write("**Tolerancia a pérdidas:**", tolerancia_perdidas)
        st.write("**Necesidad de liquidez:**", liquidez)
        st.write("**Edad:**", edad)
        st.write("**Dependientes:**", dependientes)
        st.write("**Estado laboral:**", estado_laboral)
        st.write("**Objetivo de inversión:**", objetivo_inversion)
        st.write("**Horizonte temporal:**", horizonte_temporal)
        st.write("**Rentabilidad esperada:**", rentabilidad_esperada)
        st.write("**Nivel de riesgo:**", nivel_riesgo)
        st.write("**Reacción a pérdidas:**", reaccion_perdidas)
        st.write("**Decisión difícil pasada:**", decisiones_pasadas)
        st.write("**Confianza en autogestión:**", confianza_autogestion)
        st.write("**Interés en inversiones con impacto:**", interes_inversion_impacto)
        st.write("**Industrias excluidas:**", excluir_industrias)
        st.write("**Importancia de sostenibilidad:**", importancia_sostenibilidad)
