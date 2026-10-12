from datetime import date, datetime
import base64
import glob
import folium
import pandas as pd
import pytz
import streamlit as st
from streamlit_folium import st_folium

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

# --- 2. ESTADOS DE SESIÓN ---
if "autenticado" not in st.session_state:
  st.session_state.autenticado = False
if "modo_pantalla" not in st.session_state:
  st.session_state.modo_pantalla = "DASHBOARD OPERATIVO"


def obtener_indice(lista, valor):
  try:
    return lista.index(valor)
  except ValueError:
    return 0


# --- 3. PANTALLA DE LOGIN CON ESTILO NEÓN ---
def pantalla_login():
  st.markdown(
      "<h1 style='text-align: center; color: #00d4ff; text-shadow: 0 0 15px"
      " #00d4ff;'>🔐 RECURSOS HUMANOS - C.O.N</h1>",
      unsafe_allow_html=True,
  )
  st.markdown('<p class="author-text">Desarrollado por: CABO 1RO ELMER RODRIGUEZ</p>', unsafe_allow_html=True)

  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    st.markdown(
        "<div style='background: rgba(10, 15, 25, 0.88); padding: 35px;"
        " border-radius: 15px; border: 2px solid #00d4ff; box-shadow: 0 0 30px"
        " rgba(0, 212, 255, 0.6);'>",
        unsafe_allow_html=True,
    )

    usuarios_permitidos = {
        "ADMINISTRADOR": "CONC505",
        "LORENZO BOWEN": "10924",
        "MIRNA RIVERA": "20146",
        "ALISJHON": "199432",
        "ALBERTO AYALA": "24561",
        "DANILO SMITH": "49431",
    }

    user = st.text_input("👤 Usuario institucional")
    password = st.text_input("🔑 Contraseña", type="password")

    if st.button("Iniciar Sesión", use_container_width=True):
      if user in usuarios_permitidos and usuarios_permitidos[user] == password:
        st.session_state.autenticado = True
        st.session_state.usuario_actual = user
        st.success(f"¡Bienvenido, {user}!")
        st.rerun()
      else:
        st.error("❌ Usuario o contraseña incorrectos")

    st.markdown("</div>", unsafe_allow_html=True)


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
      "SELECCIONAR",
      "COMISIONADO",
      "SUBCOMISIONADO",
      "MAYOR",
      "CAPITÁN",
      "TENIENTE",
      "SUBTENIENTE",
      "SARGENTO 1º",
      "SARGENTO 2º",
      "CABO 1º",
      "CABO 2º",
      "AGENTE",
      "MNJ",
  ]
  lista_estamentos = ["SELECCIONAR", "P.N", "SENAFRONT", "SENAN", "MINSEG", "MNJ"]
  lista_departamentos = [
      "SELECCIONAR",
      "DIRECCION",
      "SUPERVISORA ADM",
      "PLANEAMIENTO",
      "COOR. TECNOLOGICO",
      "OPERACIONES",
      "ESTADISTICA",
      "RECURSOS HUMANOS",
  ]
  lista_turnos = ["SELECCIONAR", "5X2", "24X24", "ROTATIVO", "ADMINISTRATIVO"]
  lista_sangre = [
      "SELECCIONAR",
      "A+",
      "A-",
      "B+",
      "B-",
      "AB+",
      "AB-",
      "O+",
      "O-",
  ]
  lista_provincias = [
      "SELECCIONAR",
      "PANAMÁ",
      "PANAMÁ OESTE",
      "COLÓN",
      "CHIRIQUÍ",
      "VERAGUAS",
      "COCLÉ",
      "HERRERA",
      "LOS SANTOS",
      "BOCAS DEL TORO",
      "DARIÉN",
  ]

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
        "<h1 style='color: #00d4ff; text-shadow: 0 0 12px"
        " #00d4ff;'>📊 DASHBOARD OPERATIVO - CON</h1>",
        unsafe_allow_html=True,
    )

    col_dash1, col_dash2 = st.columns([2, 1])

    with col_dash1:
      st.markdown(
          "<h3 style='color: #00d4ff;'>🏢 Distribución por Centros y"
          " Estamentos</h3>",
          unsafe_allow_html=True,
      )
      tabla_centros_estamentos = pd.DataFrame(
          {
              "ESTAMENTO / CENTRO": [
                  "CON",
                  "CORCOL",
                  "COMCH",
                  "COMDA",
                  "COMAR",
                  "COMSAM",
                  "COMCHEP",
                  "CEVIBO",
                  "TOTAL VERTICAL",
              ],
              "PNP": [0, 0, 0, 0, 0, 0, 0, 0, 0],
              "SENAN": [0, 0, 0, 0, 0, 0, 0, 0, 0],
              "SENAFRONT": [0, 0, 0, 0, 0, 0, 0, 0, 0],
              "MINSEG": [0, 0, 0, 0, 0, 0, 0, 0, 0],
              "MNJ": [0, 0, 0, 0, 0, 0, 0, 0, 0],
              "TOTAL HORIZONTAL": [0, 0, 0, 0, 0, 0, 0, 0, 0],
          }
      )
      st.dataframe(tabla_centros_estamentos, use_container_width=True)

    with col_dash2:
      st.markdown(
          "<h3 style='color: #00d4ff;'>⚡ Parte de Operatividad</h3>",
          unsafe_allow_html=True,
      )
      tabla_operatividad = pd.DataFrame(
          {
              "ESTATUS OPERATIVO": [
                  "OPERATIVO",
                  "NO OPERATIVO",
                  "ORDENES A.COMP",
                  "ORDENES DRP",
                  "MNJ",
                  "TOTAL",
              ],
              "CANTIDAD": [0, 0, 0, 0, 0, 0],
          }
      )
      st.dataframe(tabla_operatividad, use_container_width=True)

    st.markdown("---")
    st.markdown(
        "<h3 style='color: #00d4ff;'>🎖️ Total de Unidades por Rango y"
        " Centros</h3>",
        unsafe_allow_html=True,
    )
    tabla_rangos_centros = pd.DataFrame(
        {
            "RANGO / CENTRO": [
                "COMISIONADO",
                "SUBCOMISIONADO",
                "MAYOR",
                "CAPITÁN",
                "TENIENTE",
                "SUBTENIENTE",
                "SARGENTO 1º",
                "SARGENTO 2º",
                "CABO 1º",
                "CABO 2º",
                "AGENTE",
                "MNJ",
                "TOTAL VERTICAL",
            ],
            "CON": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "CORCOL": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "COMCH": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "COMDA": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "COMAR": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "COMSAM": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "COMCHEP": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "CEVIBO": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "TOTAL HORIZONTAL": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
    )
    st.dataframe(tabla_rangos_centros, use_container_width=True)

  # ==========================================
  # OPCIÓN 2: NUEVO REGISTRO (CONFIGURADO TAL CUAL LA BASE DE DATOS)
  # ==========================================
  elif st.session_state.modo_pantalla == "NUEVO REGISTRO":
    st.markdown(
        "<h1 style='color: #00d4ff; text-shadow: 0 0 12px"
        " #00d4ff;'>➕ NUEVO REGISTRO DE PERSONAL</h1>",
        unsafe_allow_html=True,
    )

    with st.form("form_nuevo_registro_excel", clear_on_submit=False):

      # SECCIÓN 1: DATOS PERSONALES
      st.subheader("📋 1. DATOS PERSONALES")
      c1, c2, c3, c4, c5 = st.columns(5)
      rango = c1.selectbox("RANGO", lista_rangos)
      posic = c2.text_input("POSIC")
      placa_metalica = c3.text_input("Nº PLACA METÁLICA")
      nombre = c4.text_input("NOMBRE")
      apellido = c5.text_input("APELLIDO")

      c6, c7, c8, c9, c10 = st.columns(5)
      cedula = c6.text_input("Nº CÉDULA")
      fecha_naci = c7.date_input("FECHA DE NACIMIENTO")
      edad = c8.number_input("EDAD", min_value=0, step=1)
      genero = c9.selectbox("GÉNERO", ["SELECCIONAR", "M", "F"])
      telefono_personal = c10.text_input("TELÉFONO PERSONAL")

      c11, c12, c13, c14, c15 = st.columns(5)
      estamento = c11.selectbox("ESTAMENTO", lista_estamentos)
      num_promocion = c12.text_input("Nº PROMOCIÓN")
      descripcion_promo = c13.text_input("DESCRIPCIÓN PROMOCIÓN")
      fecha_ingreso = c14.date_input("FECHA DE INGRESO")
      anos_servicios = c15.number_input("AÑOS DE SERVICIOS", min_value=0, step=1)

      # SECCIÓN 2: FUNCIONES GENERALES
      st.subheader("📍 2. FUNCIONES GENERALES")
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
      estado_status = f10.selectbox(
          "ESTADO O STATUS",
          [
              "SELECCIONAR",
              "ACTIVO",
              "INACTIVO",
              "VACACIONES",
              "PENSIONADO",
              "INCAPACITADO",
          ],
      )

      # SECCIÓN 3: TIPO DE OPERATIVIDAD Y DIAGNÓSTICO
      st.subheader("⚡ 3. TIPO DE OPERATIVIDAD Y DIAGNÓSTICO")
      o1, o2, o3, o4, o5 = st.columns(5)
      operat_no_operat = o1.selectbox(
          "OPERAT, NO OPERATIVO", ["SELECCIONAR", "OPERATIVO", "NO OPERATIVO"]
      )
      perm_temp = o2.selectbox("PERM./TEMP.", ["SELECCIONAR", "PERM", "TEMP"])
      condicion = o3.text_input("CONDICIÓN")
      apto_no_apto = o4.selectbox(
          "APTO - NO APTO", ["SELECCIONAR", "APTO", "NO APTO"]
      )
      nivel_salud = o5.text_input("NIVEL")

      o6, o7, o8, o9, o10 = st.columns(5)
      observacion = o6.text_input("OBSERVACIÓN")
      cert_buena_salud = o7.selectbox(
          "CERT. BUENA SALUD ACT.", ["SELECCIONAR", " SÍ", "NO"]
      )
      fecha_diagnostico = o8.date_input("FECHA DIAGNÓSTICO")
      f_prox_evaluacion = o9.date_input("F. PROX. EVALUACIÓN")
      salud_ocupacional = o10.text_input("SALUD OCUPACIONAL")

      pensionado_opt = st.selectbox("PENSIONADO", ["NO", "SÍ"])

      # SECCIÓN 4: INFORMACIÓN RESIDENCIAL, FAMILIAR Y ACADÉMICO
      st.subheader("🏡 4. INFORMACIÓN RESIDENCIAL, FAMILIAR Y ACADÉMICO")
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
      estado_civil = r9.selectbox(
          "ESTADO CIVIL",
          ["SELECCIONAR", "SOLTERO/A", "CASADO/A", "DIVORCIADO/A", "VIUDO/A"],
      )
      donante_sangre = r10.selectbox("DONANTE DE SANGRE", ["NO", "SÍ"])

      r11, r12, r13, r14, r15 = st.columns(5)
      secundaria = r11.text_input("SECUNDARIA")
      universidad = r12.text_input("UNIVERSIDAD")
      hijos_m = r13.number_input("HIJOS M", min_value=0, step=1)
      hijas_f = r14.number_input("HIJAS F", min_value=0, step=1)
      total_hijos = r15.number_input("TOTAL DE HIJO", min_value=0, step=1)

      # SECCIÓN 5: TALLAS DE UNIFORME Y OTROS
      st.subheader("🎽 5. TALLAS DE UNIFORME Y OTROS")
      t1, t2, t3, t4, t5 = st.columns(5)
      talla_camisa = t1.text_input("CAMISA")
      talla_pantalon = t2.text_input("PANTALÓN")
      talla_sueter = t3.text_input("SUÉTER")
      talla_botas = t4.text_input("BOTAS")
      talla_zapatos = t5.text_input("ZAPATOS")

      t6, t7 = st.columns(2)
      talla_quepi = t6.text_input("QUÉPI")
      talla_correa = t7.text_input("CORREA")

      st.divider()
      submitted_excel = st.form_submit_button(
          "Guardar Registro Oficial de Personal"
      )

      if submitted_excel:
        if not nombre or not apellido or not cedula or rango == "SELECCIONAR":
          st.error(
              "❌ Por favor complete los campos obligatorios principales"
              " (Rango, Nombre, Apellido y Cédula)."
          )
        else:
          st.success(
              f"✔️ El elemento {rango} {nombre} {apellido} con cédula {cedula}"
              " ha sido registrado exitosamente con todos sus datos"
              " institucionales."
          )

  # ==========================================
  # OPCIÓN 3: CONSULTA DE UNIDAD
  # ==========================================
  elif st.session_state.modo_pantalla == "CONSULTA DE UNIDAD":
    st.markdown(
        "<h1 style='color: #00d4ff; text-shadow: 0 0 12px"
        " #00d4ff;'>🔍 CONSULTA DE UNIDAD</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p>Busque la información de un elemento ingresando su número de"
        " Cédula o Apellido.</p>",
        unsafe_allow_html=True,
    )

    c_busq1, c_busq2 = st.columns([2, 1])
    with c_busq1:
      busqueda = st.text_input("Ingrese Cédula o Apellido a consultar:")
    with c_busq2:
      st.markdown("<br>", unsafe_allow_html=True)
      buscar_btn = st.button("Buscar Elemento", use_container_width=True)

    if buscar_btn and busqueda.strip():
      st.info(f"Resultados de búsqueda para: **{busqueda}**")

  # ==========================================
  # OPCIÓN 4: REGISTRO DE INCAPACIDAD, PERMISO, ETC.
  # ==========================================
  elif st.session_state.modo_pantalla == "INCAPACIDAD_PERMISO":
    st.markdown(
        "<h1 style='color: #00d4ff; text-shadow: 0 0 12px"
        " #00d4ff;'>📝 REGISTRO DE INCAPACIDADES Y PERMISOS</h1>",
        unsafe_allow_html=True,
    )

    with st.form("form_incapacidades", clear_on_submit=False):
      st.subheader("📌 Detalles de la Novedad o Ausencia")
      col_inc1, col_inc2 = st.columns(2)
      cedula_unidad = col_inc1.text_input("Cédula de la Unidad")
      tipo_novedad = col_inc2.selectbox(
          "TIPO DE NOVEDAD",
          [
              "SELECCIONAR",
              "INCAPACIDAD MÉDICA",
              "PERMISO PERSONAL",
              "VACACIONES",
              "LICENCIA",
              "SUSPENSIÓN",
          ],
      )

      col_inc3, col_inc4 = st.columns(2)
      f_inicio = col_inc3.date_input("FECHA DE INICIO")
      f_fin = col_inc4.date_input("FECHA DE FIN")

      observacion_inc = st.text_area("OBSERVACIONES / DIAGNÓSTICO / DETALLES")

      st.divider()
      btn_guardar_inc = st.form_submit_button("Registrar Novedad")

      if btn_guardar_inc:
        if tipo_novedad == "SELECCIONAR" or not cedula_unidad.strip():
          st.error(
              "❌ Debe ingresar la cédula y seleccionar el tipo de novedad."
          )
        else:
          st.success(
              f"✔️ Novedad ({tipo_novedad}) registrada con éxito para la cédula"
              f" {cedula_unidad}."
          )

  # ==========================================
  # OPCIÓN 5: UNIDADES TRASLADADAS
  # ==========================================
  elif st.session_state.modo_pantalla == "UNIDADES_TRASLADADAS":
    st.markdown(
        "<h1 style='color: #00d4ff; text-shadow: 0 0 12px"
        " #00d4ff;'>🔄 UNIDADES TRASLADADAS</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p>Listado completo de unidades que registran movimientos, asignaciones"
        " o traslados entre centros y dependencias.</p>",
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
    st.info(
        "ℹ️ Aquí se visualizarán todos los datos detallados de las unidades"
        " trasladadas."
    )
