import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# Configuración de la página para celulares
st.set_page_config(
    page_title="Buscador de Precios Ultra", 
    page_icon="📱", 
    layout="centered"
)

# Estilos visuales con PRECIO EL DOBLE DE GRANDE (90px)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .producto-card {
        background-color: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border-left: 10px solid #2ecc71;
    }
    .precio-enorme {
        color: #2ecc71;
        font-size: 90px; /* <-- EL DOBLE DE GRANDE */
        font-weight: 900;
        line-height: 1.0;
        margin: 15px 0;
        letter-spacing: -2px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }
    .historial-item {
        background-color: #ffffff;
        padding: 10px 15px;
        border-radius: 8px;
        margin-bottom: 8px;
        border-left: 4px solid #bdc3c7;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Buscador de Productos Ultra")

# Carga inteligente de datos desde el Excel
@st.cache_data
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
        st.error("⚠️ No se pudo cargar 'productos.xlsx'. Verifica los nombres de tus columnas en la fila 1.")
        return None

df = cargar_datos()

if df is not None:
    # Inicializamos la memoria de la aplicación
    if 'buscar_este_codigo' not in st.session_state:
        st.session_state.buscar_este_codigo = ""
    if 'historial' not in st.session_state:
        st.session_state.historial = []

    # Capturamos lo que envíe el JavaScript de la cámara
    if 'barcode_detected' in st.session_state and st.session_state.barcode_detected:
        nuevo_codigo = str(st.session_state.barcode_detected).strip()
        if nuevo_codigo and nuevo_codigo != st.session_state.buscar_este_codigo:
            st.session_state.buscar_este_codigo = nuevo_codigo
            st.session_state.barcode_detected = "" 
            st.rerun()

    # Pestañas de navegación superiores
    tab1, tab2 = st.tabs(["🔍 Buscar Tipeando", "📷 Escáner Manual 360°"])
    
    # --- PESTAÑA 1: BÚSQUEDA MANUAL ---
    with tab1:
        busqueda_texto = st.text_input("Escribí Descripción, Scanner o Cód. Interno:", key="manual_search").strip().lower()
        if busqueda_texto:
            st.session_state.buscar_este_codigo = busqueda_texto

    # --- PESTAÑA 2: CÁMARA ESCÁNER CON DISPARADOR MANUAL ---
    with tab2:
        if st.session_state.buscar_este_codigo:
            st.write("✨ ¡Código procesado!")
            if st.button("📷 Volver a encender cámara", type="primary"):
                st.session_state.buscar_este_codigo = ""
                st.rerun()
        else:
            st.subheader("Lector Guiado por Botón")
            st.write("Apunta al código (cualquier ángulo) y cuando lo veas nítido, presiona el botón rojo.")
            
            html_code = """
            <div style="text-align: center; position: relative;">
                <div id="interactive" class="viewport" style="width: 100%; max-width: 400px; height: 240px; border: 3px solid #3498db; border-radius: 12px; overflow: hidden; margin: 0 auto; background-color: #000; position: relative;">
                    <video autoplay playsinline style="width: 100%; height: 100%; object-fit: cover;"></video>
                    <div style="position: absolute; top: 50%; left: 10%; width: 80%; height: 2px; background-color: #3498db; opacity: 0.5; pointer-events: none;"></div>
                    <div style="position: absolute; top: 10%; left: 50%; width: 2px; height: 80%; background-color: #3498db; opacity: 0.5; pointer-events: none;"></div>
                </div>
                
                <button id="disparador" style="margin-top: 15px; padding: 12px 30px; font-size: 16px; font-weight: bold; color: white; background-color: #e74c3c; border: none; border-radius: 30px; box-shadow: 0px 4px 10px rgba(231,76,60,0.4); cursor: pointer;">
                    🔴 DISPARAR ESCÁNER
                </button>
                
                <p id="resultado" style="font-weight: bold; color: #3498db; margin-top: 12px; font-size: 15px;">Alinea el producto y gatilla...</p>
            </div>
            
            <script src="https://cdnjs.cloudflare.com/ajax/libs/quagga/0.12.1/quagga.min.js"></script>
            
            <script>
            let camaraIniciada = false;

            function reproducirBeep() {
                try {
                    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    const oscillator = audioCtx.createOscillator();
                    const gainNode = audioCtx.createGain();
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(1300, audioCtx.currentTime);
                    gainNode.gain.setValueAtTime(0.12, audioCtx.currentTime);
                    oscillator.connect(gainNode);
                    gainNode.connect(audioCtx.destination);
                    oscillator.start();
                    oscillator.stop(audioCtx.currentTime + 0.1);
                } catch(e) {}
            }

            // Iniciamos Quagga, pero NO procesamos datos en bucle de forma automática
            Quagga.init({
                inputStream: {
                    name: "Live",
                    type: "LiveStream",
                    target: document.querySelector('#interactive'),
                    constraints: {
                        width: { min: 1280, ideal: 1280 },
                        height: { min: 720, ideal: 720 },
                        facingMode: "environment",
                        focusMode: "continuous"
                    },
                },
                locator: { patchSize: "medium", halfSample: false },
                decoder: { 
                    readers: ["ean_reader", "ean_8_reader", "code_128_reader"],
                    tryPatterns: true // Habilita lectura 360° (vertical, diagonal)
                },
                locate: true
            }, function(err) {
                if (err) {
                    document.getElementById('resultado').innerText = "Error: Permite el uso de la cámara.";
                    document.getElementById('resultado').style.color = "red";
                    return;
                }
                Quagga.start();
                camaraIniciada = true;
            });

            // LOGICA DEL BOTON MANUAL: Solo lee cuando hacés click
            document.getElementById('disparador').addEventListener('click', function() {
                if (!camaraIniciada) return;
                
                document.getElementById('resultado').innerText = "⚡ Procesando imagen actual...";
                document.getElementById('resultado').style.color = "#e67e22";
                
                // Forzamos a Quagga a capturar un único fotograma clave en este instante y analizarlo
                const frame = Quagga.canvas.dom.image;
                
                // Registramos un listener temporal exclusivo para este disparo
                const unaSolaLectura = function(data) {
                    if (data && data.codeResult && data.codeResult.code) {
                        const codigo = data.codeResult.code;
                        if (codigo.length >= 5) {
                            reproducirBeep();
                            document.getElementById('resultado').innerText = "¡Detectado!: " + codigo;
                            document.getElementById('resultado').style.color = "#2ecc71";
                            
                            if (navigator.vibrate) navigator.vibrate(200);
                            
                            // Enviamos el código exacto a Streamlit
                            window.parent.postMessage({
                                type: 'streamlit:set_widget_value',
                                key: 'barcode_detected',
                                value: codigo
                            }, '*');
                            
                            Quagga.stop();
                            Quagga.offDetected(unaSolaLectura); // Desactivamos el listener
                        }
                    }
                };
                
                Quagga.onDetected(unaSolaLectura);
                
                // Si pasados 1.5 segundos no encontró nada en esa foto, avisa para volver a intentar
                setTimeout(() => {
                    Quagga.offDetected(unaSolaLectura);
                    if (document.getElementById('resultado').innerText === "⚡ Procesando imagen actual...") {
                        document.getElementById('resultado').innerText = "❌ No se leyó nada en esta posición. Reubica el código y vuelve a disparar.";
                        document.getElementById('resultado').style.color = "#e74c3c";
                    }
                }, 1500);
            });
            </script>
            """
            components.html(html_code, height=330)

    # --- MOSTRAR RESULTADOS DE BÚSQUEDA ---
    codigo_a_buscar = st.session_state.buscar_este_codigo.lower().strip()
    
    if codigo_a_buscar:
        resultados = df[
            df['desc_busqueda'].str.contains(codigo_a_buscar, na=False) | 
            df['scan_busqueda'].str.contains(codigo_a_buscar, na=False) |
            df['interno_busqueda'].str.contains(codigo_a_buscar, na=False)
        ]
        
        if not resultados.empty:
            primer_resultado = resultados.iloc[0]
            desc = primer_resultado['Descripcion']
            precio = primer_resultado['Precio']
            
            # Historial de consultas
            registro_historial = f"{desc} - **${precio:,}**"
            if not st.session_state.historial or st.session_state.historial[0] != registro_historial:
                st.session_state.historial.insert(0, registro_historial)
                if len(st.session_state.historial) > 3:
                    st.session_state.historial.pop()

            st.markdown(f"### 📦 Producto Encontrado:")
            
            for index, fila in resultados.iterrows():
                cod_int_texto = str(fila['Codigo Interno']).split('.')[0] if '.' in str(fila['Codigo Interno']) and str(fila['Codigo Interno']).split('.')[1] == '0' else str(fila['Codigo Interno'])
                scanner_texto = str(fila['codigoscanner']).split('.')[0] if '.' in str(fila['codigoscanner']) else str(fila['codigoscanner'])
                
                # Renderizado Premium: El precio se muestra de un tamaño colosal
                st.markdown(f"""
                <div class="producto-card">
                    <h2 style='margin:0; color:#2c3e50; font-size:26px;'>{fila['Descripcion']}</h2>
                    <p class="precio-enorme">💰 ${fila['Precio']:,}</p>
                    <p style='margin:0; color:#7f8c8d; font-size:16px; line-height: 1.6;'>
                        🔢 <b>Cód. Interno:</b> {cod_int_texto if pd.notna(fila['Codigo Interno']) else 'N/A'}<br>
                        📁 <b>Sector:</b> {fila['Descrip Sector'] if pd.notna(fila['Descrip Sector']) else 'N/A'}<br>
                        🏷️ <b>Scanner/EAN:</b> {scanner_texto if pd.notna(fila['codigoscanner']) else 'N/A'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # BOTÓN PARA LIMPIAR LA BÚSQUEDA ACTUAL
            if st.button("❌ Limpiar código / Escanear otro", type="secondary", use_container_width=True):
                st.session_state.buscar_este_codigo = ""
                st.rerun()
        else:
            st.warning(f"🔍 El código '{st.session_state.buscar_este_codigo}' no está en el Excel.")
            if st.button("🔄 Borrar y reintentar", use_container_width=True):
                st.session_state.buscar_este_codigo = ""
                st.rerun()

    # --- SECCIÓN DE HISTORIAL RECIENTE ---
    if st.session_state.historial:
        st.write("---")
        st.subheader("📋 Últimas consultas:")
        for item in st.session_state.historial:
            st.markdown(f'<div class="historial-item">🔹 {item}</div>', unsafe_allow_html=True)
