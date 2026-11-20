import streamlit as st
import pandas as pd
import glob
import base64
from datetime import datetime, date
import pytz
import gspread
from google.oauth2.service_account import Credentials
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS NEÓN + VIDEO LOCAL DE FONDO ---
st.set_page_config(
    page_title="CON - Recursos Humanos",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cachear el video para que no se recargue en cada clic
@st.cache_data
def cargar_video_fondo():
    archivos_video = (
        glob.glob("*VIDEO*.mp4") + glob.glob("*video*.mp4") + glob.glob("*.mp4")
    )
    if archivos_video:
        try:
            with open(archivos_video[0], "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception as e:
            print(f"Error cargando video: {e}")
    return ""

video_base64 = cargar_video_fondo()

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
    div.stButton > button, div.stFormSubmitButton > button {{
        background-color: rgba(10, 15, 25, 0.9) !important;
        color: white !important;
        border: 2px solid #00d4ff !important;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        transition: 0.3s ease;
    }}
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {{
        background-color: #00d4ff !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #00d4ff;
    }}
    div.stButton > button p, div.stFormSubmitButton > button p {{
        color: white !important;
        font-weight: bold;
    }}
    div.stButton > button:hover p, div.stFormSubmitButton > button:hover p {{
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

# --- CONFIGURACIÓN DE GOOGLE SHEETS ---
# ID CORREGIDO (44 caracteres exactos de tu hoja Recursos_Humanos)
ID_HOJA = "10RXYbyOVD8DVUvwCDwVa3Btpj9dd2mLv5cacJRCAKes"

@st.cache_resource
def conectar_google_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=scopes
    )
    return gspread.authorize(creds)

def limpiar_valor(val):
    """Convierte 'SELECCIONAR' en vacío y limpia espacios."""
    if val is None:
        return ""
    texto = str(val).strip().upper()
    return "" if texto == "SELECCIONAR" else texto

def calcular_anios(fecha_ref, hoy):
    if not fecha_ref:
        return 0
    return hoy.year - fecha_ref.year - ((hoy.month, hoy.day) < (fecha_ref.month, fecha_ref.day))

# --- 2. ESTADOS DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

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
            user = st.text_input("👤 Usuario institucional").strip().upper()
            password = st.text_input("🔑 Contraseña", type="password").strip()
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
    lista_centros = ["SELECCIONAR", "CON", "CORCOL", "COMCH", "COMDA", "COMAR", "COMSAM", "COMCHEP", "CEVIBO"]
    lista_departamentos = [
        "SELECCIONAR", "DIRECCION", "SUPERVISORA ADM", "PLANEAMIENTO",
        "COOR. TECNOLOGICO", "OPERACIONES", "ESTADISTICA", "RECURSOS HUMANOS",
    ]
    lista_turnos = ["SELECCIONAR", "4X4", "5X2", "7X7", "20X20", "24X24", "ROTATIVO", "ADMINISTRATIVO"]
    lista_sangre = ["SELECCIONAR", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    lista_provincias = [
        "SELECCIONAR", "PANAMÁ", "PANAMÁ OESTE", "COLÓN", "CHIRIQUÍ", "VERAGUAS",
        "COCLÉ", "HERRERA", "LOS SANTOS", "BOCAS DEL TORO", "DARIÉN",
        "COMARCA NGÄBE-BUGLÉ", "COMARCA GUNA YALA", "COMARCA EMBERÁ-WOUNAAN"
    ]
    lista_estados = ["SELECCIONAR", "ACTIVO", "INACTIVO", "VACACIONES", "PENSIONADO", "INCAPACITADO"]
    lista_estado_civil = ["SELECCIONAR", "SOLTERO/A", "CASADO/A", "UNIDO/A", "DIVORCIADO/A", "VIUDO/A"]
    lista_si_no = ["NO", "SÍ"]
    lista_select_si_no = ["SELECCIONAR", "SÍ", "NO"]

    # --- BARRA LATERAL (SIDEBAR) ---
    with st.sidebar:
        st.write(f"👤 Usuario: **{st.session_state.get('usuario_actual', 'Admin')}**")

        st.subheader("🕒 Hora Actual")
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
        st.markdown("➕ **Registro Individual** (Activo)")

        st.divider()
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # ==========================================
    # NUEVO REGISTRO INDIVIDUAL
    # ==========================================
    st.markdown(
        "<h1 style='color: #00d4ff; text-shadow: 0 0 12px #00d4ff;'>➕ NUEVO REGISTRO DE PERSONAL</h1>",
        unsafe_allow_html=True,
    )

    hoy_pa = datetime.now(pytz.timezone('America/Panama')).date()

    with st.form("form_nuevo_registro_excel", clear_on_submit=True):
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 1. DATOS PERSONALES",
            "📍 2. FUNCIONES GENERALES",
            "⚡ 3. OPERATIVIDAD",
            "🏡 4. RESIDENCIAL / ACADÉMICO",
            "🎽 5. TALLAS"
        ])

        with tab1:
            st.markdown("<h3 style='color: #00d4ff; margin-bottom: 20px;'>Información Personal</h3>", unsafe_allow_html=True)
            c1, c2, c3, c4, c5 = st.columns(5)
            rango = c1.selectbox("RANGO *", lista_rangos)
            posic = c2.text_input("POSIC")
            placa_metalica = c3.text_input("Nº PLACA METÁLICA")
            nombre = c4.text_input("NOMBRE *")
            apellido = c5.text_input("APELLIDO *")

            c6, c7, c8, c9, c10 = st.columns(5)
            cedula = c6.text_input("Nº CÉDULA *")
            fecha_naci = c7.date_input("FECHA DE NACIMIENTO", value=date(1990, 1, 1), min_value=date(1950, 1, 1), max_value=hoy_pa)
            genero = c8.selectbox("GÉNERO", ["SELECCIONAR", "M", "F"])
            telefono_personal = c9.text_input("TELÉFONO PERSONAL")
            estamento = c10.selectbox("ESTAMENTO", lista_estamentos)

            c11, c12, c13 = st.columns(3)
            num_promocion = c11.text_input("Nº PROMOCIÓN")
            descripcion_promo = c12.text_input("DESCRIPCIÓN PROMOCIÓN")
            fecha_ingreso = c13.date_input("FECHA DE INGRESO", value=date(2015, 1, 1), min_value=date(1980, 1, 1), max_value=hoy_pa)

        with tab2:
            st.markdown("<h3 style='color: #00d4ff; margin-bottom: 20px;'>Funciones y Asignaciones</h3>", unsafe_allow_html=True)
            f1, f2, f3, f4, f5 = st.columns(5)
            res_ogd = f1.text_input("RES. OGD. ASIG. AL CENTRO")
            asig_trasl = f2.text_input("ASIG. TRASLADO")
            direc_depen = f3.text_input("DIREC, DEPEN O A. POLICIALES")
            asignado_centro = f4.selectbox("ASIGNADO A (CENTRO)", lista_centros)
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
            tiene_diagnostico = o8.checkbox("¿Registrar fechas médicas?")
            fecha_diagnostico = o9.date_input("FECHA DIAGNÓSTICO", value=hoy_pa)
            f_prox_evaluacion = o10.date_input("F. PROX. EVALUACIÓN", value=hoy_pa)

            o11, o12, _ = st.columns([2, 1, 2])
            salud_ocupacional = o11.text_input("SALUD OCUPACIONAL")
            pensionado_opt = o12.selectbox("PENSIONADO", lista_si_no)

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

            r11, r12, r13, r14 = st.columns(4)
            secundaria = r11.text_input("SECUNDARIA")
            universidad = r12.text_input("UNIVERSIDAD")
            hijos_m = r13.number_input("HIJOS M", min_value=0, step=1)
            hijas_f = r14.number_input("HIJAS F", min_value=0, step=1)

        with tab5:
            st.markdown("<h3 style='color: #00d4ff; margin-bottom: 20px;'>Tallas de Uniforme y Equipamiento</h3>", unsafe_allow_html=True)
            t1, t2, t3, t4, t5 = st.columns(5)
            talla_camisa = t1.text_input("CAMISA")
            talla_pantalon = t2.text_input("PANTALÓN")
            talla_sueter = t3.text_input("SUÉTER")
            talla_botas = t4.text_input("BOTAS")
            talla_zapatos = t5.text_input("ZAPATOS")

            t6, t7, _ = st.columns([1, 1, 3])
            talla_quepi = t6.text_input("QUÉPI")
            talla_correa = t7.text_input("CORREA")

            st.markdown("<hr style='border:1px dashed #00d4ff; margin-top: 30px;'>", unsafe_allow_html=True)
            submitted_excel = st.form_submit_button("💾 Guardar Registro Oficial de Personal", use_container_width=True)

            if submitted_excel:
                if not nombre.strip() or not apellido.strip() or not cedula.strip() or rango == "SELECCIONAR":
                    st.error("❌ Complete los campos obligatorios de la Pestaña 1 (Rango, Nombre, Apellido y Cédula).")
                else:
                    try:
                        tz = pytz.timezone('America/Panama')
                        timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                        usuario_reg = st.session_state.get("usuario_actual", "DESCONOCIDO")

                        edad_calc = calcular_anios(fecha_naci, hoy_pa)
                        anos_serv_calc = calcular_anios(fecha_ingreso, hoy_pa)
                        total_hijos_calc = int(hijos_m + hijas_f)

                        f_diag_str = str(fecha_diagnostico) if tiene_diagnostico else ""
                        f_eval_str = str(f_prox_evaluacion) if tiene_diagnostico else ""

                        # 60 COLUMNAS EXACTAS (A1:BH1 de Plan_de_Recojo) SIN celda vacía al inicio
                        nueva_fila = [
                            timestamp,
                            limpiar_valor(usuario_reg),
                            limpiar_valor(rango),
                            limpiar_valor(posic),
                            limpiar_valor(placa_metalica),
                            limpiar_valor(nombre),
                            limpiar_valor(apellido),
                            limpiar_valor(cedula),
                            str(fecha_naci),
                            edad_calc,
                            limpiar_valor(genero),
                            limpiar_valor(telefono_personal),
                            limpiar_valor(estamento),
                            limpiar_valor(num_promocion),
                            limpiar_valor(descripcion_promo),
                            str(fecha_ingreso),
                            anos_serv_calc,
                            limpiar_valor(res_ogd),
                            limpiar_valor(asig_trasl),
                            limpiar_valor(direc_depen),
                            limpiar_valor(asignado_centro),
                            limpiar_valor(u_centro_asignado),
                            limpiar_valor(departamento),
                            limpiar_valor(turno),
                            limpiar_valor(grupo),
                            limpiar_valor(funcion),
                            limpiar_valor(estado_status),
                            limpiar_valor(operat_no_operat),
                            limpiar_valor(perm_temp),
                            limpiar_valor(condicion),
                            limpiar_valor(apto_no_apto),
                            limpiar_valor(nivel_salud),
                            limpiar_valor(observacion),
                            limpiar_valor(cert_buena_salud),
                            f_diag_str,
                            f_eval_str,
                            limpiar_valor(salud_ocupacional),
                            limpiar_valor(pensionado_opt),
                            limpiar_valor(provincia),
                            limpiar_valor(distrito),
                            limpiar_valor(corregimiento),
                            limpiar_valor(lugar),
                            limpiar_valor(tipo_sangre),
                            limpiar_valor(nombre_familiar),
                            limpiar_valor(parentesco),
                            limpiar_valor(telefono_familiar),
                            limpiar_valor(estado_civil),
                            limpiar_valor(donante_sangre),
                            limpiar_valor(secundaria),
                            limpiar_valor(universidad),
                            int(hijos_m),
                            int(hijas_f),
                            total_hijos_calc,
                            limpiar_valor(talla_camisa),
                            limpiar_valor(talla_pantalon),
                            limpiar_valor(talla_sueter),
                            limpiar_valor(talla_botas),
                            limpiar_valor(talla_zapatos),
                            limpiar_valor(talla_quepi),
                            limpiar_valor(talla_correa),
                        ]

                        cliente_gs = conectar_google_sheets()
                        hoja_bd = cliente_gs.open_by_key(ID_HOJA).worksheet("Plan_de_Recojo")
                        hoja_bd.append_row(nueva_fila, value_input_option="USER_ENTERED")

                        st.success(f"✔️ El elemento {limpiar_valor(rango)} {limpiar_valor(nombre)} {limpiar_valor(apellido)} con cédula {limpiar_valor(cedula)} ha sido registrado exitosamente.")
                    except Exception as e:
                        st.error(f"❌ Ocurrió un error al guardar en la base de datos: {e}")
