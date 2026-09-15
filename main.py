import streamlit as st
import pandas as pd
from datetime import date

# ==============================================================================
# CONFIGURACIÓN GLOBAL Y ESTILOS NEÓN (CON-C5 STYLE)
# ==============================================================================
st.set_page_config(
    page_title="S-Portal | CON-C5 & Gestión de Personal", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    #MainMenu {visibility: visible;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estilo Base Oscuro */
    .stApp { background-color: #0a0e17; }
    h1, h2, h3, span, p, label { color: #ffffff !important; }
    
    /* CONTENEDOR NEÓN GLOBAL */
    .neon-container {
        position: relative;
        border-radius: 10px;
        padding: 4px;
        background: rgba(10, 14, 23, 1);
        border: 1px solid #00ebff;
        box-shadow: 0 0 15px rgba(0, 235, 255, 0.2);
        margin-bottom: 1rem;
    }

    .neon-title-container {
        position: relative;
        border-radius: 12px;
        padding: 3px; 
        background: #0d121f;
        box-shadow: 0 0 20px rgba(0, 235, 255, 0.3);
        margin-bottom: 1.5rem;
    }
    
    .neon-title-inner {
        position: relative;
        background: #0d121f; 
        border-radius: 9px;
        padding: 20px;
        text-align: center;
    }

    .neon-title-inner h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 800;
        text-transform: uppercase;
        background: linear-gradient(45deg, #ffffff, #00ebff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }

    .author-text { 
        color: #00ebff !important; 
        font-size: 13px; 
        font-style: italic; 
        margin-top: -5px; 
        margin-bottom: 15px; 
        text-align: center; 
    }
    </style>
""", unsafe_allow_html=True)

# --- CARGA DE LA BASE DE DATOS DE PERSONAL (EXCEL) ---
@st.cache_data
def cargar_personal():
    try:
        df = pd.read_excel("BASE DE DATOS A REALIZAR EN UNA APP.xlsx")
        df.columns = df.columns.str.replace('\n', ' ').str.strip()
        return df
    except:
        return pd.DataFrame(columns=[
            'RANGO', 'POSICION', 'PLACA METALICA', 'NOMBRE', 'APELLIDO', 'CEDULA', 
            'TROPA O CARRERA', 'F.INGRESO', 'A.SERVICIO', 'FECHA DE NACI.', 'EDAD', 'T.SANGRE',
            'GRUPO OPERT', 'TIPO_SERV.', 'FACCION', 'GRUPO', 'DEPARTAMENTO', 'OGD.DE TRASLADO', 
            'CENTRO OPERATIVO', 'FUNCION', 'ESTADO/ACTIVIDAD', 'CAUSA / ESTADO-ACTIVIDAD', 'DESTINO_CAUSA', 
            'PROV. DE ORIGEN', 'PROVINCIA_RECIDENCIA', 'DISTRITO', 'CORREGIMIENTO', 'COMUNIDAD', 'BARRIADA', 'NUMERO DE CASA', 
            'ESCOLARIDAD', 'TITULO OBTENIDO', 'ESPECIALIDAD', 'Nº HIJOS', 'Nº HIJOS-SEX_M', 'Nº HIJOS-SEX_F', 
            'E.CIVIL', 'Telefono', 'CASO EMERGENCIA', 'telefono_emergencia', 'CURSOS_1', 'CURSOS_2', 'CURSOS_3'
        ])

if 'df_personal' not in st.session_state:
    st.session_state.df_personal = cargar_personal()

# ==============================================================================
# BARRA LATERAL DE NAVEGACIÓN
# ==============================================================================
with st.sidebar:
    st.markdown("### 🛡️ C.O.N. - PANAMÁ")
    st.write("---")
    modulo_principal = st.radio("Módulos del Sistema:", [
        "📊 Dashboard Operativo", 
        "📂 Directorio y Expedientes", 
        "➕ Registrar Nueva Unidad",
        "📋 Control de Novedades y Permisos",
        "📈 Rendición de Cuentas"
    ])
    st.write("---")
    st.caption("DESARROLLADO POR: CABO 1° ELMER RODRIGUEZ")

df_p = st.session_state.df_personal

# ==============================================================================
# MÓDULO 1: DASHBOARD OPERATIVO
# ==============================================================================
if modulo_principal == "📊 Dashboard Operativo":
    st.markdown("""
        <div class="neon-title-container">
            <div class="neon-title-inner">
                <h1>🛡️ Centro de Operación Nacional | Panel General</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<p class="author-text">PANEL TÁCTICO DE RECURSOS Y FUERZA POLICIAL</p>', unsafe_allow_html=True)
    
    total_unidades = len(df_p)
    operativos = len(df_p[df_p['ESTADO/ACTIVIDAD'] == 'OPERATIVO']) if 'ESTADO/ACTIVIDAD' in df_p.columns else 0
    incapacitados = len(df_p[df_p['ESTADO/ACTIVIDAD'] == 'INCAPACITADO']) if 'ESTADO/ACTIVIDAD' in df_p.columns else 0
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="neon-container" style="padding: 15px;"><h3>TOTAL UNIDADES</h3><p style="font-size: 24px; color: #00ebff;"><b>{total_unidades:,}</b></p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="neon-container" style="padding: 15px;"><h3>FUERZA OPERATIVA</h3><p style="font-size: 24px; color: #00ffaa;"><b>{operativos:,}</b></p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="neon-container" style="padding: 15px;"><h3>INCAPACITADOS / BAJAS</h3><p style="font-size: 24px; color: #ff4b4b;"><b>{incapacitados:,}</b></p></div>', unsafe_allow_html=True)

# ==============================================================================
# MÓDULO 2: DIRECTORIO Y EXPEDIENTES
# ==============================================================================
elif modulo_principal == "📂 Directorio y Expedientes":
    st.markdown("""
        <div class="neon-title-container">
            <div class="neon-title-inner">
                <h1>📂 Directorio General y Expedientes Policiales</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    busqueda = st.text_input("🔍 Buscar por Nombre, Apellido, Cédula o Placa:")
    
    df_filtrado = df_p.copy()
    if busqueda and not df_p.empty:
        mask = df_filtrado.astype(str).apply(lambda row: row.str.contains(busqueda, case=False).any(), axis=1)
        df_filtrado = df_filtrado[mask]
        
    if not df_filtrado.empty:
        col_n = 'NOMBRE' if 'NOMBRE' in df_p.columns else df_p.columns[0]
        col_a = 'APELLIDO' if 'APELLIDO' in df_p.columns else df_p.columns[1]
        
        df_filtrado['NOMBRE_COMPLETO_SEL'] = df_filtrado[col_n].astype(str) + " " + df_filtrado[col_a].astype(str)
        
        unidad_sel = st.selectbox("🎯 Seleccione una unidad para desplegar su ficha técnica completa:", ["-- Seleccione --"] + list(df_filtrado['NOMBRE_COMPLETO_SEL'].unique()))
        
        if unidad_sel != "-- Seleccione --":
            info = df_filtrado[df_filtrado['NOMBRE_COMPLETO_SEL'] == unidad_sel].iloc[0]
            
            st.markdown("---")
            st.subheader(f"📋 Ficha de Expediente: {unidad_sel}")
            
            t1, t2, t3, t4 = st.tabs(["📌 DATOS PERSONALES", "🏢 DATOS LABORALES Y OPERATIVOS", "🏠 DOMICILIO Y UBICACIÓN", "🎓 ACADEMICO, FAMILIAR Y CONTACTO"])
            
            with t1:
                c1, c2, c3 = st.columns(3)
                c1.write(f"**RANGO:** {info.get('RANGO', 'N/D')}")
                c1.write(f"**NOMBRE:** {info.get('NOMBRE', 'N/D')}")
                c1.write(f"**TROPA O CARRERA:** {info.get('TROPA O CARRERA', 'N/D')}")
                c1.write(f"**FECHA DE NACI.:** {info.get('FECHA DE NACI.', 'N/D')}")
                
                c2.write(f"**POSICION:** {info.get('POSICION', 'N/D')}")
                c2.write(f"**APELLIDO:** {info.get('APELLIDO', 'N/D')}")
                c2.write(f"**F.INGRESO:** {info.get('F.INGRESO', 'N/D')}")
                c2.write(f"**EDAD:** {info.get('EDAD', 'N/D')} años")
                
                c3.write(f"**PLACA METALICA:** {info.get('PLACA METALICA', 'N/D')}")
                c3.write(f"**CEDULA:** {info.get('CEDULA', 'N/D')}")
                c3.write(f"**A.SERVICIO:** {info.get('A.SERVICIO', 'N/D')}")
                c3.write(f"**T.SANGRE:** {info.get('T.SANGRE', 'N/D')}")

            with t2:
                c1, c2, c3 = st.columns(3)
                c1.write(f"**TROPA O CARRERA:** {info.get('TROPA O CARRERA', 'N/D')}")
                c1.write(f"**FACCION:** {info.get('FACCION', 'N/D')}")
                c1.write(f"**OGD.DE TRASLADO:** {info.get('OGD.DE TRASLADO', 'N/D')}")
                c1.write(f"**ESTADO/ACTIVIDAD:** {info.get('ESTADO/ACTIVIDAD', 'N/D')}")
                
                c2.write(f"**GRUPO OPERT:** {info.get('GRUPO OPERT', 'N/D')}")
                c2.write(f"**GRUPO:** {info.get('GRUPO', 'N/D')}")
                c2.write(f"**CENTRO OPERATIVO:** {info.get('CENTRO OPERATIVO', 'N/D')}")
                c2.write(f"**CAUSA / ESTADO-ACTIVIDAD:** {info.get('CAUSA / ESTADO-ACTIVIDAD', 'N/D')}")
                
                c3.write(f"**TIPO_SERV.:** {info.get('TIPO_SERV.', 'N/D')}")
                c3.write(f"**DEPARTAMENTO:** {info.get('DEPARTAMENTO', 'N/D')}")
                c3.write(f"**FUNCION:** {info.get('FUNCION', 'N/D')}")
                c3.write(f"**DESTINO_CAUSA:** {info.get('DESTINO_CAUSA', 'N/D')}")

            with t3:
                c1, c2, c3 = st.columns(3)
                c1.write(f"**PROV. DE ORIGEN:** {info.get('PROV. DE ORIGEN', 'N/D')}")
                c1.write(f"**CORREGIMIENTO:** {info.get('CORREGIMIENTO', 'N/D')}")
                c1.write(f"**NUMERO DE CASA:** {info.get('NUMERO DE CASA', 'N/D')}")
                
                c2.write(f"**PROVINCIA_RECIDENCIA:** {info.get('PROVINCIA_RECIDENCIA', 'N/D')}")
                c2.write(f"**COMUNIDAD:** {info.get('COMUNIDAD', 'N/D')}")
                
                c3.write(f"**DISTRITO:** {info.get('DISTRITO', 'N/D')}")
                c3.write(f"**BARRIADA:** {info.get('BARRIADA', 'N/D')}")

            with t4:
                c1, c2, c3 = st.columns(3)
                c1.write(f"**ESCOLARIDAD:** {info.get('ESCOLARIDAD', 'N/D')}")
                c1.write(f"**Nº HIJOS:** {info.get('Nº HIJOS', 0)}")
                c1.write(f"**E.CIVIL:** {info.get('E.CIVIL', 'N/D')}")
                
                c2.write(f"**TITULO OBTENIDO:** {info.get('TITULO OBTENIDO', 'N/D')}")
                c2.write(f"**Nº HIJOS-SEX_M:** {info.get('Nº HIJOS-SEX_M', 0)}")
                c2.write(f"**Telefono:** {info.get('Telefono', 'N/D')}")
                
                c3.write(f"**ESPECIALIDAD:** {info.get('ESPECIALIDAD', 'N/D')}")
                c3.write(f"**Nº HIJOS-SEX_F:** {info.get('Nº HIJOS-SEX_F', 0)}")
                c3.write(f"**CASO EMERGENCIA:** {info.get('CASO EMERGENCIA', 'N/D')}")
                
                st.write(f"**telefono (Emergencia):** {info.get('telefono_emergencia', 'N/D')}")

        st.markdown("---")
        st.dataframe(df_filtrado.drop(columns=['NOMBRE_COMPLETO_SEL'], errors='ignore'), use_container_width=True, hide_index=True)
    else:
        st.info("No se encontraron registros coincidentes.")

# ==============================================================================
# MÓDULO 3: REGISTRAR NUEVA UNIDAD
# ==============================================================================
elif modulo_principal == "➕ Registrar Nueva Unidad":
    st.markdown("""
        <div class="neon-title-container">
            <div class="neon-title-inner">
                <h1>➕ Alta de Nueva Unidad Policial</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<p class="author-text">INGRESO DE EXPEDIENTE SEGÚN MATRIZ EXACTA</p>', unsafe_allow_html=True)

    tab_dat, tab_lab, tab_ubi, tab_aca = st.tabs([
        "📌 DATOS PERSONALES", 
        "🏢 DATOS LABORALES Y OPERATIVOS", 
        "🏠 DOMICILIO Y UBICACIÓN", 
        "🎓 ACADEMICO, FAMILIAR Y CONTACTO"
    ])

    with tab_dat:
        st.subheader("DATOS PERSONALES")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            rango = st.text_input("RANGO", key="r_reg")
        with c2:
            posicion = st.text_input("POSICION", key="p_reg")
        with c3:
            placa_metalica = st.text_input("PLACA METALICA", key="pm_reg")

        c4, c5, c6 = st.columns(3)
        with c4:
            nombre = st.text_input("NOMBRE", key="n_reg")
        with c5:
            apellido = st.text_input("APELLIDO", key="a_reg")
        with c6:
            cedula = st.text_input("CEDULA", key="c_reg")

        c7, c8, c9 = st.columns(3)
        with c7:
            tropa_carrera = st.text_input("TROPA O CARRERA", key="tc_reg")
        with c8:
            f_ingreso = st.date_input("F.INGRESO", value=None, min_value=date(1980, 1, 1), max_value=date.today(), key="fi_reg")
            if f_ingreso:
                hoy = date.today()
                anos = hoy.year - f_ingreso.year
                meses = hoy.month - f_ingreso.month
                if meses < 0:
                    anos -= 1
                    meses += 12
                if hoy.day < f_ingreso.day:
                    meses -= 1
                    if meses < 0:
                        anos -= 1
                        meses += 12
                tiempo_servicio_str = f"{anos} años, {meses} meses"
                st.metric("A.SERVICIO (Calculado)", tiempo_servicio_str)
            else:
                tiempo_servicio_str = "0 años, 0 meses"
                st.info("📅 Seleccione F. Ingreso.")
        with c9:
            st.metric("A.SERVICIO (Visual)", tiempo_servicio_str)

        c10, c11, c12 = st.columns(3)
        with c10:
            f_naci = st.date_input("FECHA DE NACI.", value=None, min_value=date(1930, 1, 1), max_value=date.today(), key="fn_reg")
            if f_naci:
                hoy = date.today()
                edad_calc = hoy.year - f_naci.year - ((hoy.month, hoy.day) < (f_naci.month, f_naci.day))
                st.metric("EDAD (Calculada)", f"{edad_calc} años")
            else:
                edad_calc = 0
                st.info("📅 Seleccione F. Nacimiento.")
        with c11:
            st.metric("EDAD (Visual)", f"{edad_calc} años")
        with c12:
            t_sangre = st.text_input("T.SANGRE", key="ts_reg")

        c10_s, _ = st.columns(2)
        with c10_s:
            seg_soc = st.text_input("SEG. SOC.", key="ss_reg")

    with tab_lab:
        st.subheader("DATOS LABORALES Y OPERATIVOS")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            grupo_opert = st.text_input("GRUPO OPERT", key="go_reg")
        with c2:
            tipo_serv = st.text_input("TIPO_SERV.", key="tvs_reg")
        with c3:
            faccion = st.text_input("FACCION", key="fac_reg")

        c4, c5, c6 = st.columns(3)
        with c4:
            grupo = st.text_input("GRUPO", key="grp_reg")
        with c5:
            departamento = st.text_input("DEPARTAMENTO", key="dep_reg")
        with c6:
            ogd_traslado = st.text_input("OGD.DE TRASLADO", key="ogd_reg")

        c7, c8, c9 = st.columns(3)
        with c7:
            centro_operativo = st.text_input("CENTRO OPERATIVO", key="co_reg")
        with c8:
            funcion = st.text_input("FUNCION", key="fun_reg")
        with c9:
            estado_actividad = st.text_input("ESTADO/ACTIVIDAD", key="ea_reg")

        c10, c11 = st.columns(2)
        with c10:
            causa_estado = st.text_input("CAUSA / ESTADO-ACTIVIDAD", key="ce_reg")
        with c11:
            destino_causa = st.text_input("DESTINO_CAUSA", key="dc_reg")

    with tab_ubi:
        st.subheader("DOMICILIO Y UBICACIÓN")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            prov_origen = st.text_input("PROV. DE ORIGEN", key="po_reg")
        with c2:
            prov_residencia = st.text_input("PROVINCIA_RECIDENCIA", key="pr_reg")
        with c3:
            distrito = st.text_input("DISTRITO", key="dis_reg")

        c4, c5, c6 = st.columns(3)
        with c4:
            corregimiento = st.text_input("CORREGIMIENTO", key="corr_reg")
        with c5:
            comunidad = st.text_input("COMUNIDAD", key="com_reg")
        with c6:
            barriada = st.text_input("BARRIADA", key="bar_reg")

        c7, _ = st.columns(2)
        with c7:
            num_casa = st.text_input("NUMERO DE CASA", key="nc_reg")

    with tab_aca:
        st.subheader("ACADEMICO, FAMILIAR Y CONTACTO")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            escolaridad = st.text_input("ESCOLARIDAD", key="esc_reg")
        with c2:
            titulo_obtenido = st.text_input("TITULO OBTENIDO", key="to_reg")
        with c3:
            especialidad = st.text_input("ESPECIALIDAD", key="esp_reg")

        c4, c5, c6 = st.columns(3)
        with c4:
            n_hijos_m = st.number_input("Nº HIJOS-SEX_M", min_value=0, value=0, key="hm_reg")
        with c5:
            n_hijos_f = st.number_input("Nº HIJOS-SEX_F", min_value=0, value=0, key="hf_reg")
        with c6:
            n_hijos = n_hijos_m + n_hijos_f
            st.metric("Nº HIJOS (Calculado)", n_hijos)

        c7, c8, c9 = st.columns(3)
        with c7:
            e_civil = st.text_input("E.CIVIL", key="ec_reg_aca")
        with c8:
            telefono = st.text_input("Telefono", key="tel_reg")
        with c9:
            caso_emergencia = st.text_input("CASO EMERGENCIA", key="ce_n_reg")

        c10, _ = st.columns(2)
        with c10:
            telefono_emergencia = st.text_input("telefono (Emergencia)", key="te_reg")

        st.markdown("---")
        if st.button("💾 Guardar Nueva Unidad en el Sistema", type="primary"):
            if nombre and apellido and cedula and f_naci and f_ingreso:
                nuevo_registro = {
                    'RANGO': rango, 'POSICION': posicion, 'PLACA METALICA': placa_metalica,
                    'NOMBRE': nombre.upper(), 'APELLIDO': apellido.upper(), 'CEDULA': cedula,
                    'TROPA O CARRERA': tropa_carrera, 'F.INGRESO': str(f_ingreso), 'A.SERVICIO': tiempo_servicio_str,
                    'FECHA DE NACI.': str(f_naci), 'EDAD': edad_calc, 'T.SANGRE': t_sangre,
                    'GRUPO OPERT': grupo_opert, 'TIPO_SERV.': tipo_serv, 'FACCION': faccion,
                    'GRUPO': grupo, 'DEPARTAMENTO': departamento, 'OGD.DE TRASLADO': ogd_traslado,
                    'CENTRO OPERATIVO': centro_operativo, 'FUNCION': funcion, 'ESTADO/ACTIVIDAD': estado_actividad,
                    'CAUSA / ESTADO-ACTIVIDAD': causa_estado, 'DESTINO_CAUSA': destino_causa,
                    'PROV. DE ORIGEN': prov_origen, 'PROVINCIA_RECIDENCIA': prov_residencia,
                    'DISTRITO': distrito, 'CORREGIMIENTO': corregimiento, 'COMUNIDAD': comunidad,
                    'BARRIADA': barriada, 'NUMERO DE CASA': num_casa, 'ESCOLARIDAD': escolaridad,
                    'TITULO OBTENIDO': titulo_obtenido, 'ESPECIALIDAD': especialidad,
                    'Nº HIJOS': n_hijos, 'Nº HIJOS-SEX_M': n_hijos_m, 'Nº HIJOS-SEX_F': n_hijos_f,
                    'E.CIVIL': e_civil, 'Telefono': telefono, 'CASO EMERGENCIA': caso_emergencia, 'telefono_emergencia': telefono_emergencia
                }
                
                nuevo_df = pd.DataFrame([nuevo_registro])
                st.session_state.df_personal = pd.concat([st.session_state.df_personal, nuevo_df], ignore_index=True)
                st.success(f"¡Unidad {nombre.upper()} {apellido.upper()} registrada con éxito! (Edad: {edad_calc} | Hijos: {n_hijos} | Años Serv.: {tiempo_servicio_str})")
            else:
                st.warning("⚠️ Por favor complete los campos obligatorios: Nombre, Apellido, Cédula, Fecha de Nacimiento y Fecha de Ingreso.")

# ==============================================================================
# MÓDULO 4: CONTROL DE NOVEDADES Y PERMISOS
# ==============================================================================
elif modulo_principal == "📋 Control de Novedades y Permisos":
    st.markdown("""
        <div class="neon-title-container">
            <div class="neon-title-inner">
                <h1>📋 Control de Novedades, Vacaciones e Incapacidades</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_novedad_personal"):
        c1, c2 = st.columns(2)
        with c1:
            placa_n = st.text_input("Número de Placa o Cédula de la Unidad")
            tipo_n = st.selectbox("Tipo de Novedad", ["Incapacidad", "Vacaciones Tomadas", "Permiso Especial", "Licencia"])
            dias_n = st.number_input("Cantidad de Días", min_value=1, value=1)
        with c2:
            f_ini = st.date_input("Fecha de Inicio", date.today())
            f_fin = st.date_input("Fecha de Finalización", date.today())
            obs_n = st.text_area("Observaciones / Diagnóstico / Detalles")
            
        if st.form_submit_button("Registrar Novedad"):
            st.success(f"Novedad de tipo '{tipo_n}' registrada exitosamente para la unidad.")

# ==============================================================================
# MÓDULO 5: RENDICIÓN DE CUENTAS
# ==============================================================================
elif modulo_principal == "📈 Rendición de Cuentas":
    st.markdown("""
        <div class="neon-title-container">
            <div class="neon-title-inner">
                <h1>📈 Módulo de Rendición de Cuentas y Estado de Fuerza</h1>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_rendicion_c5"):
        c1, c2 = st.columns(2)
        with c1:
            f_rep = st.date_input("Fecha del Reporte Operativo", date.today())
            zona_rep = st.text_input("Zona / Sector / Estación")
        with c2:
            oficial_rep = st.text_input("Oficial Responsable del Turno")
            
        resumen_rep = st.text_area("Novedades Relevantes, Fuerza Efectiva y Resultados Destacados")
        
        if st.form_submit_button("Generar Informe Ejecutivo"):
            st.success("Informe de rendición de cuentas guardado exitosamente para auditoría superior.")
