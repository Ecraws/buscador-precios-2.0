import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re

# Configuración de página móvil
st.set_page_config(page_title="ECRAWS PRICE", layout="centered")

@st.cache_data(ttl=600)
def cargar_todo():
    mapa_base = {}
    mapa_ofertas = {}
    mapa_puente_barras = {}
    
    # 1. CARGAR MAESTRO EAN (maestro ean.xlsx)
    try:
        df_ean = pd.read_excel("maestro ean.xlsx")
        for _, fila in df_ean.iterrows():
            if fila.dropna().empty: continue
            cod_interno = str(fila.iloc[0]).strip().lower() if pd.notna(fila.iloc[0]) else ""
            if not cod_interno: continue
            
            # Procesar cod1 (Columna C -> Índice 2) y cod2 (Columna D -> Índice 3)
            for idx_col in [2, 3]:
                if idx_col < len(fila) and pd.notna(fila.iloc[idx_col]):
                    c_scanner = str(fila.iloc[idx_col]).strip().lower()
                    if c_scanner and c_scanner != 'nan':
                        mapa_puente_barras[c_scanner] = cod_interno
    except Exception as e:
        st.warning(f"Aviso Maestro EAN: {e}")

    # 2. CARGAR PRODUCTOS BASE (productos.xlsx)
    try:
        df_base = pd.read_excel("productos.xlsx")
        for _, fila in df_base.iterrows():
            if fila.dropna().empty: continue
            c_int = str(fila.get('Codigo Interno', '')).strip().lower()
            if c_int:
                mapa_base[c_int] = {
                    'desc': str(fila.get('Descripcion', 'Sin Nombre')).strip(),
                    'precio': fila.get('Precio', 0),
                    'interno': c_int,
                    'sector': str(fila.get('Descrip Sector', 'N/A')).strip()
                }
    except Exception as e:
        st.error(f"Error Productos Base: {e}")

    # Función auxiliar para priorizar la oferta más reciente en la carga
    def agregar_oferta_segura(codigo, nueva_of):
        if not codigo or codigo == 'nan': return
        if codigo in mapa_ofertas:
            existente = mapa_ofertas[codigo]
            try:
                dt_existente = pd.to_datetime(existente.get('hasta'), errors='coerce')
                dt_nueva = pd.to_datetime(nueva_of.get('hasta'), errors='coerce')
                if pd.notna(dt_existente) and pd.notna(dt_nueva) and dt_nueva > dt_existente:
                    mapa_ofertas[codigo] = nueva_of
            except: pass
        else:
            mapa_ofertas[codigo] = nueva_of

    # 3. CARGAR PADRÓN DE OFERTAS (padron de ofertas.xlsx)
    try:
        xls = pd.ExcelFile("padron de ofertas.xlsx")
        
        # --- HOJA OFERTAS ---
        if "OFERTAS" in xls.sheet_names:
            df_of = pd.read_excel(xls, sheet_name="OFERTAS")
            for _, fila in df_of.iterrows():
                if fila.dropna().empty: continue
                c_int = str(fila.iloc[0]).strip().lower() # Col A (0)
                c_sku = str(fila.iloc[2]).strip().lower() # Col C (2)
                
                of_data = {
                    'tipo': 'OFERTA',
                    'precio_of': fila.iloc[5],            # Col F (5)
                    'ahorro': fila.iloc[6],               # Col G (6)
                    'concepto': str(fila.iloc[9]).strip(),# Col J (9) -> ¡CORREGIDO!
                    'hasta': fila.iloc[11]                # Col L (11) -> ¡CORREGIDO!
                }
                if c_int: agregar_oferta_segura(c_int, of_data)
                if c_sku: agregar_oferta_segura(c_sku, of_data)

        # --- HOJA DESTACADOS ---
        if "DESTACADOS" in xls.sheet_names:
            df_dest = pd.read_excel(xls, sheet_name="DESTACADOS")
            for _, fila in df_dest.iterrows():
                if fila.dropna().empty: continue
                c_int = str(fila.iloc[0]).strip().lower() # Col A (0)
                c_sku = str(fila.iloc[2]).strip().lower() # Col C (2)
                
                of_data = {
                    'tipo': 'DESTACADO',
                    'precio_of': fila.iloc[4],            # Col E (4)
                    'ahorro': None,
                    'concepto': str(fila.iloc[5]).strip(),# Col F (5)
                    'hasta': fila.iloc[7]                 # Col H (7)
                }
                if c_int: agregar_oferta_segura(c_int, of_data)
                if c_sku: agregar_oferta_segura(c_sku, of_data)

        # --- HOJA COMBOS ---
        if "COMBOS" in xls.sheet_names:
            df_comb = pd.read_excel(xls, sheet_name="COMBOS")
            for _, fila in df_comb.iterrows():
                if fila.dropna().empty: continue
                
                # Función para fragmentar si vienen múltiples códigos separados
                def fragmentar(celda):
                    if pd.isna(celda): return []
                    return [str(p).strip().lower() for p in re.split(r'\s*[\|\-,\s]\s*', str(celda)) if str(p).strip()]

                lista_internos = fragmentar(fila.iloc[0]) # Col A (0)
                lista_skus = fragmentar(fila.iloc[2])     # Col C (2)
                
                of_data = {
                    'tipo': 'COMBO',
                    'precio_of': fila.iloc[5],            # Col F (5)
                    'ahorro': fila.iloc[6],               # Col G (6)
                    'concepto': str(fila.iloc[3]).strip(),# Col D (3)
                    'hasta': fila.iloc[8]                 # Col I (8)
                }
                for sub_int in lista_internos: agregar_oferta_segura(sub_int, of_data)
                for sub_sku in lista_skus: agregar_oferta_segura(sub_sku, of_data)
                
    except Exception as e:
        st.error(f"Error Padrón de Ofertas: {e}")

    return mapa_base, mapa_ofertas, mapa_puente_barras

# Inicializar bases indexadas rápidas
mapa_base, mapa_ofertas, mapa_puente_barras = cargar_todo()

# --- DISEÑO DE LA INTERFAZ ---
st.title("⚡ ECRAWS PRICE")

busqueda = st.text_input("Buscar Producto", placeholder="Código interno, de barras o nombre...").strip().lower()

if busqueda:
    # 1. Determinar el código interno real usando el maestro EAN si hace falta
    codigo_objetivo = busqueda
    if busqueda in mapa_puente_barras:
        codigo_objetivo = mapa_puente_barras[busqueda]

    # 2. Buscar coincidencias en la base de productos
    encontrados = []
    if codigo_objetivo in mapa_base:
        encontrados.append(mapa_base[codigo_objetivo])
    else:
        # Si no es código exacto, buscar por coincidencia en la descripción
        for prod in mapa_base.values():
            if busqueda in prod['desc'].lower():
                encontrados.append(prod)

    # 3. Desplegar los resultados en pantalla
    if encontrados:
        for p in encontrados:
            precio_normal = round(float(p['precio']))
            
            # Buscar si el código interno tiene una oferta activa asociada
            oferta = mapa_ofertas.get(p['interno'])
            
            # Filtrado Estricto de Fecha de Vencimiento
            oferta_valida = False
            if oferta:
                try:
                    hoy = datetime.now().date()
                    # Convertir la celda 'hasta' a una fecha limpia de Python
                    fecha_vencimiento = pd.to_datetime(oferta['hasta'], errors='coerce').date()
                    
                    # ¡Solo es válida si hoy es menor o igual a la fecha de vencimiento en el Excel!
                    if pd.notna(fecha_vencimiento) and hoy <= fecha_vencimiento:
                        oferta_valida = True
                except:
                    oferta_valida = False

            # Renderizado Condicional de Tarjetas HTML para celulares
            if oferta_valida:
                precio_promo = round(float(oferta['precio_of']))
                tipo_badge = oferta['tipo']
                detalle_promo = oferta['concepto'].upper() # Traerá el texto correcto (ej: "LLEVANDO 2 UNIDADES")
                f_vence = pd.to_datetime(oferta['hasta']).strftime('%d/%m/%Y')
                
                color_tarjeta = "#ff4757" if tipo_badge != "COMBO" else "#ffa502"
                
                st.markdown(f"""
                <div style="background-color:#131926; padding:20px; border-radius:14px; border:2px solid {color_tarjeta}; margin-bottom:15px;">
                    <span style="background-color:{color_tarjeta}; color:white; padding:4px 8px; border-radius:5px; font-size:12px; font-weight:bold;">🔥 {tipo_badge}</span>
                    <h3 style="margin-top:10px; color:white;">{p['desc']}</h3>
                    <h1 style="color:{color_tarjeta}; font-size:50px; margin:5px 0; font-weight:900;">${precio_promo:,.0f}</h1>
                    <p style="color:#94a3b8; font-style:italic; font-size:14px;">Precio normal: ${precio_normal:,.0f}</p>
                    <div style="background-color:#1e293b; padding:10px; border-radius:8px; margin-top:10px;">
                        <p style="color:#cbd5e1; margin:0; font-weight:bold; font-size:14px;">{detalle_promo}</p>
                        <p style="color:#94a3b8; margin:0; font-size:12px;">📅 Válido hasta: {f_vence}</p>
                    </div>
                    <hr style="opacity:0.1; margin:10px 0;">
                    <small style="color:#64748b;">Código Interno: {p['interno'].upper()} | Sector: {p['sector']}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Tarjeta de precio normal sin ofertas vencidas
                st.markdown(f"""
                <div style="background-color:#131926; padding:20px; border-radius:14px; border:1px solid rgba(255,255,255,0.1); margin-bottom:15px;">
                    <h3 style="color:white; margin:0;">{p['desc']}</h3>
                    <h1 style="color:#2ecc71; font-size:50px; margin:10px 0; font-weight:900;">${precio_normal:,.0f}</h1>
                    <hr style="opacity:0.1; margin:10px 0;">
                    <small style="color:#64748b;">Código Interno: {p['interno'].upper()} | Sector: {p['sector']}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("❌ Producto no encontrado en las bases de datos.")
        
