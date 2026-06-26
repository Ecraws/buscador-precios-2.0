import streamlit as st
import pandas as pd

# Configuración de página optimizada para rendimiento móvil
st.set_page_config(
    page_title="Buscador de Precios Flash Pro", 
    page_icon="⚡", 
    layout="centered"
)

# Estilos CSS Avanzados (UI/UX Limpia, Tarjetas Premium y Precios Destacados)
st.markdown("""
    <style>
    .main, .block-container {
        max-width: 100% !important;
        padding: 12px !important;
        overflow-x: hidden !important;
        background-color: #fcfcfd;
    }
    
    /* Contenedor principal de la tarjeta de producto */
    .producto-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.03), 0px 1px 3px rgba(0, 0, 0, 0.02);
        margin-top: 14px;
        margin-bottom: 14px;
        border-left: 6px solid #2ecc71;
        border-top: 1px solid #f1f2f6;
        border-right: 1px solid #f1f2f6;
        border-bottom: 1px solid #f1f2f6;
    }
    
    /* Título del Producto (Descripción) */
    .producto-titulo {
        margin: 0 0 12px 0; 
        color: #1e293b; 
        font-size: 20px; 
        font-weight: 700;
        line-height: 1.3;
    }
    
    /* Contenedor del Precio Destacado */
    .precio-contenedor {
        background-color: #f8fafc;
        padding: 12px 16px;
        border-radius: 12px;
        display: inline-block;
        width: 100%;
        box-sizing: border-box;
        margin-bottom: 14px;
        border: 1px solid #f1f5f9;
    }
    
    .precio-enorme {
        color: #2ecc71;
        font-size: 52px;
        font-weight: 900;
        line-height: 1;
        margin: 0;
        letter-spacing: -1.5px;
        font-family: system-ui, -apple-system, sans-serif;
    }
    
    /* Detalles Técnicos Estilizados */
    .meta-grid {
        display: flex;
        flex-direction: column;
        gap: 6px;
        font-family: system-ui, -apple-system, sans-serif;
    }
    
    .meta-item {
        font-size: 13.5px;
        color: #64748b;
        line-height: 1.4;
    }
    
    .meta-label {
        font-weight: 600;
        color: #475569;
        background-color: #f1f5f9;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
        text-transform: uppercase;
        margin-right: 6px;
        display: inline-block;
    }

    .historial-item {
        background-color: #ffffff;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 6px;
        border-left: 4px solid #475569;
        font-size: 14px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.01);
    }
    
    div[data-testid="stForm"] {
        padding: 14px !important;
        border-radius: 16px !important;
        background-color: white !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: none !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Buscador Flash Ultra")

# Función optimizada para formatear precios sin centavos rotos y con puntos de miles locales
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

    # --- FORMULARIO DE ENTRADA ---
    with st.form(key="formulario_busqueda", clear_on_submit=False):
        busqueda = st.text_input(
            "🔍 Ingresá Código o Nombre del Producto:", 
            placeholder="Escribí aquí y presioná Enter o Buscar...",
            key="input_text"
        ).strip().lower()
        
        bot_buscar = st.form_submit_button("🚀 BUSCAR PRECIO YA", use_container_width=True)

    if busqueda:
        if st.button("❌ LIMPIAR PANTALLA", use_container_width=True):
            st.rerun()

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

        # --- MUESTRA DE RESULTADOS ---
        if resultados_lista:
            
            # CONTROL DE HISTORIAL INTERACTIVO
            st.markdown("### 📥 Guardar en Recientes:")
            opciones_historial = [f"{p['desc']} ({formatear_precio(p['precio'])})" for p in resultados_lista]
            
            seleccion_prod = st.selectbox(
                "Seleccioná qué producto agregar a tus últimas búsquedas:",
                options=opciones_historial,
                label_visibility="collapsed"
            )
            
            if st.button("📌 AGREGAR A RECIENTES", use_container_width=True):
                if seleccion_prod:
                    idx = opciones_historial.index(seleccion_prod)
                    prod_elegido = resultados_lista[idx]
                    item_historial = f"{prod_elegido['desc']} - **{formatear_precio(prod_elegido['precio'])}**"
                    
                    if not st.session_state.historial or st.session_state.historial[0] != item_historial:
                        st.session_state.historial.insert(0, item_historial)
                        if len(st.session_state.historial) > 5:
                            st.session_state.historial.pop()
                    st.success("¡Producto guardado en la lista!")
            
            st.write("---")
            st.markdown(f"### 📦 Resultados ({len(resultados_lista)}):")
            
            # RENDERIZADO DE LAS NUEVAS TARJETAS LIMPIAS
            for prod in resultados_lista:
                precio_visual = formatear_precio(prod['precio'])
                cod_int = prod['interno'] if prod['interno'] != 'nan' else 'N/A'
                cod_scan = prod['scanner'] if prod['scanner'] != 'nan' else 'N/A'
                
                st.markdown(f"""
                <div class="producto-card">
                    <h2 class="producto-titulo">{prod['desc']}</h2>
                    
                    <div class="precio-contenedor">
                        <p class="precio-enorme">{precio_visual}</p>
                    </div>
                    
                    <div class="meta-grid">
                        <div class="meta-item"><span class="meta-label">Cód. Interno</span><span style="color:#334155;">{cod_int}</span></div>
                        <div class="meta-item"><span class="meta-label">Sector</span><span style="color:#334155;">{prod['sector']}</span></div>
                        <div class="meta-item"><span class="meta-label">Scanner / EAN</span><span style="color:#334155;">{cod_scan}</span></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"🔍 No se encontró ningún artículo para: '{busqueda}'.")

    # --- HISTORIAL ---
    if st.session_state.historial:
        st.write("---")
        st.subheader("📋 Últimas búsquedas guardadas:")
        for item in st.session_state.historial:
            st.markdown(f'<div class="historial-item">🔹 {item}</div>', unsafe_allow_html=True)
