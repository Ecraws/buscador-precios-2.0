import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re

# Configuración de página móvil
st.set_page_config(page_title="ECRAWS PRICE", layout="centered")

# FUNCIÓN DE SEGURIDAD PARA LIMPIAR CÓDIGOS DE BARRAS E INTERNOS
def limpiar_codigo(val):
    if pd.isna(val):
        return ""
    # Convertir a texto limpio sin espacios en los extremos
    s = str(val).strip()
    # Si termina en .0 (ej: 12345.0), le quitamos el decimal para evitar fallos de coincidencia
    if s.endswith('.0'):
        s = s[:-2]
    # Quitar notación científica si la hubiera y pasar a minúsculas
    return s.lower()

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
            cod_interno = limpiar_codigo(fila.iloc[0])
            if not cod_interno: continue
            
            # Procesar cod1 (Columna C -> Índice 2) y cod2 (Columna D -> Índice 3)
            for idx_col in [2, 3]:
                if idx_col < len(fila) and pd.notna(fila.iloc[idx_col]):
                    c_scanner = limpiar_codigo(fila.iloc[idx_col])
                    if c_scanner and c_scanner != 'nan':
                        mapa_puente_barras[c_scanner] = cod_interno
    except Exception as e:
        st.warning(f"Aviso Maestro EAN: {e}")

    # 2. CARGAR PRODUCTOS BASE (productos.xlsx)
    try:
        df_base = pd.read_excel("productos.xlsx")
        for _, fila in df_base.iterrows():
            if fila.dropna().empty: continue
            c_int = limpiar_codigo(fila.get('Codigo Interno', ''))
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
                c_int = limpiar_codigo(fila.iloc[0]) # Col A (0)
                c_sku = limpiar_codigo(fila.iloc[2]) # Col C (2)
                
                of_data = {
                    'tipo': 'OFERTA',
                    'precio_of': fila.iloc[5],            # Col F (5)
                    'ahorro': fila.iloc[6],               # Col G (6)
                    'concepto': str(fila.iloc[9]).strip(),# Col J (9)
                    'hasta': fila.iloc[11]                # Col L (11)
                }
                if c_int: agregar_oferta_segura(c_int, of_data)
                if c_sku: agregar_oferta_segura(c_sku, of_data)

        # --- HOJA DESTACADOS ---
        if "DESTACADOS" in xls.sheet_names:
            df_dest = pd.read_excel(xls, sheet_name="DESTACADOS")
            for _, fila in df_dest.iterrows():
                if fila.dropna().empty: continue
                c_int = limpiar_codigo(fila.iloc[0]) # Col A (0)
                c_sku = limpiar_codigo(fila.iloc[2]) # Col C (2)
                
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
                
                # Función fragmentar para limpiar cada código interno del combo
                def fragmentar(celda):
                    if pd.isna(celda): return []
                    tokens = re.split(r'\s*[\|\-,\s]\s*', str(celda))
                    resultados = []
                    for t in tokens:
                        t_clean = t.strip()
                        if t_clean.endswith('.0'):
                            t_clean = t_clean[:-2]
                        if t_clean and t_clean.lower() != 'nan':
                            resultados.append(t_clean.lower())
                    return resultados

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

busqueda_raw = st.text_input("Buscar Producto", placeholder="Código interno, de barras o nombre...").strip()

if busqueda_raw:
    # Limpiamos también la búsqueda ingresada por el usuario
    busqueda = limpiar_codigo(busqueda_raw)

    # 1. Determinar el código interno real usando el maestro EAN si hace falta
    codigo_objetivo = busqueda
    if busqueda in mapa_puente_barras:
        codigo_objetivo = mapa_puente_barras[busqueda]

    # 2. Buscar coincidencias en la base de productos
    encontrados = []
    if codigo_objetivo in mapa_base:
        encontrados.append(mapa_base[codigo_objetivo])
    else:
        # Si no es código exacto, buscar por coincidencia de texto en la descripción
        termino_busqueda = busqueda_raw.lower()
        for prod in mapa_base.values():
            if termino_busqueda in prod['desc'].lower():
                encontrados.append(prod)

    # 3. Desplegar los resultados en pantalla (OPCIÓN 2: IMPACTO SUPERMERCADO)
    if encontrados:
        for p in encontrados:
            try:
                precio_normal = round(float(p['precio']))
            except Exception:
                precio_normal = 0
            
            # Buscar si el código interno tiene una oferta asociada (con código ya normalizado)
            oferta = mapa_ofertas.get(p['interno'])
            
            # Filtrado Estricto de Fecha de Vencimiento
            oferta_valida = False
            if oferta:
                try:
                    hoy = datetime.now().date()
                    fecha_vencimiento = pd.to_datetime(oferta['hasta'], errors='coerce').date()
                    
                    if pd.notna(fecha_vencimiento) and hoy <= fecha_vencimiento:
                        oferta_valida = True
                except:
                    oferta_valida = False

            # --- RENDERIZADO VISUAL CON LA OPCIÓN 2 ---
            if oferta_valida:
                try:
                    precio_promo = round(float(oferta['precio_of']))
                except Exception:
                    precio_promo = 0
                tipo_badge = oferta['tipo']
                detalle_promo = oferta['concepto'].upper()
                f_vence = pd.to_datetime(oferta['hasta']).strftime('%d/%m/%Y')
                
                # Elige rojo llamativo para Oferta/Destacado y naranja fuerte para Combo
                color_tarjeta = "#ff3838" if tipo_badge != "COMBO" else "#ff9f1a"
                
                st.markdown(f"""
                <div style="background-color:#0f172a; padding:20px; border-radius:16px; border:2.5px solid {color_tarjeta}; margin-bottom:15px; box-shadow: 0px 4px 15px {color_tarjeta}20; font-family:-apple-system,BlinkMacSystemFont,sans-serif;">
                    <div style="background-color:{color_tarjeta}; color:#ffffff; padding:4px 10px; border-radius:8px; font-size:11px; font-weight:bold; display:inline-block; margin-bottom:12px;">🚨 {tipo_badge}</div>
                    <h3 style="color:#ffffff; font-size:20px; font-weight:800; margin:0 0 10px 0; line-height:1.3;">{p['desc']}</h3>
                    <p style="color:#cbd5e1; margin:0; font-size:13px; font-weight:600; background-color:#1e293b; padding:8px 12px; border-radius:8px; border-left:4px solid {color_tarjeta};">📢 {detalle_promo}</p>
                    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-top:15px;">
                        <div>
                            <p style="color:#94a3b8; margin:0; font-size:12px; text-decoration:line-through;">Normal: ${precio_normal:,.0f}</p>
                            <p style="color:{color_tarjeta}; font-size:42px; margin:0; font-weight:900; line-height:1;">${precio_promo:,.0f}</p>
                        </div>
                        <div style="text-align:right;">
                            <p style="color:#64748b; margin:0; font-size:11px;">Vence</p>
                            <p style="color:#cbd5e1; margin:0; font-size:12px; font-weight:bold;">{f_vence}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Tarjeta de precio normal con el estilo de la Opción 2 adaptado
                sector_texto = str(p['sector']).upper() if p['sector'] and str(p['sector']).lower() != 'nan' else "SIN SECTOR"
                st.markdown(f"""
                <div style="background-color:#0f172a; padding:20px; border-radius:16px; border:1px solid rgba(255,255,255,0.1); margin-bottom:15px; font-family:-apple-system,BlinkMacSystemFont,sans-serif;">
                    <span style="color:#64748b; font-size:11px; font-weight:600; letter-spacing:1px; display:block; margin-bottom:8px;">{sector_texto}</span>
                    <h3 style="color:#ffffff; font-size:20px; font-weight:800; margin:0 0 12px 0; line-height:1.3;">{p['desc']}</h3>
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#2ecc71; font-size:38px; font-weight:900; line-height:1;">${precio_normal:,.0f}</span>
                        <span style="color:#64748b; font-size:11px; background-color:#1e293b; padding:4px 8px; border-radius:6px;">Cod: {p['interno'].upper()}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("❌ Producto no encontrado en las bases de datos.")
    
