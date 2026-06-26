import streamlit as st
import pandas as pd

# Configuración de página optimizada para rendimiento y diseño móvil
st.set_page_config(
    page_title="FlashPrice Neo", 
    page_icon="⚡", 
    layout="centered"
)

# --- ARQUITECTURA DE DISEÑO ULTRA-PREMIUM (CSS) ---
st.markdown("""
    <style>
    /* Configuración global y fondo oscuro profundo */
    .main, .block-container {
        max-width: 100% !important;
        padding: 14px !important;
        overflow-x: hidden !important;
        background-color: #0b0f19 !important;
    }
    
    /* Cambiar el color de los títulos nativos de Streamlit a blanco */
    h1, h2, h3, h4, p, label {
        color: #ffffff !important;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* Input de texto ultra-moderno */
    .stTextInput input {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 14px !important;
        padding: 12px !important;
        font-size: 16px !important;
    }
    .stTextInput input:focus {
        border-color: #00f2fe !important;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.2) !important;
    }

    /* Formulario contenedor estilizado */
    div[data-testid="stForm"] {
        padding: 16px !important;
        border-radius: 20px !important;
        background: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Botón Principal Futurista */
    .stButton button {
        background: linear-gradient(135deg, #2ecc71 0%, #00f2fe 100%) !important;
        color: #0b0f19 !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 12px !important;
        font-size: 15px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0px 4px 15px rgba(46, 204, 113, 0.3) !important;
    }
    
    /* --- TARJETA DE PRODUCTO NEO-PREMIUM --- */
    .producto-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        padding: 24px;
        border-radius: 24px;
        box-shadow: 0px 15px 35px rgba(0, 0, 0, 0.4);
        margin-top: 16px;
        margin-bottom: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        position: relative;
        overflow: hidden;
    }
    
    /* Decoración de línea brillante superior */
    .producto-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #2ecc71, #00f2fe);
    }
    
    .producto-titulo {
        margin: 0 0 14px 0 !important; 
        color: #ffffff !important; 
        font-size: 22px !important; 
        font-weight: 800 !important;
        line-height: 1.3;
        letter-spacing: -0.5px;
    }
    
    /* Contenedor e Impacto del Precio */
    .precio-contenedor {
        background: rgba(255, 255, 255, 0.03);
        padding: 14px 18px;
        border-radius: 16px;
        margin-bottom: 18px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .precio-enorme {
        background: linear-gradient(90deg, #2ecc71 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 58px;
        font-weight: 900;
        line-height: 1;
        margin: 0;
        letter-spacing: -2px;
        font-family: system-ui, -apple-system, sans-serif;
    }
    
    /* Píldoras de información técnica modernas */
    .meta-flex {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    
    .meta-item {
        font-size: 14px;
        color: #94a3b8;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.02);
        padding: 8px 14px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.03);
    }
    
    .meta-label {
        font-weight: 700;
        color: #64748b;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .meta-valor {
        color: #cbd5e1;
        font-weight: 600;
    }

    /* Historial */
    .historial-item {
        background: rgba(30, 41, 59, 0.5);
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 6px;
        border-left: 4px solid #00f2fe;
        font-size: 14px;
        color: #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado estilizado con emojis limpios
st.markdown('<h1 style="text-align: center; font-size: 28px; font-weight: 800; background: linear-gradient(90deg, #ffffff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px;">⚡ FLASHPRICE NEO</h1>', unsafe_allow_html=True)

# Función optimizada para formatear precios locales sin centavos rotos
def formatear_precio(valor):
    try:
        entero = round(float(valor))
        return f"${entero:,.0f}".replace(",", ".")
    except:
        return f"${valor}"

# Motor de indexación instantánea en memoria
@st.cache_data(show_spinner=False)
def cargar_y_mapear_datos():
    try:
        df = pd.read_excel("productos.xlsx")
        df['Descripcion_Clean'] = df['Descripcion'].astype(str).str.strip()
        df['Precio_Clean'] = df['Precio'].fillna(0)
        
        df['cod_interno_clean'] = df['Codigo Interno'].astype(str).apply(
            lambda x: x.split('.')[0] if '.' in x and x.split('.')[1] == '0' else x
        ).str.strip().str.lower()
        
        df['cod_scanner_clean'] = df['codigoscanner'].astype(str).apply(
            lambda x: x.split('.')[0] if '.' in x else x
        ).str.strip().str.lower()
        
        mapa_codigos = {}
        for _, fila in df.iterrows():
            int_code = fila['cod_interno_clean']
            scan_code = fila['cod_scanner_clean']
            
            prod_info = {
                'desc': fila['Descripcion_Clean'],
                'precio': fila['Precio_Clean'],
                'interno': int_code,
                'sector': str(fila['Descrip Sector']).strip() if pd.notna(fila['Descrip Sector']) else 'N/A',
                'scanner': scan_code
            }
            if int_code and int_code != 'nan':
                mapa_codigos[int_code] = prod_info
            if scan_code and scan_code != 'nan':
                mapa_codigos[scan_code] = prod_info
                
        return df, mapa_codigos
    except Exception as e:
        st.error("⚠️ Error crítico: Verifica 'productos.xlsx' en tu GitHub.")
        return None, None

df, mapa_rapido = cargar_y_mapear_datos()

if df is not None:
    if 'historial' not in st.session_state:
        st.session_state.historial = []

    # --- FORMULARIO DE ENTRADA INDUSTRIAL ---
    with st.form(key="formulario_busqueda", clear_on_submit=False):
        busqueda = st.text_input(
            "🔍 Buscar Producto:", 
            placeholder="Escribí código o nombre aquí...",
            key="input_text"
        ).strip().lower()
        
        bot_buscar = st.form_submit_button("CONSEGUIR PRECIO")

    # --- PROCESAMIENTO DE BÚSQUEDA ---
    if busqueda:
        resultados_lista = []
        
        if busqueda in mapa_rapido:
            resultados_lista.append(mapa_rapido[busqueda])
        else:
            res_df = df[df['Descripcion_Clean'].str.lower().str.contains(busqueda, na=False)]
            if not res_df.empty:
                for _, fila in res_df.iterrows():
                    resultados_lista.append({
                        'desc': fila['Descripcion_Clean'],
                        'precio': fila['Precio_Clean'],
                        'interno': fila['cod_interno_clean'],
                        'sector': str(fila['Descrip Sector']).strip() if pd.notna(fila['Descrip Sector']) else 'N/A',
                        'scanner': fila['cod_scanner_clean']
                    })

        # --- MOSTRAR RESULTADOS ---
        if resultados_lista:
            
            # CONTROL DE HISTORIAL INTERACTIVO ESTILIZADO
            st.markdown('<p style="font-weight: 700; font-size: 15px; margin-top:20px; color:#94a3b8 !important;">📌 Guardar en Consultas Recientes:</p>', unsafe_allow_html=True)
            opciones_historial = [f"{p['desc']} ({formatear_precio(p['precio'])})" for p in resultados_lista]
            
            seleccion_prod = st.selectbox(
                "Seleccioná para el historial:",
                options=opciones_historial,
                label_visibility="collapsed"
            )
            
            if st.button("REGISTRAR EN HISTORIAL"):
                if seleccion_prod:
                    idx = opciones_historial.index(seleccion_prod)
                    prod_elegido = resultados_lista[idx]
                    item_historial = f"{prod_elegido['desc']} - **{formatear_precio(prod_elegido['precio'])}**"
                    
                    if not st.session_state.historial or st.session_state.historial[0] != item_historial:
                        st.session_state.historial.insert(0, item_historial)
                        if len(st.session_state.historial) > 4:
                            st.session_state.historial.pop()
                    st.success("¡Agregado con éxito!")
            
            st.write("---")
            st.markdown(f'<h3 style="font-size:18px; font-weight:700; color:#94a3b8 !important;">📦 Productos Encontrados ({len(resultados_lista)}):</h3>', unsafe_allow_html=True)
            
            # RENDERIZADO SEGURO ANTI-FALLAS (Se unificó todo el HTML en líneas continuas estrictas)
            for prod in resultados_lista:
                precio_visual = formatear_precio(prod['precio'])
                cod_int = prod['interno'] if prod['interno'] != 'nan' else 'N/A'
                cod_scan = prod['scanner'] if prod['scanner'] != 'nan' else 'N/A'
                
                html_tarjeta = (
                    f'<div class="producto-card">'
                    f'<h2 class="producto-titulo">{prod["desc"]}</h2>'
                    f'<div class="precio-contenedor"><p class="precio-enorme">{precio_visual}</p></div>'
                    f'<div class="meta-flex">'
                    f'<div class="meta-item"><span class="meta-label">Código Interno</span><span class="meta-valor">{cod_int}</span></div>'
                    f'<div class="meta-item"><span class="meta-label">Sector</span><span class="meta-valor">{prod["sector"]}</span></div>'
                    f'<div class="meta-item"><span class="meta-label">Scanner / EAN</span><span class="meta-valor">{cod_scan}</span></div>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(html_tarjeta, unsafe_allow_html=True)
        else:
            st.error(f"🔍 No se encontró ningún artículo para: '{busqueda}'.")

    # --- HISTORIAL RECIENTE NEO ---
    if st.session_state.historial:
        st.write("---")
        st.markdown('<h3 style="font-size:18px; font-weight:700; color:#94a3b8 !important;">📋 Últimas consultas:</h3>', unsafe_allow_html=True)
        for item in st.session_state.historial:
            st.markdown(f'<div class="historial-item">🔹 {item}</div>', unsafe_allow_html=True)
