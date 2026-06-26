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

# Función para separar códigos múltiples (ej: "2349 | 1187" -> ["2349", "1187"])
def fragmentar_codigos_multiples(celda):
    if pd.isna(celda): return []
    texto = str(celda).strip()
    # Separa por barras, guiones, comas o espacios extras
    partes = re.split(r'[\|\-,\s]+', texto)
    return [limpiar_codigo(p) for p in partes if p.strip() != ""]

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

        # Hoja: COMBOS (¡SOPORTE MULTI-CÓDIGO INTEGRADO!)
        if "COMBOS" in xls.sheet_names:
            df_comb = pd.read_excel(xls, sheet_name="COMBOS")
            for _, fila in df_comb.iterrows():
                # Obtenemos todos los códigos individuales de las celdas
                lista_internos = fragmentar_codigos_multiples(fila.iloc[0]) # Columna A
                lista_skus = fragmentar_codigos_multiples(fila.iloc[2])     # Columna C
                
                of_data = {
                    'tipo': 'COMBO', 'precio_of': fila.iloc[5], # Columna F
                    'ahorro': fila.iloc[6], 'concepto': fila.iloc[3], 'hasta': fila.iloc[8] # Columna D (Productos) como concepto
                }
                
                # Registramos el combo para cada código interno que tenga la celda
                for sub_int in lista_internos:
                    mapa_ofertas[sub_int] = of_data
                # Registramos el combo para cada scanner que tenga la celda
                for sub_sku in lista_skus:
                    mapa_ofertas[sub_sku] = of_data

    except Exception as e:
        st.warning("⚠️ No se encontró 'padron de ofertas.xlsx' o tiene formato incorrecto.")

    return df_base, mapa_base, mapa_ofertas

df_base, mapa_base, mapa_ofertas = cargar_todo()

if df_base is not None:
    if 'historial' not in st.session_state:
        st
        
