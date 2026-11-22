import streamlit as st
import pandas as pd
import glob
import base64
import re
from io import BytesIO
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
    div.stButton > button, div.stFormSubmitButton > button, div.stDownloadButton > button {{
        background-color: rgba(10, 15, 25, 0.9) !important;
        color: white !important;
        border: 2px solid #00d4ff !important;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
        transition: 0.3s ease;
    }}
    div.stButton > button:hover, div.stFormSubmitButton > button:hover, div.stDownloadButton > button:hover {{
        background-color: #00d4ff !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #00d4ff;
    }}
    div.stButton > button p, div.stFormSubmitButton > button p, div.stDownloadButton > button p {{
        color: white !important;
        font-weight: bold;
    }}
    div.stButton > button:hover p, div.stFormSubmitButton > button:hover p, div.stDownloadButton > button:hover p {{
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
ID_HOJA = "10RXYbyOVD8DVUvwCDwVa3Btpj9dd2mLv5cacJRCAKes"
PESTANA_PERSONAL = "Plan_de_Recojo"
PESTANA_AGREGADAS = "Unidades_Agregadas"
PESTANA_JUB_PRES_TRAS = "Vac.Jubilacion_U.Prestados_U.Trasladados"
PESTANA_NOVEDADES = "Permiso,incapacidad,licencia"

PESTANAS_UNIDADES = [
    PESTANA_PERSONAL,
    PESTANA_AGREGADAS,
    PESTANA_JUB_PRES_TRAS,
]

# Pestañas que siempre deben mantenerse ordenadas por jerarquía de RANGO
PESTANAS_ORDENADAS_RANGO = {
    PESTANA_PERSONAL,
    PESTANA_AGREGADAS,
}

COLUMNAS_OFICIALES = [
    "TIMESTAMP", "USUARIO_REGISTRO", "RANGO", "POSIC", "PLACA_METALICA",
    "NOMBRE", "APELLIDO", "CEDULA", "FECHA_NACIMIENTO", "EDAD", "GENERO",
    "TELEFONO_PERSONAL", "ESTAMENTO", "NUM_PROMOCION", "DESCRIPCION_PROMOCION",
    "FECHA_INGRESO", "ANOS_SERVICIOS", "RES_OGD_ASIG", "ASIG_TRASLADO",
    "DIREC_DEPEN", "ASIGNADO_CENTRO", "U_CENTRO_ASIGNADO", "DEPARTAMENTO",
    "TURNO", "GRUPO", "FUNCION", "ESTADO_STATUS", "OPERAT_NO_OPERAT",
    "PERM_TEMP", "CONDICION", "APTO_NO_APTO", "NIVEL_SALUD", "OBSERVACION",
    "CERT_BUENA_SALUD", "FECHA_DIAGNOSTICO", "F_PROX_EVALUACION",
    "SALUD_OCUPACIONAL", "PENSIONADO", "PROVINCIA", "DISTRITO",
    "CORREGIMIENTO", "LUGAR", "TIPO_SANGRE", "NOMBRE_EMERGENCIA",
    "PARENTESCO", "TELEFONO_EMERGENCIA", "ESTADO_CIVIL", "DONANTE_SANGRE",
    "SECUNDARIA", "UNIVERSIDAD", "HIJOS_M", "HIJAS_F", "TOTAL_HIJOS",
    "TALLA_CAMISA", "TALLA_PANTALON", "TALLA_SUETER", "TALLA_BOTAS",
    "TALLA_ZAPATOS", "TALLA_QUEPI", "TALLA_CORREA",
]

# Esquema gerencial de 27 columnas (sin PLACA_METALICA) para Permiso,incapacidad,licencia
COLUMNAS_NOVEDADES = [
    "ID_NOVEDAD", "TIMESTAMP", "USUARIO_REGISTRO", "RANGO", "POSIC",
    "NOMBRE", "APELLIDO", "CEDULA", "ESTAMENTO", "ASIGNADO_CENTRO",
    "DEPARTAMENTO", "TURNO", "GRUPO", "FUNCION", "IMPACTO_OPERATIVO",
    "TIPO_NOVEDAD", "SUBTIPO_MOTIVO", "FECHA_INICIO", "FECHA_FIN",
    "DIAS_TOTALES", "DIAS_RESTANTES", "ESTADO_TRAMITE", "ALERTA_REINTEGRO",
    "NUM_DOCUMENTO_RESPALDO", "ENTIDAD_EMISORA", "AUTORIZADO_POR",
    "OBSERVACION",
]

# Jerarquía oficial de rangos policiales / estamentales (menor número = mayor jerarquía)
JERARQUIA_RANGOS = {
    "COMISIONADO": 1,
    "COMISIONADO (A)": 1,
    "COMISIONADA": 1,
    "COM.": 1,
    "SUBCOMISIONADO": 2,
    "SUBCOMISIONADA": 2,
    "SUBCOM.": 2,
    "SUBCOM": 2,
    "MAYOR": 3,
    "CAPITÁN": 4,
    "CAPITAN": 4,
    "TENIENTE": 5,
    "SUBTENIENTE": 6,
    "SARGENTO 1º": 7,
    "SARGENTO 1°": 7,
    "SARGENTO 1RO": 7,
    "SARGENTO PRIMERO": 7,
    "SARGENTO 2º": 8,
    "SARGENTO 2°": 8,
    "SARGENTO 2DO": 8,
    "SARGENTO SEGUNDO": 8,
    "CABO 1º": 9,
    "CABO 1°": 9,
    "CABO 1RO": 9,
    "CABO PRIMERO": 9,
    "CABO 2º": 10,
    "CABO 2°": 10,
    "CABO 2DO": 10,
    "CABO SEGUNDO": 10,
    "AGENTE": 11,
    "MINSEG": 12,
    "M.N.J.": 13,
    "M.N.J": 13,
    "MNJ": 13,
}

def clave_orden_rango_posic(fila):
    rango_txt = re.sub(r"\s+", " ", str(fila[2]).strip().upper())
    peso_rango = JERARQUIA_RANGOS.get(rango_txt, 99)
    posic_txt = str(fila[3]).strip()
    try:
        peso_posic = int(float(posic_txt)) if posic_txt else 999999999
    except ValueError:
        peso_posic = 999999999
    return (peso_rango, peso_posic, str(fila[6]).strip().upper(), str(fila[5]).strip().upper())

@st.cache_resource
def conectar_google_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=scopes
    )
    return gspread.authorize(creds)

def obtener_o_crear_worksheet(nombre_pestana, columnas_hdr=None):
    if columnas_hdr is None:
        columnas_hdr = COLUMNAS_NOVEDADES if nombre_pestana == PESTANA_NOVEDADES else COLUMNAS_OFICIALES
    cliente_gs = conectar_google_sheets()
    libro = cliente_gs.open_by_key(ID_HOJA)
    try:
        ws = libro.worksheet(nombre_pestana)
    except gspread.WorksheetNotFound:
        ws = libro.add_worksheet(title=nombre_pestana, rows=1000, cols=len(columnas_hdr))
    if not ws.row_values(1):
        ws.append_row(columnas_hdr, value_input_option="USER_ENTERED")
    return ws

def ordenar_pestana_por_rango(nombre_pestana):
    """
    Reordena por jerarquía de RANGO + POSIC las pestañas activas de centros
    (Plan_de_Recojo y Unidades_Agregadas) y restablece las fórmulas dinámicas
    de EDAD (J), ANOS_SERVICIOS (Q) y TOTAL_HIJOS (BA) en cada fila.
    No modifica Vac.Jubilacion_U.Prestados_U.Trasladados.
    """
    if nombre_pestana not in PESTANAS_ORDENADAS_RANGO:
        return

    ws = obtener_o_crear_worksheet(nombre_pestana, COLUMNAS_OFICIALES)
    todos = ws.get_all_values()
    if len(todos) <= 2:
        return

    num_cols = len(COLUMNAS_OFICIALES)
    encabezado = todos[0][:num_cols] + COLUMNAS_OFICIALES[len(todos[0]):]
    filas = [
        f[:num_cols] + [""] * max(0, num_cols - len(f))
        for f in todos[1:]
        if any(str(celda).strip() != "" for celda in f)
    ]

    filas_ordenadas = sorted(filas, key=clave_orden_rango_posic)

    # Reaplicar fórmulas dinámicas por fila (2..N+1) en columnas J (EDAD), Q (ANOS_SERVICIOS) y BA (TOTAL_HIJOS)
    for idx, fila in enumerate(filas_ordenadas, start=2):
        fila[9] = f'=IF(ISBLANK(I{idx}),"",DATEDIF(I{idx},TODAY(),"Y"))'
        fila[16] = f'=IF(ISBLANK(P{idx}),"",DATEDIF(P{idx},TODAY(),"Y"))'
        fila[52] = f'=IF(AND(ISBLANK(AY{idx}),ISBLANK(AZ{idx})),"",SUM(AY{idx}:AZ{idx}))'

    matriz_final = [encabezado] + filas_ordenadas
    ws.clear()
    ws.update(range_name=f"A1:BH{len(matriz_final)}", values=matriz_final, value_input_option="USER_ENTERED")

@st.cache_data(ttl=60)
def leer_pestana_df(nombre_pestana, columnas_esperadas):
    try:
        ws = obtener_o_crear_worksheet(nombre_pestana, columnas_esperadas)
        valores = ws.get_all_values()
        if not valores or len(valores) <= 1:
            return pd.DataFrame(columns=columnas_esperadas)
        encabezados = [str(h).strip() for h in valores[0]]
        filas = valores[1:]
        num_cols = len(encabezados)
        filas_norm = [
            f[:num_cols] + [""] * max(0, num_cols - len(f))
            for f in filas
        ]
        return pd.DataFrame(filas_norm, columns=encabezados)
    except Exception as e:
        st.error(f"❌ Error al leer la pestaña `{nombre_pestana}`: {e}")
        return pd.DataFrame(columns=columnas_esperadas)

def mover_unidad_entre_pestanas(
    pestana_origen,
    pestana_destino,
    indice_df_origen,
    nuevo_estado_status,
    usuario_actual,
    timestamp_str,
    respaldo_mov="",
    obs_adicional="",
):
    if pestana_origen == pestana_destino:
        raise ValueError("La pestaña de origen y destino no pueden ser la misma.")

    ws_orig = obtener_o_crear_worksheet(pestana_origen, COLUMNAS_OFICIALES)
    ws_dest = obtener_o_crear_worksheet(pestana_destino, COLUMNAS_OFICIALES)

    todos_orig = ws_orig.get_all_values()
    if len(todos_orig) <= 1:
        raise ValueError(f"La pestaña `{pestana_origen}` no tiene registros.")

    encabezados = [str(h).strip() for h in todos_orig[0]]
    num_cols = len(COLUMNAS_OFICIALES)

    fila_sheet_num = indice_df_origen + 2
    if fila_sheet_num < 2 or fila_sheet_num > len(todos_orig):
        raise IndexError("No se encontró la fila seleccionada en la hoja de origen.")

    fila_cruda = todos_orig[fila_sheet_num - 1]
    fila_60 = fila_cruda[:num_cols] + [""] * max(0, num_cols - len(fila_cruda))

    mapa_cols = {col: idx for idx, col in enumerate(COLUMNAS_OFICIALES)}
    if encabezados != COLUMNAS_OFICIALES:
        dic_fila = {col: "" for col in COLUMNAS_OFICIALES}
        for c_idx, h_name in enumerate(encabezados):
            if h_name in dic_fila and c_idx < len(fila_cruda):
                dic_fila[h_name] = fila_cruda[c_idx]
        fila_60 = [dic_fila[c] for c in COLUMNAS_OFICIALES]

    estado_limpio = limpiar_valor(nuevo_estado_status)
    if estado_limpio:
        fila_60[mapa_cols["ESTADO_STATUS"]] = estado_limpio

    if limpiar_valor(respaldo_mov):
        prev_res = str(fila_60[mapa_cols["RES_OGD_ASIG"]]).strip()
        nuevo_res = limpiar_valor(respaldo_mov)
        fila_60[mapa_cols["RES_OGD_ASIG"]] = (
            f"{prev_res} | {nuevo_res}" if prev_res and nuevo_res not in prev_res else (nuevo_res or prev_res)
        )

    nota_mov = f"MOVIDO [{pestana_origen} -> {pestana_destino}] POR {limpiar_valor(usuario_actual)} ({timestamp_str})"
    if limpiar_valor(obs_adicional):
        nota_mov = f"{nota_mov} · {limpiar_valor(obs_adicional)}"

    obs_previa = str(fila_60[mapa_cols["OBSERVACION"]]).strip()
    fila_60[mapa_cols["OBSERVACION"]] = f"{obs_previa} | {nota_mov}" if obs_previa else nota_mov

    # 1. Agregar a pestaña destino y eliminar de pestaña origen
    ws_dest.append_row(fila_60, value_input_option="USER_ENTERED")
    ws_orig.delete_rows(fila_sheet_num)

    # 2. Mantener ordenadas por RANGO las pestañas activas afectadas (Plan_de_Recojo / Unidades_Agregadas)
    #    La tercera pestaña (Vac.Jubilacion_U.Prestados_U.Trasladados) conserva su orden cronológico/resolución.
    if pestana_destino in PESTANAS_ORDENADAS_RANGO:
        ordenar_pestana_por_rango(pestana_destino)
    if pestana_origen in PESTANAS_ORDENADAS_RANGO:
        ordenar_pestana_por_rango(pestana_origen)

    leer_pestana_df.clear()

def convertir_df_a_excel(df, nombre_hoja="Datos"):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=nombre_hoja[:31])
    return buffer.getvalue()

def es_placeholder_vacio(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return True
    s = str(val).strip()
    if s == "" or s.upper() in ("NAN", "NAT", "NONE", "00:00:00", "SELECCIONAR"):
        return True
    if s.upper() in ("X", "XX", "XXX", "XXXX", "XXXXX", "XXXXXX", "********", "…"):
        return True
    if re.fullmatch(r"[xX*\-.\s…]+", s) and s.upper() not in ("XX", "X"):
        return True
    return False

def limpiar_valor(val):
    if es_placeholder_vacio(val):
        return ""
    if isinstance(val, (datetime, date, pd.Timestamp)):
        return val.strftime("%Y-%m-%d")
    s = re.sub(r"\s+", " ", str(val).strip())
    if re.fullmatch(r"\d+\.0", s):
        s = s[:-2]
    return s.upper()

def calcular_anios(fecha_ref, hoy):
    if not fecha_ref:
        return ""
    return hoy.year - fecha_ref.year - ((hoy.month, hoy.day) < (fecha_ref.month, fecha_ref.day))

def calcular_hijos_fila(m_val, f_val):
    m_txt = str(m_val).strip()
    f_txt = str(f_val).strip()
    if m_txt == "" and f_txt == "":
        return ""
    m_num = int(float(m_txt)) if re.fullmatch(r"\d+(\.\d+)?", m_txt) else 0
    f_num = int(float(f_txt)) if re.fullmatch(r"\d+(\.\d+)?", f_txt) else 0
    return m_num + f_num

def calcular_alerta_reintegro(fecha_fin, estado_tramite, hoy):
    est = limpiar_valor(estado_tramite)
    if est == "FINALIZADO":
        return "REINCORPORADO"
    if est == "ANULADO":
        return "ANULADO"
    if not fecha_fin:
        return ""
    if fecha_fin < hoy:
        return "VENCIDO / VERIFICAR"
    if (fecha_fin - hoy).days <= 2:
        return "REINCORPORA PRONTO"
    return "EN CURSO"

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
        unsafe_allow_html=True,
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
        "CLL-104", "VIDEO SEGURIDAD", "DESPACHO",
    ]
    lista_turnos = ["SELECCIONAR", "4X4", "5X2", "7X7", "20X20", "24X24", "ROTATIVO", "ADMINISTRATIVO"]
    lista_sangre = ["SELECCIONAR", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    lista_provincias = [
        "SELECCIONAR", "PANAMÁ", "PANAMÁ OESTE", "COLÓN", "CHIRIQUÍ", "VERAGUAS",
        "COCLÉ", "HERRERA", "LOS SANTOS", "BOCAS DEL TORO", "DARIÉN",
        "COMARCA NGÄBE-BUGLÉ", "COMARCA GUNA YALA", "COMARCA EMBERÁ-WOUNAAN",
    ]
    lista_estados = [
        "SELECCIONAR", "ACTIVO", "INACTIVO", "VACACIONES",
        "VACACIONES POR JUBILACIONES", "TRASLADADOS", "PRESTADO", "ASIGNADO",
        "PENSIONADO", "INCAPACITADO",
    ]
    lista_estado_civil = ["SELECCIONAR", "SOLTERO/A", "CASADO/A", "UNIDO/A", "DIVORCIADO/A", "VIUDO/A"]
    lista_si_no = ["NO", "SÍ"]
    lista_select_si_no = ["SELECCIONAR", "SÍ", "NO"]

    # --- BARRA LATERAL (SIDEBAR) ---
    with st.sidebar:
        st.write(
            f"👤 Usuario: **{st.session_state.get('usuario_actual', 'Admin')}**"
        )

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
        modulo_activo = st.radio(
            "Seleccione un módulo:",
            [
                "➕ Registro Individual",
                "🔄 Movimiento de Unidades",
                "🩺 Permisos, Incapacidades y Licencias",
                "📊 Consulta de Bases de Datos",
            ],
            label_visibility="collapsed",
        )

        st.divider()
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    tz_pa = pytz.timezone("America/Panama")
    ahora_pa = datetime.now(tz_pa)
    hoy_pa = ahora_pa.date()
    timestamp_actual = ahora_pa.strftime("%Y-%m-%d %H:%M:%S")

    # ==========================================
    # MÓDULO 1: NUEVO REGISTRO INDIVIDUAL
    # ==========================================
    if modulo_activo == "➕ Registro Individual":
        st.markdown(
            "<h1 style='color: #00d4ff; text-shadow: 0 0 12px #00d4ff;'>➕ NUEVO REGISTRO DE PERSONAL</h1>",
            unsafe_allow_html=True,
        )

        with st.form("form_nuevo_registro_excel", clear_on_submit=True):
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 1. DATOS PERSONALES",
                "📍 2. FUNCIONES GENERALES",
                "⚡ 3. OPERATIVIDAD",
                "🏡 4. RESIDENCIAL / ACADÉMICO",
                "🎽 5. TALLAS",
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
                            usuario_reg = st.session_state.get("usuario_actual", "DESCONOCIDO")
                            edad_calc = calcular_anios(fecha_naci, hoy_pa)
                            anos_serv_calc = calcular_anios(fecha_ingreso, hoy_pa)
                            total_hijos_calc = calcular_hijos_fila(hijos_m, hijas_f)
                            f_diag_str = str(fecha_diagnostico) if tiene_diagnostico else ""
                            f_eval_str = str(f_prox_evaluacion) if tiene_diagnostico else ""

                            nueva_fila = [
                                timestamp_actual,
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
                                int(hijos_m) if int(hijos_m) > 0 else "",
                                int(hijas_f) if int(hijas_f) > 0 else "",
                                total_hijos_calc,
                                limpiar_valor(talla_camisa),
                                limpiar_valor(talla_pantalon),
                                limpiar_valor(talla_sueter),
                                limpiar_valor(talla_botas),
                                limpiar_valor(talla_zapatos),
                                limpiar_valor(talla_quepi),
                                limpiar_valor(talla_correa),
                            ]

                            hoja_bd = obtener_o_crear_worksheet(PESTANA_PERSONAL, COLUMNAS_OFICIALES)
                            hoja_bd.append_row(nueva_fila, value_input_option="USER_ENTERED")
                            ordenar_pestana_por_rango(PESTANA_PERSONAL)
                            leer_pestana_df.clear()

                            st.success(f"✔️ El elemento {limpiar_valor(rango)} {limpiar_valor(nombre)} {limpiar_valor(apellido)} con cédula {limpiar_valor(cedula)} ha sido registrado y ordenado jerárquicamente.")
                        except Exception as e:
                            st.error(f"❌ Ocurrió un error al guardar en la base de datos: {e}")

    # ==========================================
    # MÓDULO 2: MOVIMIENTO DINÁMICO DE UNIDADES ENTRE PESTAÑAS
    # ==========================================
    elif modulo_activo == "🔄 Movimiento de Unidades":
        st.markdown(
            "<h1 style='color: #00d4ff; text-shadow: 0 0 12px #00d4ff;'>🔄 MOVIMIENTO DINÁMICO DE UNIDADES</h1>",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="neon-card">', unsafe_allow_html=True)
        st.write(
            "Mueve unidades entre **`Plan_de_Recojo`**, **`Unidades_Agregadas`** y "
            "**`Vac.Jubilacion_U.Prestados_U.Trasladados`**. Cada vez que ingresa o retorna una unidad a "
            "**`Plan_de_Recojo`** o **`Unidades_Agregadas`**, la hoja se reordena automáticamente por **jerarquía de RANGO + POSIC**."
        )

        m_col1, m_col2 = st.columns(2)
        pestana_origen_sel = m_col1.selectbox(
            "1. Pestaña de Origen (donde está actualmente la unidad):",
            PESTANAS_UNIDADES,
            key="mov_origen",
        )

        destinos_posibles = [p for p in PESTANAS_UNIDADES if p != pestana_origen_sel]
        idx_dest_def = 0
        if pestana_origen_sel != PESTANA_JUB_PRES_TRAS and PESTANA_JUB_PRES_TRAS in destinos_posibles:
            idx_dest_def = destinos_posibles.index(PESTANA_JUB_PRES_TRAS)
        elif PESTANA_PERSONAL in destinos_posibles:
            idx_dest_def = destinos_posibles.index(PESTANA_PERSONAL)

        pestana_destino_sel = m_col2.selectbox(
            "2. Pestaña de Destino (a dónde pasará la unidad):",
            destinos_posibles,
            index=idx_dest_def,
            key="mov_destino",
        )

        df_origen_mov = leer_pestana_df(pestana_origen_sel, COLUMNAS_OFICIALES)

        if df_origen_mov.empty:
            st.warning(f"⚠️ La pestaña **`{pestana_origen_sel}`** no tiene registros disponibles.")
        else:
            filtro_busq_mov = st.text_input(
                "3. Buscar unidad por Cédula, Nombre, Apellido o Posición:",
                key="mov_buscar",
            ).strip().upper()

            df_candidatos = df_origen_mov.copy()
            if filtro_busq_mov:
                mask_m = (
                    df_candidatos["CEDULA"].str.upper().str.contains(filtro_busq_mov, na=False)
                    | df_candidatos["NOMBRE"].str.upper().str.contains(filtro_busq_mov, na=False)
                    | df_candidatos["APELLIDO"].str.upper().str.contains(filtro_busq_mov, na=False)
                    | df_candidatos["POSIC"].str.upper().str.contains(filtro_busq_mov, na=False)
                )
                df_candidatos = df_candidatos[mask_m]

            if df_candidatos.empty:
                st.info("No se encontraron unidades con ese criterio de búsqueda.")
            else:
                opciones_indices = list(df_candidatos.index)
                unidad_idx = st.selectbox(
                    "4. Selecciona la unidad a mover:",
                    opciones_indices,
                    format_func=lambda idx: (
                        f"{df_origen_mov.loc[idx, 'RANGO']} | POSIC: {df_origen_mov.loc[idx, 'POSIC']} | "
                        f"{df_origen_mov.loc[idx, 'NOMBRE']} {df_origen_mov.loc[idx, 'APELLIDO']} | "
                        f"CÉD: {df_origen_mov.loc[idx, 'CEDULA']} | "
                        f"ESTADO: {df_origen_mov.loc[idx, 'ESTADO_STATUS']}"
                    ),
                    key="mov_unidad_sel",
                )

                fila_sel = df_origen_mov.loc[unidad_idx]
                st.markdown("**Vista previa de la unidad seleccionada:**")
                st.dataframe(
                    pd.DataFrame([fila_sel[["RANGO", "POSIC", "NOMBRE", "APELLIDO", "CEDULA", "ESTAMENTO", "ASIGNADO_CENTRO", "DEPARTAMENTO", "ESTADO_STATUS"]]]),
                    use_container_width=True,
                )

                if pestana_destino_sel == PESTANA_JUB_PRES_TRAS:
                    estados_sugeridos = ["TRASLADADOS", "PRESTADO", "VACACIONES POR JUBILACIONES", "ASIGNADO"]
                else:
                    estados_sugeridos = ["ACTIVO", "ASIGNADO", "TRASLADADOS", "PRESTADO", "VACACIONES"]

                d_col1, d_col2, d_col3 = st.columns(3)
                estado_nuevo = d_col1.selectbox(
                    "5. Nuevo ESTADO_STATUS al mover:",
                    estados_sugeridos,
                    key="mov_nuevo_estado",
                )
                respaldo_doc = d_col2.text_input(
                    "Resolución / OGD / Respaldo (opcional):",
                    key="mov_respaldo",
                )
                nota_mov = d_col3.text_input(
                    "Motivo / Observación del movimiento (opcional):",
                    key="mov_obs",
                )

                if st.button(
                    f"🔄 Mover a {pestana_destino_sel} y quitar de {pestana_origen_sel}",
                    use_container_width=True,
                ):
                    try:
                        mover_unidad_entre_pestanas(
                            pestana_origen=pestana_origen_sel,
                            pestana_destino=pestana_destino_sel,
                            indice_df_origen=int(unidad_idx),
                            nuevo_estado_status=estado_nuevo,
                            usuario_actual=st.session_state.get("usuario_actual", "ADMINISTRADOR"),
                            timestamp_str=timestamp_actual,
                            respaldo_mov=respaldo_doc,
                            obs_adicional=nota_mov,
                        )
                        st.success(
                            f"✔️ Unidad **{fila_sel['NOMBRE']} {fila_sel['APELLIDO']}** (Cédula: `{fila_sel['CEDULA']}`) "
                            f"movida de **`{pestana_origen_sel}`** a **`{pestana_destino_sel}`** con estado **`{estado_nuevo}`**."
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al mover la unidad: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # MÓDULO 3: PERMISOS, INCAPACIDADES Y LICENCIAS (REGISTRO INDIVIDUAL)
    # ==========================================
    elif modulo_activo == "🩺 Permisos, Incapacidades y Licencias":
        st.markdown(
            "<h1 style='color: #00d4ff; text-shadow: 0 0 12px #00d4ff;'>🩺 CONTROL DE PERMISOS, INCAPACIDADES Y LICENCIAS</h1>",
            unsafe_allow_html=True,
        )

        with st.form("form_novedad_gerencial", clear_on_submit=True):
            st.markdown("<h3 style='color: #00d4ff;'>1. Identificación de la Unidad</h3>", unsafe_allow_html=True)
            n1, n2, n3, n4, n5, n6 = st.columns(6)
            nov_rango = n1.selectbox("RANGO *", lista_rangos)
            nov_posic = n2.text_input("POSIC")
            nov_nombre = n3.text_input("NOMBRE *")
            nov_apellido = n4.text_input("APELLIDO *")
            nov_cedula = n5.text_input("CÉDULA *")
            nov_estamento = n6.selectbox("ESTAMENTO", lista_estamentos)

            st.markdown("<h3 style='color: #00d4ff;'>2. Ubicación Operativa y Cobertura</h3>", unsafe_allow_html=True)
            u1, u2, u3, u4, u5, u6 = st.columns(6)
            nov_centro = u1.selectbox("ASIGNADO_CENTRO", lista_centros)
            nov_depto = u2.selectbox("DEPARTAMENTO", lista_departamentos)
            nov_turno = u3.selectbox("TURNO", lista_turnos)
            nov_grupo = u4.text_input("GRUPO")
            nov_funcion = u5.text_input("FUNCIÓN")
            nov_impacto = u6.selectbox(
                "IMPACTO_OPERATIVO",
                ["SIN AFECTACIÓN", "CUBIERTO POR GRUPO", "REQUIERE RELEVO", "CRÍTICO EN TURNO"],
            )

            st.markdown("<h3 style='color: #00d4ff;'>3. Detalle de Novedad y Respaldo Documental</h3>", unsafe_allow_html=True)
            d1, d2, d3, d4, d5 = st.columns(5)
            nov_tipo = d1.selectbox("TIPO_NOVEDAD *", ["PERMISO", "INCAPACIDAD", "LICENCIA"])
            nov_subtipo = d2.text_input("SUBTIPO_MOTIVO *")
            nov_f_inicio = d3.date_input("FECHA_INICIO *", value=hoy_pa)
            nov_f_fin = d4.date_input("FECHA_FIN *", value=hoy_pa)
            nov_estado = d5.selectbox("ESTADO_TRAMITE", ["VIGENTE", "FINALIZADO", "PRORROGADO", "ANULADO"])

            r1, r2, r3, r4 = st.columns(4)
            nov_doc = r1.text_input("NUM_DOCUMENTO_RESPALDO")
            nov_entidad = r2.text_input("ENTIDAD_EMISORA")
            nov_autorizado = r3.text_input("AUTORIZADO_POR")
            nov_obs = r4.text_input("OBSERVACION")

            guardar_nov = st.form_submit_button("💾 Registrar en Permiso,incapacidad,licencia", use_container_width=True)

            if guardar_nov:
                if not nov_nombre.strip() or not nov_apellido.strip() or not nov_cedula.strip() or nov_rango == "SELECCIONAR":
                    st.error("❌ Complete los campos obligatorios: Rango, Nombre, Apellido y Cédula.")
                elif nov_f_fin < nov_f_inicio:
                    st.error("❌ La FECHA_FIN no puede ser anterior a la FECHA_INICIO.")
                else:
                    try:
                        ws_nov = obtener_o_crear_worksheet(PESTANA_NOVEDADES, COLUMNAS_NOVEDADES)
                        filas_existentes = len(ws_nov.get_all_values())
                        correlativo = max(1, filas_existentes)
                        id_nov = f"NOV-{hoy_pa.year}-{correlativo:03d}"

                        dias_totales = int((nov_f_fin - nov_f_inicio).days + 1)
                        dias_restantes = int(max(0, (nov_f_fin - hoy_pa).days))
                        alerta_reint = calcular_alerta_reintegro(nov_f_fin, nov_estado, hoy_pa)
                        usuario_reg = st.session_state.get("usuario_actual", "ADMINISTRADOR")

                        fila_nov = [
                            id_nov,
                            timestamp_actual,
                            limpiar_valor(usuario_reg),
                            limpiar_valor(nov_rango),
                            limpiar_valor(nov_posic),
                            limpiar_valor(nov_nombre),
                            limpiar_valor(nov_apellido),
                            limpiar_valor(nov_cedula),
                            limpiar_valor(nov_estamento),
                            limpiar_valor(nov_centro),
                            limpiar_valor(nov_depto),
                            limpiar_valor(nov_turno),
                            limpiar_valor(nov_grupo),
                            limpiar_valor(nov_funcion),
                            limpiar_valor(nov_impacto),
                            limpiar_valor(nov_tipo),
                            limpiar_valor(nov_subtipo),
                            str(nov_f_inicio),
                            str(nov_f_fin),
                            dias_totales,
                            dias_restantes,
                            limpiar_valor(nov_estado),
                            alerta_reint,
                            limpiar_valor(nov_doc),
                            limpiar_valor(nov_entidad),
                            limpiar_valor(nov_autorizado),
                            limpiar_valor(nov_obs),
                        ]

                        ws_nov.append_row(fila_nov, value_input_option="USER_ENTERED")
                        leer_pestana_df.clear()
                        st.success(f"✔️ Registro **{id_nov}** ({limpiar_valor(nov_tipo)}) guardado en **`{PESTANA_NOVEDADES}`** ({dias_totales} días).")
                    except Exception as e:
                        st.error(f"❌ Error al guardar en `{PESTANA_NOVEDADES}`: {e}")

    # ==========================================
    # MÓDULO 4: CONSULTA COMPLETA DE BASES DE DATOS (2 PESTAÑAS PRINCIPALES)
    # ==========================================
    elif modulo_activo == "📊 Consulta de Bases de Datos":
        col_tit, col_btn = st.columns([5, 1])
        with col_tit:
            st.markdown(
                "<h1 style='color: #00d4ff; text-shadow: 0 0 12px #00d4ff;'>📊 CONSULTA GENERAL DE BASES DE DATOS</h1>",
                unsafe_allow_html=True,
            )
        with col_btn:
            st.write("")
            if st.button("🔄 Actualizar Datos", use_container_width=True):
                leer_pestana_df.clear()
                st.rerun()

        tab_bd_personal, tab_bd_novedades = st.tabs([
            "🗂️ 1. BASE DE DATOS DE PERSONAL (3 PESTAÑAS)",
            "🩺 2. PERMISOS, INCAPACIDADES Y LICENCIAS",
        ])

        with tab_bd_personal:
            sub_tab_1, sub_tab_2, sub_tab_3 = st.tabs([
                "👮 Plan_de_Recojo",
                "⚓ Unidades_Agregadas",
                "📋 Vac.Jubilacion_U.Prestados_U.Trasladados",
            ])

            def renderizar_visor_personal(nombre_hoja, key_prefix):
                df_p = leer_pestana_df(nombre_hoja, COLUMNAS_OFICIALES)
                if df_p.empty:
                    st.info(f"La pestaña **{nombre_hoja}** aún no tiene registros.")
                    return

                st.markdown('<div class="neon-card">', unsafe_allow_html=True)
                f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
                busqueda = f1.text_input(
                    "🔎 Buscar por Cédula, Nombre, Apellido o Posición:",
                    key=f"{key_prefix}_busq",
                ).strip().upper()

                ests_disp = ["TODOS"] + sorted([x for x in df_p["ESTAMENTO"].unique() if str(x).strip() != ""])
                filtro_est = f2.selectbox("Estamento:", ests_disp, key=f"{key_prefix}_est")

                centros_disp = ["TODOS"] + sorted([x for x in df_p["ASIGNADO_CENTRO"].unique() if str(x).strip() != ""])
                filtro_cen = f3.selectbox("Centro:", centros_disp, key=f"{key_prefix}_cen")

                status_disp = ["TODOS"] + sorted([x for x in df_p["ESTADO_STATUS"].unique() if str(x).strip() != ""])
                filtro_sta = f4.selectbox("Estado / Status:", status_disp, key=f"{key_prefix}_sta")

                df_filtrado = df_p.copy()
                if busqueda:
                    mask_b = (
                        df_filtrado["CEDULA"].str.upper().str.contains(busqueda, na=False)
                        | df_filtrado["NOMBRE"].str.upper().str.contains(busqueda, na=False)
                        | df_filtrado["APELLIDO"].str.upper().str.contains(busqueda, na=False)
                        | df_filtrado["POSIC"].str.upper().str.contains(busqueda, na=False)
                    )
                    df_filtrado = df_filtrado[mask_b]
                if filtro_est != "TODOS":
                    df_filtrado = df_filtrado[df_filtrado["ESTAMENTO"] == filtro_est]
                if filtro_cen != "TODOS":
                    df_filtrado = df_filtrado[df_filtrado["ASIGNADO_CENTRO"] == filtro_cen]
                if filtro_sta != "TODOS":
                    df_filtrado = df_filtrado[df_filtrado["ESTADO_STATUS"] == filtro_sta]

                c_info, c_dl = st.columns([4, 1])
                c_info.markdown(
                    f"**Pestaña:** `{nombre_hoja}` · **Mostrando:** `{len(df_filtrado)}` de `{len(df_p)}` registros completos (60 columnas)"
                )
                c_dl.download_button(
                    label="📥 Descargar Excel",
                    data=convertir_df_a_excel(df_filtrado, nombre_hoja),
                    file_name=f"{nombre_hoja}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key=f"{key_prefix}_dl",
                )

                st.dataframe(df_filtrado, use_container_width=True, height=520)
                st.markdown("</div>", unsafe_allow_html=True)

            with sub_tab_1:
                renderizar_visor_personal(PESTANA_PERSONAL, "recojo")

            with sub_tab_2:
                renderizar_visor_personal(PESTANA_AGREGADAS, "agregadas")

            with sub_tab_3:
                renderizar_visor_personal(PESTANA_JUB_PRES_TRAS, "jub_pres_tras")

        with tab_bd_novedades:
            df_nov = leer_pestana_df(PESTANA_NOVEDADES, COLUMNAS_NOVEDADES)
            st.markdown('<div class="neon-card">', unsafe_allow_html=True)

            if df_nov.empty:
                st.info(
                    f"La pestaña **`{PESTANA_NOVEDADES}`** aún no tiene registros cargados. "
                    "Puedes agregarlos desde el módulo **🩺 Permisos, Incapacidades y Licencias**."
                )
            else:
                fn1, fn2, fn3, fn4 = st.columns([2, 1, 1, 1])
                busq_nov = fn1.text_input(
                    "🔎 Buscar por Cédula, Nombre, Apellido, Posición o ID:",
                    key="nov_busq",
                ).strip().upper()

                tipos_disp = ["TODOS"] + sorted([x for x in df_nov["TIPO_NOVEDAD"].unique() if str(x).strip() != ""])
                filtro_tipo_nov = fn2.selectbox("Tipo de Novedad:", tipos_disp, key="nov_tipo_f")

                cen_nov_disp = ["TODOS"] + sorted([x for x in df_nov["ASIGNADO_CENTRO"].unique() if str(x).strip() != ""])
                filtro_cen_nov = fn3.selectbox("Centro:", cen_nov_disp, key="nov_cen_f")

                est_nov_disp = ["TODOS"] + sorted([x for x in df_nov["ESTADO_TRAMITE"].unique() if str(x).strip() != ""])
                filtro_est_nov = fn4.selectbox("Estado Trámite:", est_nov_disp, key="nov_est_f")

                df_nov_filt = df_nov.copy()
                if busq_nov:
                    mask_n = (
                        df_nov_filt["CEDULA"].str.upper().str.contains(busq_nov, na=False)
                        | df_nov_filt["NOMBRE"].str.upper().str.contains(busq_nov, na=False)
                        | df_nov_filt["APELLIDO"].str.upper().str.contains(busq_nov, na=False)
                        | df_nov_filt["POSIC"].str.upper().str.contains(busq_nov, na=False)
                        | df_nov_filt["ID_NOVEDAD"].str.upper().str.contains(busq_nov, na=False)
                    )
                    df_nov_filt = df_nov_filt[mask_n]
                if filtro_tipo_nov != "TODOS":
                    df_nov_filt = df_nov_filt[df_nov_filt["TIPO_NOVEDAD"] == filtro_tipo_nov]
                if filtro_cen_nov != "TODOS":
                    df_nov_filt = df_nov_filt[df_nov_filt["ASIGNADO_CENTRO"] == filtro_cen_nov]
                if filtro_est_nov != "TODOS":
                    df_nov_filt = df_nov_filt[df_nov_filt["ESTADO_TRAMITE"] == filtro_est_nov]

                cn_info, cn_dl = st.columns([4, 1])
                cn_info.markdown(
                    f"**Pestaña:** `{PESTANA_NOVEDADES}` · **Mostrando:** `{len(df_nov_filt)}` de `{len(df_nov)}` registros (27 columnas)"
                )
                cn_dl.download_button(
                    label="📥 Descargar Excel",
                    data=convertir_df_a_excel(df_nov_filt, "Permisos_Incapacidades"),
                    file_name="Permiso_incapacidad_licencia.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="nov_dl",
                )

                st.dataframe(df_nov_filt, use_container_width=True, height=520)

            st.markdown("</div>", unsafe_allow_html=True)
