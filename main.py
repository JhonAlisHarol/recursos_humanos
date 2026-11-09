import streamlit as st
import pandas as pd
import glob
import base64
import time
from datetime import datetime
import pytz
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS NEÓN + VIDEO LOCAL DE FONDO ---
st.set_page_config(
    page_title="CON - Recursos Humanos",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Búsqueda automática del archivo de video local en la carpeta
video_base64 = ""
archivos_video = (
    glob.glob("*VIDEO*.mp4") + glob.glob("*video*.mp4") + glob.glob("*.mp4")
)

if archivos_video:
    try:
        with open(archivos_video[0], "rb") as f:
            video_base64 = base64.b64encode(f.read()).decode()
    except Exception as e:
        print(f"Error cargando video: {e}")

# Estilos CSS avanzados para el fondo de video local y efectos neón corporativos
st.markdown(
    f"""
    <style>
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Fondo de video fijo a pantalla completa */
    .video-background {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -99999;
        overflow: hidden;
        pointer-events: none;
    }}
    .video-background video {{
        width: 100vw;
        height: 100vh;
        object-fit: cover;
    }}

    /* Transparencia total en contenedores principales de Streamlit */
    .stApp, .block-container, [data-testid="stVerticalBlock"] {{
        background: transparent !important;
    }}

    /* Paneles con efecto Neón */
    [data-testid="stSidebar"] {{
        background-color: rgba(10, 15, 25, 0.85) !important;
        border-right: 2px solid #00d4ff !important;
        box-shadow: 5px 0 20px rgba(0, 212, 255, 0.4);
    }}

    div[data-testid="stForm"], .neon-card {{
        background-color: rgba(10, 15, 25, 0.85) !important;
        border: 2px solid #00d4ff !important;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 0 25px rgba(0, 212, 255, 0.5);
    }}

    /* Estilo para las Pestañas (Tabs) */
    div[data-testid="stTabs"] button {{
        color: #ffffff !important;
        font-weight: bold;
        font-size: 16px;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        border-bottom-color: #00d4ff !important;
        background-color: rgba(0, 212, 255, 0.15) !important;
        color: #00d4ff !important;
        text-shadow: 0 0 8px rgba(0, 212, 255, 0.8);
    }}

    /* Estilo para Tablas */
    table {{
        width: 100%;
        color: white !important;
        background-color: rgba(10, 15, 25, 0.7);
        border-collapse: collapse;
    }}
    th, td {{
        border: 1px solid #00d4ff !important;
        padding: 8px;
        text-align: center;
    }}
    th {{
        background-color: rgba(0, 212, 255, 0.2);
        color: #00d4ff !important;
    }}

    /* Efecto Neón en Textos y Títulos */
    h1, h2, h3, label, p, .neon-text {{
        color: #ffffff !important;
        text-shadow: 0 0 8px rgba(0, 212, 255, 0.8), 0 0 20px rgba(0, 212, 255, 0.4);
    }}

    .author {{
        font-size: 12px;
        color: #00ffff !important;
        font-weight: bold;
        letter-spacing: 2px;
        text-shadow: 0 0 10px #00ffff;
    }}

    /* Estilo Neón para Botones */
    div.stButton > button {{
        background-color: rgba(10, 15, 25, 0.9) !important;
        color: white !important;
        border: 2px solid #00d4ff !important;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        transition: 0.3s ease;
    }}
    div.stButton > button:hover {{
        background-color: #00d4ff !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #00d4ff;
    }}
    div.stButton > button p {{
        color: white !important;
        font-weight: bold;
    }}
    div.stButton > button:hover p {{
        color: black !important;
    }}
    </style>

    <div class="video-background">
        <video autoplay loop muted playsinline>
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        </video>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def conectar_google_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    client = gspread.authorize(creds)
    return client

# ID del nuevo documento Google Sheet "Plan_Recojo_CON"
ID_HOJA = "10RXYbyOVD8UVwCDWv3btpj9ddLv5cacJRCAKes"

# --- 2. ESTADOS DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "modo_pantalla" not in st.session_state:
    st.session_state.modo_pantalla = "NUEVO REGISTRO"

# --- 3. PANTALLA DE LOGIN CON ESTILO NEÓN ---
def pantalla_login():
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1 style='color: #00d4ff; text-shadow: 0 0 15px #00d4ff; margin-bottom: 0px;'>🔐 RECURSOS HUMANOS - C.O.N</h1>
            <p style='color: #00d4ff; font-size: 16px; font-style: italic; margin-top: 5px;'>Desarrollado por: CABO 1RO ELMER RODRIGUEZ</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        usuarios_permitidos = {
            "ADMINISTRADOR": "CONC505",
            "LORENZO BOWEN": "10924",
            "MIRNA RIVERA": "20146",
            "ALISJHON": "199432",
            "ALBERTO AYALA": "24561",
            "DANILO SMITH": "49431",
            "YANILKA RODRIGUEZ": "142012",
        }

        with st.form("login_form"):
            user = st.text_input("👤 Usuario institucional")
            password = st.text_input("🔑 Contraseña", type="password")
            
            submitted = st.form_submit_button("Iniciar Sesión", use_container_width=True)

            if submitted:
                if user in usuarios_permitidos and usuarios_permitidos[user] == password:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = user
                    st.success(f"¡Bienvenido, {user}!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")

# --- 4. APLICACIÓN PRINCIPAL ---
if not st.session_state.autenticado:
    pantalla_login()
else:
    st.markdown(
        '<p class="author">CENTRO DE OPERACIÓN NACIONAL - GESTIÓN DE PERSONAL</p>',
        unsafe_allow_html=True,
    )

    # Listas maestras
    lista_rangos = [
        "SELECCIONAR", "COMISIONADO", "SUBCOMISIONADO", "MAYOR", "CAPITÁN",
        "TENIENTE", "SUBTENIENTE", "SARGENTO 1º", "SARGENTO 2º", "CABO 1º",
        "CABO 2º", "AGENTE", "MNJ",
    ]
    lista_estamentos = ["SELECCIONAR", "P.N", "SENAFRONT", "SENAN", "MINSEG", "MNJ"]
    lista_departamentos = [
        "SELECCIONAR", "DIRECCION", "SUPERVISORA ADM", "PLANEAMIENTO",
        "COOR. TECNOLOGICO", "OPERACIONES", "ESTADISTICA", "RECURSOS HUMANOS",
    ]
    lista_turnos = ["SELECCIONAR", "5X2", "24X24", "ROTATIVO", "ADMINISTRATIVO"]
    lista_sangre = ["SELECCIONAR", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    lista_provincias = [
        "SELECCIONAR", "PANAMÁ", "PANAMÁ OESTE", "COLÓN", "CHIRIQUÍ", "VERAGUAS",
        "COCLÉ", "HERRERA", "LOS SANTOS", "BOCAS DEL TORO", "DARIÉN",
    ]
    lista_estados = ["SELECCIONAR", "ACTIVO", "INACTIVO", "VACACIONES", "PENSIONADO", "INCAPACITADO"]
    lista_estado_civil = ["SELECCIONAR", "SOLTERO/A", "CASADO/A", "DIVORCIADO/A", "VIUDO/A"]
    lista_si_no = ["NO", "SÍ"]
    lista_select_si_no = ["SELECCIONAR", " SÍ", "NO"]

    # --- BARRA LATERAL (SIDEBAR) ---
    with st.sidebar:
        st.write(
            f"👤 Usuario: **{st.session_state.get('usuario_actual', 'Admin')}**"
        )

        st.subheader("🕒 Hora Actual")
        import streamlit.components.v1 as components

        components.html(
            """
            <div id="reloj" style="font-size: 20px; font-weight: bold; color: #00ffff; text-shadow: 0 0 10px #00ffff;"></div>
            <script>
                function actualizarReloj() {
                    const ahora = new Date();
                    const opciones = { timeZone: 'America/Panama', hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' };
                    document.getElementById('reloj').innerText = ahora.toLocaleTimeString('es-PA', opciones);
                }
                setInterval(actualizarReloj, 1000);
                actualizarReloj();
            </script>
            """,
            height=35,
        )

        st.divider()
        st.subheader("Módulos de Operación")

        if st.button("➕ Registro Individual", use_container_width=True):
            st.session_state.modo_pantalla = "NUEVO REGISTRO"
            st.rerun()

        if st.button("📂 Carga Masiva (Plan de Recojo)", use_container_width=True):
            st.session_state.modo_pantalla = "CARGA_MASIVA"
            st.rerun()

        st.divider()
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # ==========================================
    # OPCIÓN 1: NUEVO REGISTRO INDIVIDUAL
    # ==========================================
    if st.session_state.modo_pantalla == "NUEVO REGISTRO":
        st.markdown(
            "<h1 style='color: #00d4ff; text-shadow: 0 0 12px #00d4ff;'>➕ NUEVO REGISTRO DE PERSONAL</h1>",
            unsafe_allow_html=True,
        )

        with st.form("form_nuevo_registro_excel", clear_on_submit=False):
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 1. DATOS PERSONALES", "📍 2. FUNCIONES GENERALES", "⚡ 3. OPERATIVIDAD", "🏡 4. RESIDENCIAL / ACADÉMICO", "🎽 5. TALLAS"
            ])

            with tab1:
                st.markdown("<h3 style='color: #00d4ff; margin-bottom: 20px;'>Información Personal</h3>", unsafe_allow_html=True)
                c1, c2, c3, c4, c5 = st.columns(5)
                rango = c1.selectbox("RANGO", lista_rangos)
                posic = c2.text_input("POSIC")
                placa_metalica = c3.text_input("Nº PLACA METÁLICA")
                nombre = c4.text_input("NOMBRE")
                apellido = c5.text_input("APELLIDO")

                c6, c7, c8, c9, c10 = st.columns(5)
                cedula = c6.text_input("Nº CÉDULA")
                fecha_naci = c7.date_input("FECHA DE NACIMIENTO", min_value=datetime(1950, 1, 1), max_value=datetime.now(pytz.timezone('America/Panama')))
                edad = c8.number_input("EDAD", min_value=0, step=1)
                genero = c9.selectbox("GÉNERO", ["SELECCIONAR", "M", "F"])
                telefono_personal = c10.text_input("TELÉFONO PERSONAL")

                c11, c12, c13, c14, c15 = st.columns(5)
                estamento = c11.selectbox("ESTAMENTO", lista_estamentos)
                num_promocion = c12.text_input("Nº PROMOCIÓN")
                descripcion_promo = c13.text_input("DESCRIPCIÓN PROMOCIÓN")
                fecha_ingreso = c14.date_input("FECHA DE INGRESO", min_value=datetime(1980, 1, 1), max_value=datetime.now(pytz.timezone('America/Panama')))
                anos_servicios = c15.number_input("AÑOS DE SERVICIO", min_value=0, step=1)

            with tab2:
                st.markdown("<h3 style='color: #00d4ff; margin-bottom: 20px;'>Funciones y Asignaciones</h3>", unsafe_allow_html=True)
                f1, f2, f3, f4, f5 = st.columns(5)
                res_ogd = f1.text_input("RES. OGD. ASIG. AL CENTRO")
                asig_trasl = f2.text_input("ASIG. TRASLADO")
                direc_depen = f3.text_input("DIREC, DEPEN O A. POLICIALES")
                asignado_centro = f4.text_input("ASIGNADO A (CENTRO)")
                u_centro_asignado = f5.text_input("U. DEL CENTRO ASIGNADO")

                f6, f7, f8, f9, f10 = st.columns(5)
                departamento = f6.selectbox("DEPARTAMENTO", lista_departamentos)
                turno = f7.selectbox("TURNO", lista_turnos)
                grupo = f8.text_input("GRUPO")
                funcion = f9.text_input("FUNCIÓN")
                estado_status = f10.selectbox("ESTADO O STATUS", lista_estados)

            with tab3:
                st.markdown("<h3 style='color: #00d4ff; margin-bottom: 20px;'>Tipo de Operatividad y Diagnóstico Médico</h3>", unsafe_allow_html=True)
                o1, o2, o3, o4, o5 = st.columns(5)
                operat_no_operat = o1.selectbox("ESTATUS OPERAT.", ["SELECCIONAR", "OPERATIVO", "NO OPERATIVO"])
                perm_temp = o2.selectbox("PERM./TEMP.", ["SELECCIONAR", "PERM", "TEMP"])
                condicion = o3.text_input("CONDICIÓN")
                apto_no_apto = o4.selectbox("APTO - NO APTO", ["SELECCIONAR", "APTO", "NO APTO"])
                nivel_salud = o5.text_input("NIVEL")

                o6, o7, o8, o9, o10 = st.columns(5)
                observacion = o6.text_input("OBSERVACIÓN")
                cert_buena_salud = o7.selectbox("CERT. BUENA SALUD ACT.", lista_select_si_no)
                fecha_diagnostico = o8.date_input("FECHA DIAGNÓSTICO")
                f_prox_evaluacion = o9.date_input("F. PROX. EVALUACIÓN")
                salud_ocupacional = o10.text_input("SALUD OCUPACIONAL")

                o11, _ = st.columns([1, 4])
                pensionado_opt = o11.selectbox("PENSIONADO", lista_si_no)

            with tab4:
                st.markdown("<h3 style='color: #00d4ff; margin-bottom: 20px;'>Información Residencial, Familiar y Académica</h3>", unsafe_allow_html=True)
                r1, r2, r3, r4, r5 = st.columns(5)
                provincia = r1.selectbox("PROVINCIA", lista_provincias)
                distrito = r2.text_input("DISTRITO")
                corregimiento = r3.text_input("CORREGIMIENTO")
                lugar = r4.text_input("LUGAR")
                tipo_sangre = r5.selectbox("TIPO DE SANGRE", lista_sangre)

                r6, r7, r8, r9, r10 = st.columns(5)
                nombre_familiar = r6.text_input("NOMBRE (EMERGENCIA)")
                parentesco = r7.text_input("PARENTESCO")
                telefono_familiar = r8.text_input("TELÉFONO (EMERGENCIA)")
                estado_civil = r9.selectbox("ESTADO CIVIL", lista_estado_civil)
                donante_sangre = r10.selectbox("DONANTE DE SANGRE", lista_si_no)

                r11, r12, r13, r14, r15 = st.columns(5)
                secundaria = r11.text_input("SECUNDARIA")
                universidad = r12.text_input("UNIVERSIDAD")
                hijos_m = r13.number_input("HIJOS M", min_value=0, step=1)
                hijas_f = r14.number_input("HIJAS F", min_value=0, step=1)
                total_hijos = r15.number_input("TOTAL DE HIJOS", min_value=0, step=1)

            with tab5:
                st.markdown("<h3 style='color: #00d4ff; margin-bottom: 20px;'>Tallas de Uniforme y Equipamiento</h3>", unsafe_allow_html=True)
                t1, t2, t3, t4, t5 = st.columns(5)
                talla_camisa = t1.text_input("CAMISA")
                talla_pantalon = t2.text_input("PANTALÓN")
                talla_sueter = t3.text_input("SUÉTER")
                talla_botas = t4.text_input("BOTAS")
                talla_zapatos = t5.text_input("ZAPATOS")

                t6, t7, t8 = st.columns([1, 1, 3])
                talla_quepi = t6.text_input("QUÉPI")
                talla_correa = t7.text_input("CORREA")

                st.markdown("<hr style='border:1px dashed #00d4ff; margin-top: 30px;'>", unsafe_allow_html=True)
                st.info("⚠️ Revise que la información de las 4 pestañas anteriores esté completa antes de guardar el registro oficial.")
                
                submitted_excel = st.form_submit_button("💾 Guardar Registro Oficial de Personal", use_container_width=True)

                if submitted_excel:
                    if not nombre or not apellido or not cedula or rango == "SELECCIONAR":
                        st.error("❌ Por favor complete los campos obligatorios principales de la Pestaña 1 (Rango, Nombre, Apellido y Cédula).")
                    else:
                        try:
                            tz = pytz.timezone('America/Panama')
                            timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                            usuario_reg = st.session_state.get("usuario_actual", "DESCONOCIDO")

                            # Se añade un string vacío "" al inicio para respetar la columna A ("Nº") de tu Google Sheet
                            nueva_fila = [
                                "", timestamp, usuario_reg, rango, posic, placa_metalica, nombre, apellido, cedula,
                                str(fecha_naci), str(edad), genero, telefono_personal, estamento, num_promocion, descripcion_promo,
                                str(fecha_ingreso), str(anos_servicios), res_ogd, asig_trasl, direc_depen, asignado_centro, u_centro_asignado,
                                departamento, turno, grupo, funcion, estado_status, operat_no_operat, perm_temp, condicion, apto_no_apto,
                                nivel_salud, observacion, cert_buena_salud, str(fecha_diagnostico), str(f_prox_evaluacion), salud_ocupacional,
                                pensionado_opt, provincia, distrito, corregimiento, lugar, tipo_sangre, nombre_familiar, parentesco,
                                telefono_familiar, estado_civil, donante_sangre, secundaria, universidad, str(hijos_m), str(hijas_f),
                                str(total_hijos), talla_camisa, talla_pantalon, talla_sueter, talla_botas, talla_zapatos, talla_quepi, talla_correa
                            ]

                            st.info("Conectando con la base de datos principal (Plan_Recojo_CON)...")
                            cliente_gs = conectar_google_sheets()
                            
                            # Nos conectamos a la pestaña "Plan de Recojo"
                            hoja_bd = cliente_gs.open_by_key(ID_HOJA).worksheet("Plan de Recojo")
                            hoja_bd.append_row(nueva_fila)

                            st.success(f"✔️ El elemento {rango} {nombre} {apellido} con cédula {cedula} ha sido registrado exitosamente.")
                        except Exception as e:
                            st.error(f"❌ Ocurrió un error al guardar en la base de datos: {e}")

    # ==========================================
    # OPCIÓN 2: CARGA MASIVA (PLAN DE RECOJO COMPLETO)
    # ==========================================
    elif st.session_state.modo_pantalla == "CARGA_MASIVA":
        st.markdown(
            "<h1 style='color: #00d4ff; text-shadow: 0 0 12px #00d4ff;'>📂 CARGA MASIVA - PLAN DE RECOJO</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p>Sube tu archivo Excel con el formato horizontal del Plan de Recojo. El sistema procesará e inyectará todas las unidades de una sola vez a la pestaña <b>Plan de Recojo</b>.</p>",
            unsafe_allow_html=True,
        )

        archivo_subido = st.file_uploader("Seleccione el archivo Excel (.xlsx) o CSV del Plan de Recojo", type=["csv", "xlsx"])

        if archivo_subido is not None:
            try:
                # Lectura de la carga masiva desde la fila de encabezados correcta (Fila 2 / índice 1)
                if archivo_subido.name.endswith('.csv'):
                    df_subido = pd.read_csv(archivo_subido, header=1)
                else:
                    df_subido = pd.read_excel(archivo_subido, header=1)

                st.success(f"✔️ Archivo leído con éxito. Se detectaron {len(df_subido)} registros para procesar.")
                
                st.markdown("### Vista Previa de los Datos:")
                st.dataframe(df_subido.head(), use_container_width=True)

                if st.button("🚀 Inyectar Plan de Recojo a Google Sheets", use_container_width=True):
                    with st.spinner("Subiendo registros masivamente a Google Sheets..."):
                        tz = pytz.timezone('America/Panama')
                        timestamp_actual = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                        usuario_reg = st.session_state.get("usuario_actual", "ADMINISTRADOR")

                        filas_a_insertar = []

                        for _, row in df_subido.iterrows():
                            # Mapeo exacto adaptado a las columnas de tu archivo Excel de carga masiva
                            fila_procesada = [
                                "", # Columna A (Nº - autoincremental en la hoja)
                                str(row.get("TIMESTAMP", timestamp_actual)),
                                str(row.get("USUARIO_REGISTRO", usuario_reg + " (Masivo)")),
                                str(row.get("RANGO", "")),
                                str(row.get("POSIC", "")),
                                str(row.get("Nº PLACA METALICA", "")),
                                str(row.get("NOMBRE", "")),
                                str(row.get("APELLIDO", "")),
                                str(row.get("Nº CEDULA", "")),
                                str(row.get("FECHA DE NACI.", "")),
                                str(row.get("EDAD", "")),
                                str(row.get("GENERO", "")),
                                str(row.get("Teléfono Personal", "")),
                                str(row.get("ESTAMENTO", "")),
                                str(row.get("PROMOCIÓN", "")),
                                str(row.get("DESCRIPCION", "")),
                                str(row.get("FECHA DE INGRESO", "")),
                                str(row.get("ANOS_SERVICIOS", "")),
                                str(row.get("RESOLUCION/ OGD - ASIGANCIÓN AL CENTRO", "")),
                                str(row.get("ASIGNADO / TRASLADO", "")),
                                str(row.get("DIRECCION, DEPENDENCIA O AREAS POLICIALES ", "")),
                                str(row.get("ASIGNADO A (CENTRO)", "")),
                                str(row.get("UBICACIÓN DEL CENTRO ASIGNADO", "")),
                                str(row.get("DEPARTAMENTO", "")),
                                str(row.get("TRUNO", "")),
                                str(row.get("GRUPO", "")),
                                str(row.get("FUNCIÓN", "")),
                                str(row.get("ESTADO  O STATUS", "")),
                                str(row.get("TIPO DE OPERATIVIDAD ", "")),
                                str(row.get("PERM_TEMP", "")),
                                str(row.get("CONDICIÓN", "")),
                                str(row.get("APTO - NO APTO", "")),
                                str(row.get("NIVEL", "")),
                                str(row.get("OBSERVACIÓN", "")),
                                str(row.get("CERTIFICADO DE BUENA SALUD ACTUALIZADO", "")),
                                str(row.get("FECHA DIAGNOSTICO", "")),
                                str(row.get("FECHA DE PROX. EVALUACIÓN", "")),
                                str(row.get("SALUD OCUPACIONAL", "")),
                                str(row.get("PENSIONADO", "")),
                                str(row.get("PROVINCIA", "")),
                                str(row.get("DISTRITO", "")),
                                str(row.get("CORREGIMIENTO", "")),
                                str(row.get("LUGAR", "")),
                                str(row.get("TIPO SANGRE", "")),
                                str(row.get("NOMBRE", "")),  # Emergencia
                                str(row.get("PARENTESCO", "")),
                                str(row.get("TELEFONO", "")),
                                str(row.get("ESTADO CIVIL", "")),
                                str(row.get("DONANTE DE SANGRE", "")),
                                str(row.get("SECUNDARIA", "")),
                                str(row.get("UNIVERSIDAD", "")),
                                str(row.get("M", "")),
                                str(row.get("F", "")),
                                str(row.get("TOTAL_HIJOS", "")),
                                str(row.get("CAMISA", "")),
                                str(row.get("PANTALON", "")),
                                str(row.get("SUETER", "")),
                                str(row.get("BOTAS", "")),
                                str(row.get("ZAPATOS", "")),
                                str(row.get("QUEPI", "")),
                                str(row.get("CORREA", ""))
                            ]
                            filas_a_insertar.append(fila_procesada)

                        # Conexión y envío masivo a la pestaña "Plan de Recojo"
                        cliente_gs = conectar_google_sheets()
                        hoja_bd = cliente_gs.open_by_key(ID_HOJA).worksheet("Plan de Recojo")
                        
                        hoja_bd.append_rows(filas_a_insertar)

                        st.success(f"🎉 ¡Plan de Recojo procesado con éxito! Se han registrado {len(filas_a_insertar)} unidades en el documento.")

            except Exception as e:
                st.error(f"❌ Ocurrió un error al procesar el archivo o inyectarlo en Google Sheets: {e}")
