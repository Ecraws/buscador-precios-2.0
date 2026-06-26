import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de página optimizada para rendimiento y diseño móvil
st.set_page_config(
    page_title="FlashPrice Neo Pro", 
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
    
    /* Colores globales de texto nativo */
    h1, h2, h3, h4, p, label {
        color: #ffffff !important;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
    /* Input de texto moderno */
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
    
    /* Botón Principal */
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
    }
    
    /* --- TARJETA DE PRODUCTO BASE --- */
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
    
    .producto-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #64748b, #cbd5e1);
    }

    /* --- TARJETA CON OFERTA ACTIVA (Borde Neón Dinámico) --- */
    .producto-card.con-oferta::before {
        background: linear-gradient(90deg, #ff4757, #ffa502) !important;
    }
    
    .producto-titulo {
        margin: 0 0 14px 0 !important; 
        color: #ffffff !important; 
        font-size: 22px !important; 
        font-weight: 800 !important;
        line-height: 1.3;
        letter-spacing: -0.5px;
    }
    
    /* Contenedores de Precios */
    .precio-contenedor {
        background: rgba(255, 255, 255, 0.03);
        padding: 14px 18px;
        border-radius: 16px;
        margin-bottom: 14px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .precio-enorme {
        color: #ffffff;
        font-size: 54px;
        font-weight: 900;
        line-height: 1;
        margin: 0;
        letter-spacing: -2px;
    }

    .precio-oferta-color {
        background: linear-gradient(90deg, #ff4757 0%, #ffa502 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Etiquetas de ofertas */
    .badge-oferta {
        display: inline-block;
        padding: 4px 10px;
        background: linear-gradient(135deg, #ff4757, #ff6b81);
        color: white !important;
        font-weight: 700;
        font-size: 11px;
        border-radius: 8px;
        text-transform: uppercase;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }

    .info-oferta-bloque {
        background: rgba(255, 71, 87, 0.08);
        border: 1px solid rgba(255, 71, 87, 0.15);
        padding: 12px;
        border-radius: 14px;
        margin-bottom: 14px;
        font-size: 13px;
    }
    
    /* Detalles Técnicos */
    .meta-flex {
        display: flex;
        flex-direction: column;
        gap: 6px;
    }
    
    .meta-item {
        font-size: 13px;
        color: #94a3b8;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.01);
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.02);
    }
    
    .meta-label {
        font-weight: 700;
        color: #64748b;
        font-size: 11px;
        text-transform: uppercase;
    }
    
    .meta-valor {
        color: #cbd5e1;
        font-weight: 600;
    }

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

st.markdown('<h1 style="text-align: center; font-size: 28px; font-weight: 800; background: linear-gradient(90deg, #ffffff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px;">⚡ FLASHPRICE NEO PRO</h1>', unsafe_allow_html=True)

def formatear_precio(valor):
    try:
        if pd.isna(valor) or valor == '': return "N/A"
        entero = round(float(valor))
        return f"${entero:,.0f}".replace(",", ".")
    except:
        return f"${valor}"

def formatear_fecha(val):
    try:
        if pd.isna(val): return "Sin fecha"
        if isinstance(val, datetime):
            return val.strftime("%d/%m/%Y")
        return str(val).split(" ")[0]
    except:
        return str(val)

def limpiar_codigo(cod):
    if pd.isna(cod): return ""
    st_cod = str(cod).strip()
    if '.' in st_cod and st_cod.split('.')[1] == '0':
        st_cod = st_cod.split('.')[0]
    return st_cod.lower()

# --- CARGA Y INDEXACIÓN EXTREMA EN MEMORIA ---
@st.cache_data(show_spinner=False)
def cargar_todo():
    # 1. Cargar Base Normal
    df_base, mapa_base = None, {}
    try:
        df_base = pd.read_excel("productos.xlsx")
        df_base['Descripcion_Clean'] = df_base['Descripcion'].astype(str).str.strip()
        df_base['Precio_Clean'] = df_base['Precio'].fillna(0)
        df_base['cod_interno_clean'] = df_base['Codigo Interno'].apply(limpiar_codigo)
        df_base['cod_scanner_clean'] = df_base['codigoscanner'].apply(limpiar_codigo)
        
        for _, fila in df_base.iterrows():
            prod_info = {
                'desc': fila['Descripcion_Clean'], 'precio': fila['Precio_Clean'],
                'interno': fila['cod_interno_clean'], 'scanner': fila['cod_scanner_clean'],
                'sector': str(fila['Descrip Sector']).strip() if pd.notna(fila['Descrip Sector']) else 'N/A'
            }
            if prod_info['interno']: mapa_base[prod_info['interno']] = prod_info
            if prod_info['scanner']: mapa_base[prod_info['scanner']] = prod_info
    except Exception as e:
        st.error("⚠️ Error cargando 'productos.xlsx'")

    # 2. Cargar Base Ofertas
    mapa_ofertas = {}
    try:
        xls = pd.ExcelFile("padron de ofertas.xlsx")
        
        # Hoja: OFERTAS
        if "OFERTAS" in xls.sheet_names:
            df_of = pd.read_excel(xls, sheet_name="OFERTAS")
            for _, fila in df_of.iterrows():
                c_int = limpiar_codigo(fila.iloc[0]) # Columna A
                c_sku = limpiar_codigo(fila.iloc[2]) # Columna C
                of_data = {
                    'tipo': 'OFERTA', 'precio_of': fila.iloc[5], # Columna F
                    'ahorro': fila.iloc[6], 'concepto': fila.iloc[9], 'hasta': fila.iloc[11]
                }
                if c_int: mapa_ofertas[c_int] = of_data
                if c_sku: mapa_ofertas[c_sku] = of_data

        # Hoja: DESTACADOS
        if "DESTACADOS" in xls.sheet_names:
            df_dest = pd.read_excel(xls, sheet_name="DESTACADOS")
            for _, fila in df_dest.iterrows():
                c_int = limpiar_codigo(fila.iloc[0]) # Columna A
                c_sku = limpiar_codigo(fila.iloc[2]) # Columna C
                of_data = {
                    'tipo': 'DESTACADO', 'precio_of': fila.iloc[4], # Columna E
                    'ahorro': None, 'concepto': fila.iloc[5], 'hasta': fila.iloc[7]
                }
                if c_int: mapa_ofertas[c_int] = of_data
                if c_sku: mapa_ofertas[c_sku] = of_data

        # Hoja: COMBOS
        if "COMBOS" in xls.sheet_names:
            df_comb = pd.read_excel(xls, sheet_name="COMBOS")
            for _, fila in df_comb.iterrows():
                c_int = limpiar_codigo(fila.iloc[0]) # Columna A
                c_sku = limpiar_codigo(fila.iloc[2]) # Columna C
                of_data = {
                    'tipo': 'COMBO', 'precio_of': fila.iloc[5], # Columna F
                    'ahorro': fila.iloc[6], 'concepto': fila.iloc[3], 'hasta': fila.iloc[8]
                }
                if c_int: mapa_ofertas[c_int] = of_data
                if c_sku: mapa_ofertas[c_sku] = of_data

    except Exception as e:
        st.warning("⚠️ No se encontró 'padron de ofertas.xlsx' o tiene formato incorrecto.")

    return df_base, mapa_base, mapa_ofertas

df_base, mapa_base, mapa_ofertas = cargar_todo()

if df_base is not None:
    if 'historial' not in st.session_state:
        st.session_state.historial = []

    with st.form(key="formulario_busqueda", clear_on_submit=False):
        busqueda = st.text_input("🔍 Buscar Producto:", placeholder="Código o nombre...").strip().lower()
        bot_buscar = st.form_submit_button("CONSEGUIR PRECIO")

    if busqueda:
        resultados_lista = []
        
        if busqueda in mapa_base:
            resultados_lista.append(mapa_base[busqueda])
        else:
            res_df = df_base[df_base['Descripcion_Clean'].str.lower().str.contains(busqueda, na=False)]
            for _, fila in res_df.iterrows():
                resultados_lista.append({
                    'desc': fila['Descripcion_Clean'], 'precio': fila['Precio_Clean'],
                    'interno': fila['cod_interno_clean'], 'scanner': fila['cod_scanner_clean'],
                    'sector': str(fila['Descrip Sector']).strip() if pd.notna(fila['Descrip Sector']) else 'N/A'
                })

        if resultados_lista:
            # Historial rápido
            st.markdown('<p style="font-weight: 700; font-size: 15px; margin-top:20px; color:#94a3b8 !important;">📌 Guardar en Consultas Recientes:</p>', unsafe_allow_html=True)
            opciones_historial = [f"{p['desc']} ({formatear_precio(p['precio'])})" for p in resultados_lista]
            seleccion_prod = st.selectbox("Historial:", options=opciones_historial, label_visibility="collapsed")
            
            if st.button("REGISTRAR EN HISTORIAL"):
                if seleccion_prod:
                    idx = opciones_historial.index(seleccion_prod)
                    p_elegido = resultados_lista[idx]
                    item_hist = f"{p_elegido['desc']} - **{formatear_precio(p_elegido['precio'])}**"
                    if not st.session_state.historial or st.session_state.historial[0] != item_hist:
                        st.session_state.historial.insert(0, item_hist)
                        if len(st.session_state.historial) > 4: st.session_state.historial.pop()
                    st.success("¡Agregado!")

            st.write("---")
            st.markdown(f'<h3 style="font-size:18px; font-weight:700; color:#94a3b8 !important;">📦 Encontrados ({len(resultados_lista)}):</h3>', unsafe_allow_html=True)
            
            # --- DESPLIEGUE SEGURO DE TARJETAS CON OFERTAS ---
            for prod in resultados_lista:
                # Comprobar si existe oferta vinculada por código interno o escáner
                oferta_vinculada = mapa_ofertas.get(prod['interno']) or mapa_ofertas.get(prod['scanner'])
                
                precio_base_visual = formatear_precio(prod['precio'])
                cod_int = prod['interno'] if prod['interno'] != '' else 'N/A'
                cod_scan = prod['scanner'] if prod['scanner'] != '' else 'N/A'
                
                if oferta_vinculada:
                    precio_oferta_visual = formatear_precio(oferta_vinculada['precio_of'])
                    txt_ahorro = f" | Ahorrás: {formatear_precio(oferta_vinculada['ahorro'])}" if oferta_vinculada['ahorro'] else ""
                    txt_hasta = formatear_fecha(oferta_vinculada['hasta'])
                    concepto_txt = str(oferta_vinculada['concepto']).upper() if pd.notna(oferta_vinculada['concepto']) else "PROMOCIÓN"
                    
                    html_tarjeta = (
                        f'<div class="producto-card con-oferta">'
                        f'<span class="badge-of">🔥 {oferta_vinculada["tipo"]}</span>'
                        f'<h2 class="producto-titulo">{prod["desc"]}</h2>'
                        f'<div class="precio-contenedor">'
                        f'<p class="precio-enorme precio-oferta-color">{precio_oferta_visual}</p>'
                        f'<p style="margin:5px 0 0 0; font-size:13px; color:#94a3b8 !important;">Precio normal: <del>{precio_base_visual}</del></p>'
                        f'</div>'
                        f'<div class="info-oferta-bloque">'
                        f'✨ <b>{concepto_txt}</b>{txt_ahorro}<br>📅 Vence: {txt_hasta}'
                        f'</div>'
                        f'<div class="meta-flex">'
                        f'<div class="meta-item"><span class="meta-label">Código Interno</span><span class="meta-valor">{cod_int}</span></div>'
                        f'<div class="meta-item"><span class="meta-label">Sector</span><span class="meta-valor">{prod["sector"]}</span></div>'
                        f'<div class="meta-item"><span class="meta-label">Scanner / EAN</span><span class="meta-valor">{cod_scan}</span></div>'
                        f'</div>'
                        f'</div>'
                    )
                else:
                    html_tarjeta = (
                        f'<div class="producto-card">'
                        f'<h2 class="producto-titulo">{prod["desc"]}</h2>'
                        f'<div class="precio-contenedor"><p class="precio-enorme">{precio_base_visual}</p></div>'
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

    if st.session_state.historial:
        st.write("---")
        st.markdown('<h3 style="font-size:18px; font-weight:700; color:#94a3b8 !important;">📋 Últimas consultas:</h3>', unsafe_allow_html=True)
        for item in st.session_state.historial:
            st.markdown(f'<div class="historial-item">🔹 {item}</div>', unsafe_allow_html=True)
                    
