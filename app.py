import streamlit as st
import pandas as pd
import re
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
    
    h1, h2, h3, h4, p, label {
        color: #ffffff !important;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    
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

    div[data-testid="stForm"] {
        padding: 16px !important;
        border-radius: 20px !important;
        background: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.2) !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #2ecc71 0%, #00f2fe 100%) !important;
        color: #0b0f19 !important;
        font-weight: 700 !important;
        border-radius: 14px !important;
        border: none !important;
        padding: 12px !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    /* --- TARJETAS --- */
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

    .producto-card.con-oferta::before {
        background: linear-gradient(90deg, #ff4757, #ffa502) !important;
    }
    
    .producto-titulo {
        margin: 0 0 14px 0 !important; 
        color: #ffffff !important; 
        font-size: 22px !important; 
        font-weight: 800 !important;
        line-height: 1.3;
    }
    
    /* CONTENEDOR DE PRECIO TRADICIONAL */
    .precio-contenedor {
        background: rgba(255, 255, 255, 0.03);
        padding: 14px 18px;
        border-radius: 16px;
        margin-bottom: 14px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* CONTENEDOR PARTIDO EN DOS */
    .precio-split-container {
        display: flex;
        gap: 12px;
        margin-bottom: 14px;
        width: 100%;
    }
    
    .split-half {
        flex: 1;
        background: rgba(255, 255, 255, 0.03);
        padding: 12px 14px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        text-align: center;
    }
    
    .split-half.combo-side {
        background: rgba(255, 165, 0, 0.04);
        border: 1px solid rgba(254, 165, 2, 0.2);
    }

    .precio-enorme {
        color: #ffffff;
        font-size: 46px;
        font-weight: 900;
        line-height: 1;
        margin: 0;
        letter-spacing: -1px;
    }

    .precio-oferta-color {
        background: linear-gradient(90deg, #ff4757 0%, #ffa502 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .split-label {
        font-size: 11px;
        text-transform: uppercase;
        color: #64748b;
        font-weight: 700;
        margin-bottom: 4px;
        letter-spacing: 0.5px;
    }

    .info-oferta-bloque {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 12px;
        border-radius: 14px;
        margin-bottom: 14px;
        font-size: 13px;
    }
    
    /* Píldoras de estado de tiempo */
    .status-tiempo {
        font-size: 11px;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 6px;
        display: inline-block;
    }
    .status-activo { background: rgba(46, 204, 113, 0.15); color: #2ecc71 !important; }
    .status-futuro { background: rgba(255, 165, 0, 0.15); color: #ffa502 !important; }
    .status-ultimo { 
        background: rgba(231, 76, 60, 0.25); 
        color: #ff4757 !important; 
        border: 1px solid rgba(231, 76, 60, 0.5);
        animation: pulse_clean 2s infinite ease-in-out;
    }
    
    @keyframes pulse_clean {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .meta-flex { display: flex; flex-direction: column; gap: 6px; }
    .meta-item {
        font-size: 13px; color: #94a3b8; display: flex; align-items: center; justify-content: space-between;
        background: rgba(255, 255, 255, 0.01); padding: 6px 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.02);
    }
    .meta-label { font-weight: 700; color: #64748b; font-size: 11px; text-transform: uppercase; }
    .meta-valor { color: #cbd5e1; font-weight: 600; }
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
        dt = pd.to_datetime(val, errors='coerce')
        if pd.notna(dt):
            return dt.strftime("%d/%m/%Y")
        return str(val).split(" ")[0]
    except:
        return str(val)

# --- NORMALIZADOR Y PROCESADOR DE TIEMPOS ULTRA SEGURO ---
def evaluar_estado_oferta(desde_val, hasta_val):
    try:
        hoy = datetime.now().date()
        
        dt_hasta = pd.to_datetime(hasta_val, errors='coerce')
        dt_desde = pd.to_datetime(desde_val, errors='coerce')
        
        if pd.isna(dt_hasta) or pd.isna(dt_desde):
            return ""
            
        f_hasta = dt_hasta.date()
        f_desde = dt_desde.date()
            
        # 1. Filtro estricto: Si ya expiró, destruye la promo de la vista
        if hoy > f_hasta:
            return 'vencido'
            
        # 2. Notificación interactiva: Último día activo
        if hoy == f_hasta:
            return '<span class="status-tiempo status-ultimo">⚠️ ¡ÚLTIMO DÍA! Retirar cartel al cerrar</span>'
            
        diferencia = (hoy - f_desde).days
        if diferencia >= 0:
            return f'<span class="status-tiempo status-activo">⏱️ Activa (Hace {diferencia} días)</span>'
        else:
            return f'<span class="status-tiempo status-futuro">⏳ Inicia en {abs(diferencia)} días</span>'
    except:
        return ""

def limpiar_codigo(cod):
    if pd.isna(cod): return ""
    st_cod = str(cod).strip()
    if '.' in st_cod and st_cod.split('.')[1] == '0':
        st_cod = st_cod.split('.')[0]
    return st_cod.lower()

def fragmentar_codigos_multiples(celda):
    if pd.isna(celda): return []
    texto = str(celda).strip()
    partes = re.split(r'\s*[\|\-,\s]\s*', texto)
    return [limpiar_codigo(p) for p in partes if p.strip() != ""]

@st.cache_data(show_spinner=False)
def cargar_todo():
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

    mapa_ofertas = {}
    try:
        xls = pd.ExcelFile("padron de ofertas.xlsx")
        
        # Hoja: OFERTAS
        if "OFERTAS" in xls.sheet_names:
            df_of = pd.read_excel(xls, sheet_name="OFERTAS")
            for _, fila in df_of.iterrows():
                c_int = limpiar_codigo(fila.iloc[0]) 
                c_sku = limpiar_codigo(fila.iloc[2]) 
                of_data = {
                    'tipo': 'OFERTA', 'precio_of': fila.iloc[5], 
                    'ahorro': fila.iloc[6], 'concepto': fila.iloc[9], 
                    'desde': fila.iloc[10], 'hasta': fila.iloc[11]
                }
                if c_int: mapa_ofertas[c_int] = of_data
                if c_sku: mapa_ofertas[c_sku] = of_data

        # Hoja: DESTACADOS
        if "DESTACADOS" in xls.sheet_names:
            df_dest = pd.read_excel(xls, sheet_name="DESTACADOS")
            for _, fila in df_dest.iterrows():
                c_int = limpiar_codigo(fila.iloc[0]) 
                c_sku = limpiar_codigo(fila.iloc[2]) 
                of_data = {
                    'tipo': 'DESTACADO', 'precio_of': fila.iloc[4], 
                    'ahorro': None, 'concepto': fila.iloc[5], 
                    'desde': fila.iloc[6], 'hasta': fila.iloc[7]
                }
                if c_int: mapa_ofertas[c_int] = of_data
                if c_sku: mapa_ofertas[c_sku] = of_data

        # Hoja: COMBOS (Índices estrictamente mapeados)
        if "COMBOS" in xls.sheet_names:
            df_comb = pd.read_excel(xls, sheet_name="COMBOS")
            for _, fila in df_comb.iterrows():
                lista_internos = fragmentar_codigos_multiples(fila.iloc[0]) # Col A
                lista_skus = fragmentar_codigos_multiples(fila.iloc[2])     # Col C
                
                of_data = {
                    'tipo': 'COMBO', 'precio_of': fila.iloc[5],             # Col F
                    'ahorro': fila.iloc[6], 'concepto': fila.iloc[3],       # Col G y Col D
                    'desde': fila.iloc[7], 'hasta': fila.iloc[8]            # Col H y Col I
                }
                
                for sub_int in lista_internos:
                    if sub_int: mapa_ofertas[sub_int] = of_data
                for sub_sku in lista_skus:
                    if sub_sku: mapa_ofertas[sub_sku] = of_data

    except Exception as e:
        st.warning("⚠️ Formato modificado o inconsistencias detectadas en 'padron de ofertas.xlsx'.")

    return df_base, mapa_base, mapa_ofertas

df_base, mapa_base, mapa_ofertas = cargar_todo()

if df_base is not None:
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
            st.write("---")
            for prod in resultados_lista:
                oferta_vinculada = mapa_ofertas.get(prod['interno']) or mapa_ofertas.get(prod['scanner'])
                precio_base_visual = formatear_precio(prod['precio'])
                cod_int = prod['interno'] if prod['interno'] != '' else 'N/A'
                cod_scan = prod['scanner'] if prod['scanner'] != '' else 'N/A'
                
                badge_tiempo = ""
                es_oferta_valida = False
                
                if oferta_vinculada:
                    # Validación en tiempo real del periodo de vigencia
                    resultado_evaluacion = evaluar_estado_oferta(oferta_vinculada['desde'], oferta_vinculada['hasta'])
                    if resultado_evaluacion != 'vencido':
                        es_oferta_valida = True
                        badge_tiempo = resultado_evaluacion

                if es_oferta_valida:
                    precio_oferta_visual = formatear_precio(oferta_vinculada['precio_of'])
                    txt_ahorro = f" | Ahorrás: {formatear_precio(oferta_vinculada['ahorro'])}" if oferta_vinculada['ahorro'] else ""
                    txt_hasta = formatear_fecha(oferta_vinculada['hasta'])
                    concepto_txt = str(oferta_vinculada['concepto']).upper() if pd.notna(oferta_vinculada['concepto']) else "PROMOCIÓN"
                    tipo_promo = str(oferta_vinculada['tipo'])
                    
                    if tipo_promo == "COMBO":
                        bloque_precio_html = (
                            f'<div class="precio-split-container">'
                            f'<div class="split-half">'
                            f'<div class="split-label">Normal Indiv.</div>'
                            f'<div class="precio-enorme" style="color:#94a3b8;">{precio_base_visual}</div>'
                            f'</div>'
                            f'<div class="split-half combo-side">'
                            f'<div class="split-label" style="color:#ffa502;">Precio Combo</div>'
                            f'<div class="precio-enorme precio-oferta-color">{precio_oferta_visual}</div>'
                            f'</div>'
                            f'</div>'
                        )
                    else:
                        bloque_precio_html = (
                            f'<div class="precio-contenedor">'
                            f'<p class="precio-enorme precio-oferta-color">{precio_oferta_visual}</p>'
                            f'<p style="margin:5px 0 0 0; font-size:13px; color:#94a3b8 !important;">Precio normal: <del>{precio_base_visual}</del></p>'
                            f'</div>'
                        )
                    
                    html_tarjeta = (
                        f'<div class="producto-card con-oferta">'
                        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:6px;">'
                        f'<span style="padding:4px 10px; background:linear-gradient(135deg, #ff4757, #ffa502); color:white; font-weight:700; font-size:11px; border-radius:8px; text-transform:uppercase; letter-spacing:0.5px;">🔥 {tipo_promo}</span>'
                        f'{badge_tiempo}'
                        f'</div>'
                        f'<h2 class="producto-titulo">{prod["desc"]}</h2>'
                        f'{bloque_precio_html}'
                        f'<div class="info-oferta-bloque">'
                        f'📦 <b>DETALLE:</b> {concepto_txt}{txt_ahorro}<br>'
                        f'<span style="color:#94a3b8; font-size:12px;">📅 Vence: {txt_hasta}</span>'
                        f'</div>'
                        f'<div class="meta-flex">'
                        f'<div class="meta-item"><span class="meta-label">Código Interno</span><span class="meta-valor">{cod_int}</span></div>'
                        f'<div class="meta-item"><span class="meta-label">Sector</span><span class="meta-valor">{prod["sector"]}</span></div>'
                        f'<div class="meta-item"><span class="meta-label">Scanner / EAN</span><span class="meta-valor">{cod_scan}</span></div>'
                        f'</div>'
                        f'</div>'
                    )
                else:
                    # Render estándar si el producto no tiene promo activa o ya expiró temporalmente
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
                
