import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Configuración de diseño móvil estricto
st.set_page_config(
    page_title="Buscador Ultra Todo en Uno", 
    page_icon="📱", 
    layout="centered"
)

# Estilos CSS de Nivel Profesional (Ajuste perfecto a la pantalla de tu celular)
st.markdown("""
    <style>
    .main, .block-container {
        max-width: 100% !important;
        padding-left: 12px !important;
        padding-right: 12px !important;
        overflow-x: hidden !important;
        background-color: #f8f9fa;
    }
    .producto-card {
        background-color: white;
        padding: 22px;
        border-radius: 18px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.06);
        margin-top: 15px;
        margin-bottom: 15px;
        border-left: 12px solid #2ecc71;
    }
    .precio-enorme {
        color: #2ecc71;
        font-size: 95px;
        font-weight: 900;
        line-height: 0.85;
        margin: 15px 0;
        letter-spacing: -3px;
        font-family: Arial, sans-serif;
    }
    .historial-item {
        background-color: #ffffff;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 6px;
        border-left: 4px solid #34495e;
        font-size: 13px;
    }
    div[data-testid="stVerticalBlock"] {
        max-width: 100% !important;
        overflow-x: hidden !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Buscador de Productos Ultra")

# Carga e indexación rápida del archivo Excel
@st.cache_data(show_spinner=False)
def cargar_datos():
    try:
        df = pd.read_excel("productos.xlsx")
        df['desc_busqueda'] = df['Descripcion'].astype(str).str.lower().str.strip()
        df['scan_busqueda'] = df['codigoscanner'].astype(str).str.strip()
        df['interno_busqueda'] = df['Codigo Interno'].astype(str).apply(
            lambda x: x.split('.')[0] if '.' in x and x.split('.')[1] == '0' else x
        ).str.strip().str.lower()
        return df
    except Exception as e:
        st.error("⚠️ Error: No se encontró 'productos.xlsx' en tu repositorio de GitHub.")
        return None

df = cargar_datos()

if df is not None:
    # Estructura de memoria interna estable
    if 'buscar_este_codigo' not in st.session_state:
        st.session_state.buscar_este_codigo = ""
    if 'historial' not in st.session_state:
        st.session_state.historial = []
    if 'camara_activa' not in st.session_state:
        st.session_state.camara_activa = False

    # --- BLOQUE 1: PANEL DE CONTROL DE HARDWARE (Cámara y Limpieza) ---
    st.subheader("📷 Control del Escáner")
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.session_state.camara_activa:
            if st.button("🔴 APAGAR CÁMARA", use_container_width=True):
                st.session_state.camara_activa = False
                st.rerun()
        else:
            if st.button("🟢 ENCENDER CÁMARA", type="primary", use_container_width=True):
                st.session_state.camara_activa = True
                st.rerun()
                
    with col_btn2:
        if st.button("❌ LIMPIAR TODO", use_container_width=True):
            st.session_state.buscar_este_codigo = ""
            st.rerun()

    # --- BLOQUE 2: VISOR INTEGRADO COMPACTO ---
    if st.session_state.camara_activa:
        # Reducimos la altura del visor a 170px para garantizar que todo entre en la pantalla sin scroll
        html_code = """
        <div style="width: 100%; max-width: 100%; box-sizing: border-box; text-align: center; overflow: hidden;">
            
            <div id="interactive" class="viewport" style="width: 100%; max-width: 340px; height: 170px; border: 3px solid #3498db; border-radius: 14px; overflow: hidden; margin: 0 auto; background-color: #000; position: relative; box-sizing: border-box;">
                <video autoplay playsinline style="width: 100%; height: 100%; object-fit: cover; position: absolute; top:0; left:0; filter: contrast(1.1);"></video>
                <div style="position: absolute; top: 50%; left: 10%; width: 80%; height: 2px; background-color: #3498db; opacity: 0.6; pointer-events: none;"></div>
                <div style="position: absolute; top: 10%; left: 50%; width: 2px; height: 80%; background-color: #3498db; opacity: 0.6; pointer-events: none;"></div>
            </div>
            
            <button id="disparador" style="margin-top: 12px; padding: 14px 0; font-size: 16px; font-weight: bold; color: white; background-color: #e74c3c; border: none; border-radius: 25px; box-shadow: 0px 5px 15px rgba(231,76,60,0.4); cursor: pointer; width: 100%; max-width: 340px; box-sizing: border-box; -webkit-tap-highlight-color: transparent;">
                📸 GATILLAR ESCÁNER
            </button>
            
            <p id="resultado" style="font-weight: bold; color: #3498db; margin-top: 8px; font-size: 13px; margin-bottom: 2px;">Apunta y presiona el botón rojo</p>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
        
        <script>
        let quaggaListo = false;

        function beep() {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioCtx.createOscillator();
                const gainNode = audioCtx.createGain();
                oscillator.type = 'sine';
                oscillator.frequency.setValueAtTime(1350, audioCtx.currentTime);
                gainNode.gain.setValueAtTime(0.12, audioCtx.currentTime);
                oscillator.connect(gainNode);
                gainNode.connect(audioCtx.destination);
                oscillator.start();
                oscillator.stop(audioCtx.currentTime + 0.08);
            } catch(e) {}
        }

        Quagga.init({
            inputStream: {
                name: "Live",
                type: "LiveStream",
                target: document.querySelector('#interactive'),
                constraints: {
                    width: { min: 640, ideal: 1280 },
                    height: { min: 480, ideal: 720 },
                    facingMode: "environment"
                },
            },
            locator: { patchSize: "medium", halfSample: false },
            decoder: { 
                readers: ["ean_reader", "ean_8_reader", "code_128_reader"],
                tryPatterns: true
            },
            locate: true
        }, function(err) {
            if (err) {
                document.getElementById('resultado').innerText = "Permiso de cámara denegado.";
                return;
            }
            Quagga.start();
            quaggaListo = true;
        });

        document.getElementById('disparador').addEventListener('click', function() {
            if (!quaggaListo) return;
            
            document.getElementById('resultado').innerText = "⚡ Leyendo código...";
            document.getElementById('resultado').style.color = "#e67e22";
            
            const rafagaMecanica = function(data) {
                if (data && data.codeResult && data.codeResult.code) {
                    const codigo = data.codeResult.code.trim();
                    if (codigo.length >= 5) {
                        beep();
                        if (navigator.vibrate) navigator.vibrate(100);
                        
                        document.getElementById('resultado').innerText = "¡Código enviado!";
                        document.getElementById('resultado').style.color = "#2ecc71";
                        
                        Quagga.offDetected(rafagaMecanica);
                        Quagga.stop();
                        
                        // Enviamos el código usando el puente oficial de datos de Streamlit
                        window.parent.postMessage({
                            type: 'streamlit:set_widget_value',
                            key: 'codigo_escaneado_oculto',
                            value: codigo
                        }, '*');
                    }
                }
            };
            
            Quagga.onDetected(rafagaMecanica);
            
            setTimeout(() => {
                Quagga.offDetected(rafagaMecanica);
                if (document.getElementById('resultado').innerText === "⚡ Leyendo código...") {
                    document.getElementById('resultado').innerText = "❌ No se leyó. Enfoca bien y vuelve a intentar.";
                    document.getElementById('resultado').style.color = "#e74c3c";
                }
            }, 1400);
        });
        </script>
        """
        # Cambiamos a la nueva variable de widget para el puente directo
        st.session_state.buscar_este_codigo = st.text_input("🔑 Código actual:", key="codigo_escaneado_oculto", label_visibility="collapsed")
        components.html(html_code, height=255)
    else:
        st.info("💡 Lector apagado. Presioná el botón verde para encenderlo.")

    # --- BLOQUE 3: ENTRADA MANUAL COMPLEMENTARIA ---
    st.write("---")
    busqueda_manual = st.text_input("🔍 ¿No lee? Escribí Descripción o Código a mano:", value=st.session_state.buscar_este_codigo if not st.session_state.camara_activa else "").strip().lower()
    if busqueda_manual and busqueda_manual != st.session_state.buscar_este_codigo.lower():
        st.session_state.buscar_este_codigo = busqueda_manual
        st.rerun()

    # --- BLOQUE 4: PROCESADOR Y MUESTRA DEL PRECIO COLOSAL ---
    codigo_final = st.session_state.buscar_este_codigo.lower().strip()
    
    if codigo_final:
        resultados = df[
            df['desc_busqueda'].str.contains(codigo_final, na=False) | 
            df['scan_busqueda'].str.contains(codigo_final, na=False) |
            df['interno_busqueda'].str.contains(codigo_final, na=False)
        ]
        
        if not resultados.empty:
            primer_res = resultados.iloc[0]
            item_historial = f"{primer_res['Descripcion']} - **${primer_res['Precio']:,}**"
            if not st.session_state.historial or st.session_state.historial[0] != item_historial:
                st.session_state.historial.insert(0, item_historial)
                if len(st.session_state.historial) > 3:
                    st.session_state.historial.pop()

            st.markdown("### 📦 Producto Encontrado:")
            for index, fila in resultados.iterrows():
                cod_int_texto = str(fila['Codigo Interno']).split('.')[0] if '.' in str(fila['Codigo Interno']) and str(fila['Codigo Interno']).split('.')[1] == '0' else str(fila['Codigo Interno'])
                scanner_texto = str(fila['codigoscanner']).split('.')[0] if '.' in str(fila['codigoscanner']) else str(fila['codigoscanner'])
                
                # Renderizado Premium: Sin desbordes y precio colosal
                st.markdown(f"""
                <div class="producto-card">
                    <h2 style='margin:0; color:#2c3e50; font-size:24px; font-weight:700;'>{fila['Descripcion']}</h2>
                    <p class="precio-enorme">💰 ${fila['Precio']:,}</p>
                    <p style='margin:0; color:#7f8c8d; font-size:15px; line-height: 1.5; border-top: 1px solid #eee; padding-top: 10px;'>
                        🔢 <b>Cód. Interno:</b> <span style="color:#2c3e50;">{cod_int_texto if pd.notna(fila['Codigo Interno']) else 'N/A'}</span><br>
                        📁 <b>Sector:</b> <span style="color:#2c3e50;">{fila['Descrip Sector'] if pd.notna(fila['Descrip Sector']) else 'N/A'}</span><br>
                        🏷️ <b>Scanner/EAN:</b> <span style="color:#2c3e50;">{scanner_texto if pd.notna(fila['codigoscanner']) else 'N/A'}</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"🔍 El artículo '{st.session_state.buscar_este_codigo}' no está en el Excel.")

    # --- BLOQUE 5: HISTORIAL RECIENTE ---
    if st.session_state.historial:
        st.write("---")
        st.subheader("📋 Últimas consultas:")
        for item in st.session_state.historial:
            st.markdown(f'<div class="historial-item">🔹 {item}</div>', unsafe_allow_html=True)
