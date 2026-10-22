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

# --- 2. ESTADOS DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "modo_pantalla" not in st.session_state:
    st.session_state.modo_pantalla = "DASHBOARD OPERATIVO"

def obtener_indice(lista, valor):
    try:
        # Intenta buscar convirtiendo todo a mayúsculas para evitar errores
        if isinstance(valor, str):
            return lista.index(valor.strip().upper())
        return lista.index(valor)
    except ValueError:
        return 0

def parse_date(date_str, min_year):
    try:
        parsed = datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
        return parsed
    except:
        return datetime(min_year, 1, 1).date()

def safe_int(value):
    try:
        return int(float(value))
    except:
        return 0

def safe_str(value):
    if pd.isna(value) or value is None:
        return ""
    return str(value).strip()

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
        st.subheader("Modo de Operación")

        if st.button("📊 Dashboard Operativo", use_container_width=True):
            st.session_state.modo_pantalla = "DASHBOARD OPERATIVO"
            st.rerun()

        if st.button("➕ Nuevo Registro", use_container_width=True):
            st.session_state.modo_pantalla = "NUEVO REGISTRO"
            st.rerun()

        if st.button("🔍 Consulta de Unidad", use_container_width=True):
            st.session_state.modo_pantalla = "CONSULTA DE UNIDAD"
            st.rerun()

        if st.button("📝 Incapacidad / Permiso", use_container_width=True):
            st.session_state.modo_pantalla = "INCAPACIDAD_PERMISO"
            st.rerun()

        if st.button("🔄 Unidades Trasladadas", use_container_width=True):
            st.session_state.modo_pantalla = "UNIDADES_TRASLADADAS"
            st.rerun()

        st.divider()
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # ==========================================
    # OPCIÓN 1: DASHBOARD OPERATIVO
    # ==========================================
    if st.session_state.modo_pantalla == "DASHBOARD OPERATIVO":
        st.markdown(
            "<h1 style='color: #00d4ff; text-shadow: 0 0 12px #00d4ff;'>📊 DASHBOARD OPERATIVO - CON</h1>",
            unsafe_allow_html=True,
        )

        col_dash1, col_dash2 = st.columns([2, 1])

        with col_dash1:
            st.markdown("<h3 style='color: #00d4ff;'>🏢 Distribución por Centros y Estamentos</h3>", unsafe_allow_html=True)
            tabla_centros_estamentos = pd.DataFrame({
                "ESTAMENTO / CENTRO": ["CON", "CORCOL", "COMCH", "COMDA", "COMAR", "COMSAM", "COMCHEP", "CEVIBO", "TOTAL VERTICAL"],
                "PNP": [0]*9, "SENAN": [0]*9, "SENAFRONT": [0]*9, "MINSEG": [0]*9, "MNJ": [0]*9, "TOTAL HORIZONTAL": [0]*9,
            })
            st.dataframe(tabla_centros_estamentos, use_container_width=True)

        with col_dash2:
            st.markdown("<h3 style='color: #00d4ff;'>⚡ Parte de Operatividad</h3>", unsafe_allow_html=True)
            tabla_operatividad = pd.DataFrame({
                "ESTATUS OPERATIVO": ["OPERATIVO", "NO OPERATIVO", "ORDENES A.COMP", "ORDENES DRP", "MNJ", "TOTAL"],
                "CANTIDAD": [0]*6,
            })
            st.dataframe(tabla_operatividad, use_container_width=True)

        st.markdown("---")
        st.markdown("<h3 style='color: #00d4ff;'>🎖️ Total de Unidades por Rango y Centros</h3>", unsafe_allow_html=True)
        tabla_rangos_centros = pd.DataFrame({
            "RANGO / CENTRO": ["COMISIONADO", "SUBCOMISIONADO", "MAYOR", "CAPITÁN", "TENIENTE", "SUBTENIENTE", "SARGENTO 1º", "SARGENTO 2º", "CABO 1º", "CABO 2º", "AGENTE", "MNJ", "TOTAL VERTICAL"],
            "CON": [0]*13, "CORCOL": [0]*13, "COMCH": [0]*13, "COMDA": [0]*13, "COMAR": [0]*13, "COMSAM": [0]*13, "COMCHEP": [0]*13, "CEVIBO": [0]*13, "TOTAL HORIZONTAL": [0]*13,
        })
        st.dataframe(tabla_rangos_centros, use_container_width=True)

    # ==========================================
    # OPCIÓN 2: NUEVO REGISTRO (CON PESTAÑAS Y GUARDADO FINAL)
    # ==========================================
    elif st.session_state.modo_pantalla == "NUEVO REGISTRO":
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

                            nueva_fila = [
                                timestamp, usuario_reg, rango, posic, placa_metalica, nombre, apellido, cedula,
                                str(fecha_naci), str(edad), genero, telefono_personal, estamento, num_promocion, descripcion_promo,
                                str(fecha_ingreso), str(anos_servicios), res_ogd, asig_trasl, direc_depen, asignado_centro, u_centro_asignado,
                                departamento, turno, grupo, funcion, estado_status, operat_no_operat, perm_temp, condicion, apto_no_apto,
                                nivel_salud, observacion, cert_buena_salud, str(fecha_diagnostico), str(f_prox_evaluacion), salud_ocupacional,
                                pensionado_opt, provincia, distrito, corregimiento, lugar, tipo_sangre, nombre_familiar, parentesco,
                                telefono_familiar, estado_civil, donante_sangre, secundaria, universidad, str(hijos_m), str(hijas_f),
                                str(total_hijos), talla_camisa, talla_pantalon, talla_sueter, talla_botas, talla_zapatos, talla_quepi, talla_correa
                            ]

                            st.info("Conectando con la base de datos principal...")
                            cliente_gs = conectar_google_sheets()
                            
                            # ---> ¡REEMPLAZA ESTO POR EL ID DE TU GOOGLE SHEET! <---
                            ID_HOJA = "PEGA_AQUI_EL_ID_DE_TU_HOJA" 
                            hoja_bd = cliente_gs.open_by_key(ID_HOJA).sheet1
                            hoja_bd.append_row(nueva_fila)

                            st.success(f"✔️ El elemento {rango} {nombre} {apellido} con cédula {cedula} ha sido registrado exitosamente.")
                        except Exception as e:
                            st.error(f"❌ Ocurrió un error al guardar en la base de datos: {e}")

    # ==========================================
    # OPCIÓN 3: CONSULTA DE UNIDAD (MODO EDICIÓN COMPLETO SIN PESTAÑAS)
    # ==========================================
    elif st.session_state.modo_pantalla == "CONSULTA DE UNIDAD":
        st.markdown(
            "<h1 style='color: #00d4ff; text-shadow: 0 0 12px #00d4ff;'>🔍 BÚSQUEDA Y EDICIÓN DE UNIDAD</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p>Busque la información de un elemento ingresando <b>Nombre, Apellido, Cédula, Posición o Placa Metálica</b>.</p>",
            unsafe_allow_html=True,
        )

        with st.container():
            c_busq1, c_busq2 = st.columns([3, 1])
            with c_busq1:
                busqueda = st.text_input("Término de búsqueda:")
            with c_busq2:
                st.markdown("<br>", unsafe_allow_html=True)
                buscar_btn = st.button("Buscar Elemento", use_container_width=True)

        if buscar_btn and busqueda.strip():
            st.session_state.termino_busqueda = busqueda.strip().lower()

        if "termino_busqueda" in st.session_state and st.session_state.termino_busqueda:
            term = st.session_state.termino_busqueda
            
            try:
                # Conectar y buscar
                cliente_gs = conectar_google_sheets()
                # ---> ¡REEMPLAZA ESTO POR EL ID DE TU GOOGLE SHEET! <---
                ID_HOJA = "PEGA_AQUI_EL_ID_DE_TU_HOJA" 
                hoja_bd = cliente_gs.open_by_key(ID_HOJA).sheet1
                records = hoja_bd.get_all_records()
                df_bd = pd.DataFrame(records)
                
                if df_bd.empty:
                    st.warning("La base de datos está vacía.")
                else:
                    # Filtro en múltiples columnas
                    cols_to_search = ['CEDULA', 'APELLIDO', 'NOMBRE', 'POSIC', 'PLACA_METALICA']
                    mask = pd.Series(False, index=df_bd.index)
                    for col in cols_to_search:
                        if col in df_bd.columns:
                            mask = mask | df_bd[col].astype(str).str.lower().str.contains(term, na=False)
                    
                    resultados = df_bd[mask]
                    
                    if len(resultados) == 0:
                        st.warning(f"No se encontraron registros que coincidan con '{term}'.")
                    else:
                        st.success(f"Se encontraron {len(resultados)} registro(s).")
                        
                        # Si hay varios, dejamos escoger
                        opciones = ["SELECCIONAR UNIDAD..."] + resultados.apply(
                            lambda row: f"{row.get('RANGO', '')} {row.get('NOMBRE', '')} {row.get('APELLIDO', '')} | Cédula: {row.get('CEDULA', '')}", axis=1
                        ).tolist()
                        
                        seleccion = st.selectbox("Seleccione el registro que desea visualizar o editar:", opciones)

                        if seleccion != "SELECCIONAR UNIDAD...":
                            idx_dataframe = opciones.index(seleccion) - 1
                            registro = resultados.iloc[idx_dataframe]
                            
                            # La fila real en Google Sheets es el índice del DataFrame + 2 (1 de cabecera y 1 porque Pandas es base 0)
                            fila_google_sheets = registro.name + 2 

                            st.markdown("---")
                            st.markdown("<h2 style='text-align:center; color:#00ffaa;'>FICHA COMPLETA DEL ELEMENTO</h2>", unsafe_allow_html=True)
                            
                            # =================================================================
                            # FORMULARIO GIGANTE DE EDICIÓN (SIN PESTAÑAS - TODO EN UNA VISTA)
                            # =================================================================
                            with st.form("form_edicion_completa", clear_on_submit=False):
                                
                                # SECCIÓN 1: DATOS PERSONALES
                                st.markdown("<h3 style='color: #00d4ff; border-bottom: 1px solid #00d4ff; padding-bottom: 5px; margin-top:20px;'>📋 1. DATOS PERSONALES</h3>", unsafe_allow_html=True)
                                c1, c2, c3, c4, c5 = st.columns(5)
                                e_rango = c1.selectbox("RANGO", lista_rangos, index=obtener_indice(lista_rangos, registro.get("RANGO", "")))
                                e_posic = c2.text_input("POSIC", value=safe_str(registro.get("POSIC", "")))
                                e_placa_metalica = c3.text_input("Nº PLACA METÁLICA", value=safe_str(registro.get("PLACA_METALICA", "")))
                                e_nombre = c4.text_input("NOMBRE", value=safe_str(registro.get("NOMBRE", "")))
                                e_apellido = c5.text_input("APELLIDO", value=safe_str(registro.get("APELLIDO", "")))

                                c6, c7, c8, c9, c10 = st.columns(5)
                                e_cedula = c6.text_input("Nº CÉDULA", value=safe_str(registro.get("CEDULA", "")))
                                e_fecha_naci = c7.date_input("FECHA DE NACIMIENTO", value=parse_date(registro.get("FECHA_NACIMIENTO", ""), 1950), min_value=datetime(1950, 1, 1))
                                e_edad = c8.number_input("EDAD", min_value=0, step=1, value=safe_int(registro.get("EDAD", 0)))
                                e_genero = c9.selectbox("GÉNERO", ["SELECCIONAR", "M", "F"], index=obtener_indice(["SELECCIONAR", "M", "F"], registro.get("GENERO", "")))
                                e_telefono_personal = c10.text_input("TELÉFONO PERSONAL", value=safe_str(registro.get("TELEFONO_PERSONAL", "")))

                                c11, c12, c13, c14, c15 = st.columns(5)
                                e_estamento = c11.selectbox("ESTAMENTO", lista_estamentos, index=obtener_indice(lista_estamentos, registro.get("ESTAMENTO", "")))
                                e_num_promocion = c12.text_input("Nº PROMOCIÓN", value=safe_str(registro.get("NUM_PROMOCION", "")))
                                e_descripcion_promo = c13.text_input("DESCRIPCIÓN PROMOCIÓN", value=safe_str(registro.get("DESCRIPCION_PROMOCION", "")))
                                e_fecha_ingreso = c14.date_input("FECHA DE INGRESO", value=parse_date(registro.get("FECHA_INGRESO", ""), 1980), min_value=datetime(1980, 1, 1))
                                e_anos_servicios = c15.number_input("AÑOS DE SERVICIO", min_value=0, step=1, value=safe_int(registro.get("ANOS_SERVICIOS", 0)))

                                # SECCIÓN 2: FUNCIONES GENERALES
                                st.markdown("<h3 style='color: #00d4ff; border-bottom: 1px solid #00d4ff; padding-bottom: 5px; margin-top:30px;'>📍 2. FUNCIONES GENERALES</h3>", unsafe_allow_html=True)
                                f1, f2, f3, f4, f5 = st.columns(5)
                                e_res_ogd = f1.text_input("RES. OGD. ASIG. AL CENTRO", value=safe_str(registro.get("RES_OGD_ASIG", "")))
                                e_asig_trasl = f2.text_input("ASIG. TRASLADO", value=safe_str(registro.get("ASIG_TRASLADO", "")))
                                e_direc_depen = f3.text_input("DIREC, DEPEN O A. POLICIALES", value=safe_str(registro.get("DIREC_DEPEN", "")))
                                e_asignado_centro = f4.text_input("ASIGNADO A (CENTRO)", value=safe_str(registro.get("ASIGNADO_CENTRO", "")))
                                e_u_centro_asignado = f5.text_input("U. DEL CENTRO ASIGNADO", value=safe_str(registro.get("U_CENTRO_ASIGNADO", "")))

                                f6, f7, f8, f9, f10 = st.columns(5)
                                e_departamento = f6.selectbox("DEPARTAMENTO", lista_departamentos, index=obtener_indice(lista_departamentos, registro.get("DEPARTAMENTO", "")))
                                e_turno = f7.selectbox("TURNO", lista_turnos, index=obtener_indice(lista_turnos, registro.get("TURNO", "")))
                                e_grupo = f8.text_input("GRUPO", value=safe_str(registro.get("GRUPO", "")))
                                e_funcion = f9.text_input("FUNCIÓN", value=safe_str(registro.get("FUNCION", "")))
                                e_estado_status = f10.selectbox("ESTADO O STATUS", lista_estados, index=obtener_indice(lista_estados, registro.get("ESTADO_STATUS", "")))

                                # SECCIÓN 3: OPERATIVIDAD
                                st.markdown("<h3 style='color: #00d4ff; border-bottom: 1px solid #00d4ff; padding-bottom: 5px; margin-top:30px;'>⚡ 3. TIPO DE OPERATIVIDAD Y DIAGNÓSTICO MÉDICO</h3>", unsafe_allow_html=True)
                                o1, o2, o3, o4, o5 = st.columns(5)
                                e_operat_no_operat = o1.selectbox("ESTATUS OPERAT.", ["SELECCIONAR", "OPERATIVO", "NO OPERATIVO"], index=obtener_indice(["SELECCIONAR", "OPERATIVO", "NO OPERATIVO"], registro.get("OPERAT_NO_OPERAT", "")))
                                e_perm_temp = o2.selectbox("PERM./TEMP.", ["SELECCIONAR", "PERM", "TEMP"], index=obtener_indice(["SELECCIONAR", "PERM", "TEMP"], registro.get("PERM_TEMP", "")))
                                e_condicion = o3.text_input("CONDICIÓN", value=safe_str(registro.get("CONDICION", "")))
                                e_apto_no_apto = o4.selectbox("APTO - NO APTO", ["SELECCIONAR", "APTO", "NO APTO"], index=obtener_indice(["SELECCIONAR", "APTO", "NO APTO"], registro.get("APTO_NO_APTO", "")))
                                e_nivel_salud = o5.text_input("NIVEL", value=safe_str(registro.get("NIVEL_SALUD", "")))

                                o6, o7, o8, o9, o10 = st.columns(5)
                                e_observacion = o6.text_input("OBSERVACIÓN", value=safe_str(registro.get("OBSERVACION", "")))
                                e_cert_buena_salud = o7.selectbox("CERT. BUENA SALUD ACT.", lista_select_si_no, index=obtener_indice(lista_select_si_no, registro.get("CERT_BUENA_SALUD", "")))
                                e_fecha_diagnostico = o8.date_input("FECHA DIAGNÓSTICO", value=parse_date(registro.get("FECHA_DIAGNOSTICO", ""), 2000))
                                e_f_prox_evaluacion = o9.date_input("F. PROX. EVALUACIÓN", value=parse_date(registro.get("F_PROX_EVALUACION", ""), 2000))
                                e_salud_ocupacional = o10.text_input("SALUD OCUPACIONAL", value=safe_str(registro.get("SALUD_OCUPACIONAL", "")))

                                o11, _ = st.columns([1, 4])
                                e_pensionado_opt = o11.selectbox("PENSIONADO", lista_si_no, index=obtener_indice(lista_si_no, registro.get("PENSIONADO", "")))

                                # SECCIÓN 4: RESIDENCIAL Y FAMILIAR
                                st.markdown("<h3 style='color: #00d4ff; border-bottom: 1px solid #00d4ff; padding-bottom: 5px; margin-top:30px;'>🏡 4. INFORMACIÓN RESIDENCIAL, FAMILIAR Y ACADÉMICA</h3>", unsafe_allow_html=True)
                                r1, r2, r3, r4, r5 = st.columns(5)
                                e_provincia = r1.selectbox("PROVINCIA", lista_provincias, index=obtener_indice(lista_provincias, registro.get("PROVINCIA", "")))
                                e_distrito = r2.text_input("DISTRITO", value=safe_str(registro.get("DISTRITO", "")))
                                e_corregimiento = r3.text_input("CORREGIMIENTO", value=safe_str(registro.get("CORREGIMIENTO", "")))
                                e_lugar = r4.text_input("LUGAR", value=safe_str(registro.get("LUGAR", "")))
                                e_tipo_sangre = r5.selectbox("TIPO DE SANGRE", lista_sangre, index=obtener_indice(lista_sangre, registro.get("TIPO_SANGRE", "")))

                                r6, r7, r8, r9, r10 = st.columns(5)
                                e_nombre_familiar = r6.text_input("NOMBRE (EMERGENCIA)", value=safe_str(registro.get("NOMBRE_EMERGENCIA", "")))
                                e_parentesco = r7.text_input("PARENTESCO", value=safe_str(registro.get("PARENTESCO", "")))
                                e_telefono_familiar = r8.text_input("TELÉFONO (EMERGENCIA)", value=safe_str(registro.get("TELEFONO_EMERGENCIA", "")))
                                e_estado_civil = r9.selectbox("ESTADO CIVIL", lista_estado_civil, index=obtener_indice(lista_estado_civil, registro.get("ESTADO_CIVIL", "")))
                                e_donante_sangre = r10.selectbox("DONANTE DE SANGRE", lista_si_no, index=obtener_indice(lista_si_no, registro.get("DONANTE_SANGRE", "")))

                                r11, r12, r13, r14, r15 = st.columns(5)
                                e_secundaria = r11.text_input("SECUNDARIA", value=safe_str(registro.get("SECUNDARIA", "")))
                                e_universidad = r12.text_input("UNIVERSIDAD", value=safe_str(registro.get("UNIVERSIDAD", "")))
                                e_hijos_m = r13.number_input("HIJOS M", min_value=0, step=1, value=safe_int(registro.get("HIJOS_M", 0)))
                                e_hijas_f = r14.number_input("HIJAS F", min_value=0, step=1, value=safe_int(registro.get("HIJAS_F", 0)))
                                e_total_hijos = r15.number_input("TOTAL DE HIJOS", min_value=0, step=1, value=safe_int(registro.get("TOTAL_HIJOS", 0)))

                                # SECCIÓN 5: TALLAS
                                st.markdown("<h3 style='color: #00d4ff; border-bottom: 1px solid #00d4ff; padding-bottom: 5px; margin-top:30px;'>🎽 5. TALLAS DE UNIFORME Y EQUIPAMIENTO</h3>", unsafe_allow_html=True)
                                t1, t2, t3, t4, t5 = st.columns(5)
                                e_talla_camisa = t1.text_input("CAMISA", value=safe_str(registro.get("TALLA_CAMISA", "")))
                                e_talla_pantalon = t2.text_input("PANTALÓN", value=safe_str(registro.get("TALLA_PANTALON", "")))
                                e_talla_sueter = t3.text_input("SUÉTER", value=safe_str(registro.get("TALLA_SUETER", "")))
                                e_talla_botas = t4.text_input("BOTAS", value=safe_str(registro.get("TALLA_BOTAS", "")))
                                e_talla_zapatos = t5.text_input("ZAPATOS", value=safe_str(registro.get("TALLA_ZAPATOS", "")))

                                t6, t7, t8 = st.columns([1, 1, 3])
                                e_talla_quepi = t6.text_input("QUÉPI", value=safe_str(registro.get("TALLA_QUEPI", "")))
                                e_talla_correa = t7.text_input("CORREA", value=safe_str(registro.get("TALLA_CORREA", "")))

                                st.markdown("<hr style='border:1px dashed #00ffaa; margin-top: 30px;'>", unsafe_allow_html=True)
                                
                                btn_actualizar = st.form_submit_button("🔄 Guardar Cambios (Actualizar Fila en Base de Datos)", use_container_width=True)

                                if btn_actualizar:
                                    try:
                                        # Recopilamos todos los datos igual que en nuevo registro, manteniendo timestamp original si es posible, o generando uno nuevo de edición.
                                        fila_actualizada = [
                                            str(registro.get("TIMESTAMP", datetime.now(pytz.timezone('America/Panama')).strftime("%Y-%m-%d %H:%M:%S"))), 
                                            st.session_state.get("usuario_actual", "DESCONOCIDO") + " (Editó)", 
                                            e_rango, e_posic, e_placa_metalica, e_nombre, e_apellido, e_cedula,
                                            str(e_fecha_naci), str(e_edad), e_genero, e_telefono_personal, e_estamento, e_num_promocion, e_descripcion_promo,
                                            str(e_fecha_ingreso), str(e_anos_servicios), e_res_ogd, e_asig_trasl, e_direc_depen, e_asignado_centro, e_u_centro_asignado,
                                            e_departamento, e_turno, e_grupo, e_funcion, e_estado_status, e_operat_no_operat, e_perm_temp, e_condicion, e_apto_no_apto,
                                            e_nivel_salud, e_observacion, e_cert_buena_salud, str(e_fecha_diagnostico), str(e_f_prox_evaluacion), e_salud_ocupacional,
                                            e_pensionado_opt, e_provincia, e_distrito, e_corregimiento, e_lugar, e_tipo_sangre, e_nombre_familiar, e_parentesco,
                                            e_telefono_familiar, e_estado_civil, e_donante_sangre, e_secundaria, e_universidad, str(e_hijos_m), str(e_hijas_f),
                                            str(e_total_hijos), e_talla_camisa, e_talla_pantalon, e_talla_sueter, e_talla_botas, e_talla_zapatos, e_talla_quepi, e_talla_correa
                                        ]

                                        st.info(f"Actualizando registro en la fila {fila_google_sheets} de la Base de Datos...")
                                        
                                        # Enviar actualización a Google Sheets en el rango específico de esa fila
                                        rango_a_actualizar = f"A{fila_google_sheets}:BH{fila_google_sheets}"
                                        hoja_bd.update(values=[fila_actualizada], range_name=rango_a_actualizar)
                                        
                                        st.success(f"✔️ Registro de {e_nombre} {e_apellido} actualizado correctamente.")
                                    except Exception as e:
                                        st.error(f"❌ Ocurrió un error al actualizar: {e}")

            except Exception as e:
                st.error(f"Error al conectar con la base de datos o buscar: {e}")

    # ==========================================
    # OPCIÓN 4: REGISTRO DE INCAPACIDAD, PERMISO, ETC.
    # ==========================================
    elif st.session_state.modo_pantalla == "INCAPACIDAD_PERMISO":
        st.markdown(
            "<h1 style='color: #00d4ff; text-shadow: 0 0 12px #00d4ff;'>📝 REGISTRO DE INCAPACIDADES Y PERMISOS</h1>",
            unsafe_allow_html=True,
        )

        with st.form("form_incapacidades", clear_on_submit=False):
            st.subheader("📌 Detalles de la Novedad o Ausencia")
            col_inc1, col_inc2 = st.columns(2)
            cedula_unidad = col_inc1.text_input("Cédula de la Unidad")
            tipo_novedad = col_inc2.selectbox(
                "TIPO DE NOVEDAD",
                ["SELECCIONAR", "INCAPACIDAD MÉDICA", "PERMISO PERSONAL", "VACACIONES", "LICENCIA", "SUSPENSIÓN"],
            )

            col_inc3, col_inc4 = st.columns(2)
            f_inicio = col_inc3.date_input("FECHA DE INICIO")
            f_fin = col_inc4.date_input("FECHA DE FIN")

            observacion_inc = st.text_area("OBSERVACIONES / DIAGNÓSTICO / DETALLES")

            st.divider()
            btn_guardar_inc = st.form_submit_button("Registrar Novedad")

            if btn_guardar_inc:
                if tipo_novedad == "SELECCIONAR" or not cedula_unidad.strip():
                    st.error("❌ Debe ingresar la cédula y seleccionar el tipo de novedad.")
                else:
                    st.success(f"✔️ Novedad ({tipo_novedad}) registrada con éxito para la cédula {cedula_unidad}.")

    # ==========================================
    # OPCIÓN 5: UNIDADES TRASLADADAS
    # ==========================================
    elif st.session_state.modo_pantalla == "UNIDADES_TRASLADADAS":
        st.markdown(
            "<h1 style='color: #00d4ff; text-shadow: 0 0 12px #00d4ff;'>🔄 UNIDADES TRASLADADAS</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p>Listado completo de unidades que registran movimientos, asignaciones o traslados entre centros y dependencias.</p>",
            unsafe_allow_html=True,
        )

        tabla_traslados = pd.DataFrame(
            {
                "Nº": [],
                "RANGO": [],
                "NOMBRE": [],
                "APELLIDO": [],
                "CÉDULA": [],
                "CENTRO ANTERIOR": [],
                "CENTRO NUEVO / TRASLADO": [],
                "FECHA DE TRASLADO": [],
                "RESOLUCIÓN / OGD": [],
            }
        )
        st.dataframe(tabla_traslados, use_container_width=True)
        st.info("ℹ️ Aquí se visualizarán todos los datos detallados de las unidades trasladadas.")
