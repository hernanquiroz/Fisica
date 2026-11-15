import base64
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Cursos Física & Biofísica",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        #MainMenu, footer, header { visibility: hidden; }
        .block-container { padding: 0 !important; max-width: 100% !important; }
        .stApp { background: #0a0a1a; }
        iframe { border: none; display: block; }
    </style>
    """,
    unsafe_allow_html=True,
)

BASE_DIR = Path("cursos_data")
MAX_FILE_SIZE = 15 * 1024 * 1024

COURSES = {
    "fisica": {
        "title": "Introducción a la Física",
        "desc": "Fundamentos y conceptos básicos",
        "icon": "⚛️",
        "suit": "♠",
        "color1": "#ff6b6b",
        "color2": "#ee5a24",
        "color3": "#f0932b",
    },
    "bio1": {
        "title": "Biofísica I",
        "desc": "Fenómenos físicos en sistemas biológicos",
        "icon": "🧬",
        "suit": "♥",
        "color1": "#6c5ce7",
        "color2": "#a29bfe",
        "color3": "#74b9ff",
    },
    "bio2": {
        "title": "Biofísica II",
        "desc": "Membranas, electricidad y radiación",
        "icon": "🔬",
        "suit": "♦",
        "color1": "#00cec9",
        "color2": "#00b894",
        "color3": "#55efc4",
    },
}

for key in COURSES:
    (BASE_DIR / key).mkdir(parents=True, exist_ok=True)


def get_files(course_key: str) -> list:
    folder = BASE_DIR / course_key
    files = []
    for f in sorted(folder.glob("*")):
        if f.is_file() and f.stat().st_size <= MAX_FILE_SIZE:
            try:
                data = base64.b64encode(f.read_bytes()).decode()
                files.append({"name": f.name, "size": f.stat().st_size, "data": data})
            except Exception:
                continue
    return files


# ---------- Sidebar ----------
with st.sidebar:
    st.title("📤 Administrar archivos")
    st.caption("Sube material a cada curso")
    sel = st.selectbox("Curso", list(COURSES.keys()),
                       format_func=lambda k: COURSES[k]["title"])
    uploaded = st.file_uploader("Selecciona archivos", accept_multiple_files=True)
    if uploaded and st.button("💾 Guardar", use_container_width=True, type="primary"):
        for uf in uploaded:
            (BASE_DIR / sel / uf.name).write_bytes(uf.getbuffer())
        st.success(f"✅ {len(uploaded)} archivo(s) subido(s)")
        st.rerun()
    st.divider()
    st.caption(f"Máx. por archivo: {MAX_FILE_SIZE // (1024*1024)} MB")
    if st.button("🗑️ Vaciar este curso", use_container_width=True):
        for f in (BASE_DIR / sel).glob("*"):
            if f.is_file():
                f.unlink()
        st.rerun()


courses_data = [{"id": k, **v, "files": get_files(k)} for k, v in COURSES.items()]
courses_json = json.dumps(courses_data, ensure_ascii=False).replace("</", "<\\/")


HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: radial-gradient(ellipse at top, #1a1a3e 0%, #0f0f1e 55%, #000 100%);
    color: white; overflow-x: hidden; min-height: 100vh;
  }
  body { padding: 20px 10px 40px; }

  .header { text-align: center; margin-bottom: 6px; }
  .header h1 {
    font-size: clamp(1.4rem, 4vw, 2.4rem);
    margin: 0 0 6px; font-weight: 800;
    background: linear-gradient(90deg, #ff6b6b, #a29bfe, #00cec9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .header p { color: rgba(255,255,255,.6); margin: 0; font-size: .9rem; }

  /* ============ CARRUSEL 3D ARRASTRABLE ============ */
  .carousel-wrap {
    position: relative;
    width: 100%; max-width: 1100px;
    margin: 30px auto 0;
    height: 480px;
    perspective: 1600px;
    cursor: grab;
    user-select: none;
    -webkit-user-select: none;
    touch-action: pan-y;
    overflow: visible;
  }
  .carousel-wrap:active { cursor: grabbing; }
  .carousel { position: relative; width: 100%; height: 100%; }

  .card {
    position: absolute;
    top: 50%; left: 50%;
    width: 240px; height: 360px;
    margin-top: -180px; margin-left: -120px;
    border-radius: 22px;
    cursor: pointer;
    transition: opacity .3s ease;
    transform-style: preserve-3d;
    box-shadow: 0 25px 60px rgba(0,0,0,.55);
    will-change: transform, opacity;
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
  }
  .card-inner {
    position: relative;
    width: 100%; height: 100%;
    padding: 22px 18px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center;
    border-radius: 22px;
    overflow: hidden;
    color: white;
  }
  .card-inner::before {
    content: ""; position: absolute; inset: 0;
    background: radial-gradient(circle at 30% 15%, rgba(255,255,255,.35), transparent 55%);
    pointer-events: none;
  }
  .card-inner::after {
    content: ""; position: absolute; inset: 0;
    border-radius: 22px;
    border: 2px solid rgba(255,255,255,.25);
    pointer-events: none;
  }

  .suit { position: absolute; font-size: 1.7rem; opacity: .32; color: #fff; }
  .suit.tl { top: 14px; left: 18px; }
  .suit.tr { top: 14px; right: 18px; }
  .suit.bl { bottom: 14px; left: 18px; transform: rotate(180deg); }
  .suit.br { bottom: 14px; right: 18px; transform: rotate(180deg); }

  .icon {
    font-size: 3.8rem; margin-bottom: 12px;
    filter: drop-shadow(0 8px 20px rgba(0,0,0,.4));
    position: relative; z-index: 1;
    animation: float 3.4s ease-in-out infinite;
  }
  @keyframes float {
    0%,100% { transform: translateY(0); }
    50%     { transform: translateY(-8px); }
  }
  .card h2 {
    font-size: 1.2rem; margin: 0 0 8px; line-height: 1.2;
    font-weight: 800; text-shadow: 0 2px 12px rgba(0,0,0,.4);
    position: relative; z-index: 1;
  }
  .card p {
    font-size: .78rem; margin: 0 0 14px; opacity: .93;
    line-height: 1.3; position: relative; z-index: 1;
  }
  .badge {
    display: inline-block; padding: 5px 14px;
    border-radius: 20px; background: rgba(255,255,255,.22);
    backdrop-filter: blur(8px);
    font-size: .7rem; font-weight: 700;
    border: 1px solid rgba(255,255,255,.35);
    position: relative; z-index: 1;
  }
  .tap-hint {
    display: none;
    font-size: .65rem; opacity: .9; margin-top: 10px;
    position: relative; z-index: 1;
    animation: pulse 2s ease-in-out infinite;
  }
  .card[data-center="1"] .tap-hint { display: block; }
  @keyframes pulse {
    0%,100% { opacity: .55; }
    50%     { opacity: 1; }
  }

  /* Indicador de arrastre */
  .drag-hint {
    text-align: center;
    margin-top: 8px;
    font-size: .78rem;
    color: rgba(255,255,255,.5);
    letter-spacing: .5px;
  }
  .drag-hint span { display: inline-block; animation: slide 2s ease-in-out infinite; }
  @keyframes slide {
    0%,100% { transform: translateX(-4px); }
    50%     { transform: translateX(4px); }
  }

  /* ============ MODAL ============ */
  .modal {
    position: fixed; inset: 0;
    background: rgba(5,5,20,.93);
    backdrop-filter: blur(14px);
    display: none; align-items: center; justify-content: center;
    z-index: 9999; padding: 20px;
  }
  .modal.open { display: flex; }
  .modal-content {
    background: linear-gradient(160deg, #1e1e3f, #0f0f2e);
    border: 2px solid rgba(255,255,255,.1);
    border-radius: 25px;
    max-width: 640px; width: 100%;
    max-height: 85vh; overflow-y: auto;
    padding: 30px;
    position: relative;
    animation: unfold .55s cubic-bezier(.34,1.56,.64,1);
    box-shadow: 0 30px 80px rgba(0,0,0,.75);
  }
  @keyframes unfold {
    from { transform: scale(.3) rotateX(80deg); opacity: 0; }
    to   { transform: scale(1) rotateX(0);       opacity: 1; }
  }
  .modal-header {
    display: flex; align-items: center; gap: 15px;
    margin-bottom: 16px; padding-right: 45px;
  }
  .modal-icon { font-size: 2.8rem; }
  .modal-header h2 { margin: 0; font-size: 1.5rem; line-height: 1.2; }
  .modal-header p { margin: 4px 0 0; opacity: .7; font-size: .85rem; }
  .close-btn {
    position: absolute; top: 16px; right: 16px;
    background: rgba(255,71,87,.9); color: white;
    border: none; width: 38px; height: 38px;
    border-radius: 50%; font-size: 1.1rem;
    cursor: pointer; transition: transform .25s ease, background .2s;
    display: flex; align-items: center; justify-content: center;
  }
  .close-btn:hover { transform: rotate(90deg) scale(1.1); background: #ff4757; }
  .files-title { font-size: 1rem; margin: 20px 0 12px; opacity: .9; }
  .file-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 13px 16px; margin-bottom: 10px;
    background: rgba(255,255,255,.06);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 12px;
    transition: all .2s;
    text-decoration: none; color: white;
  }
  .file-item:hover {
    background: rgba(255,255,255,.12);
    transform: translateX(5px);
    border-color: rgba(162,155,254,.6);
  }
  .file-name {
    display: flex; align-items: center; gap: 10px;
    font-size: .9rem; overflow: hidden; flex: 1; min-width: 0;
  }
  .file-name span:first-child { font-size: 1.2rem; flex-shrink: 0; }
  .file-name span:last-child {
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .download-btn {
    background: linear-gradient(135deg, #6c5ce7, #a29bfe);
    padding: 7px 14px; border-radius: 20px;
    font-size: .72rem; font-weight: 700;
    flex-shrink: 0; color: white;
  }
  .empty { text-align: center; padding: 40px 20px; opacity: .5; font-style: italic; }

  /* ============ RESPONSIVE ============ */
  @media (max-width: 700px) {
    .carousel-wrap { height: 420px; }
    .card { width: 210px; height: 315px; margin-top: -157px; margin-left: -105px; }
    .icon { font-size: 3rem; }
    .card h2 { font-size: 1.05rem; }
    .card p { font-size: .72rem; }
    .modal-content { padding: 22px; }
  }
  @media (max-width: 400px) {
    .card { width: 180px; height: 270px; margin-top: -135px; margin-left: -90px; }
  }
</style>
</head>
<body>

<div class="header">
  <h1>🎓 Cursos de Física &amp; Biofísica</h1>
  <p>Arrastra o desliza para girar el carrusel</p>
</div>

<div class="carousel-wrap" id="carousel-wrap">
  <div class="carousel" id="carousel"></div>
</div>

<div class="drag-hint">
  <span>👈 &nbsp; Arrastra / swipe / rueda del mouse &nbsp; 👉</span>
</div>

<div class="modal" id="modal">
  <div class="modal-content" id="modalContent"></div>
</div>

<script id="courses-data" type="application/json">__COURSES_JSON__</script>
<script>
(function () {
  const courses = JSON.parse(document.getElementById('courses-data').textContent);
  const N = courses.length;
  const wrapEl        = document.getElementById('carousel-wrap');
  const carouselEl    = document.getElementById('carousel');
  const modalEl       = document.getElementById('modal');
  const modalContent  = document.getElementById('modalContent');

  // --- Configuración de layout 3D ---
  const CARD_STEP    = 280;   // separación horizontal entre cartas (px)
  const CARD_ROT_Y   = 22;    // grados de rotación lateral
  const CARD_SCALE   = 0.80;  // escala de las cartas laterales
  const CARD_Z_SIDE  = -70;   // profundidad de cartas laterales
  const DRAG_THRESHOLD = 6;   // px para considerar que fue drag
  const SNAP_DURATION = 550;  // ms

  // --- Estado ---
  let rotation     = 0;   // posición actual del carrusel (en unidades de carta)
  let isDragging   = false;
  let justDragged  = false;
  let startX       = 0;
  let startRotation= 0;
  let lastMoveX    = 0;
  let lastMoveTime = 0;
  let velocity     = 0;   // px / ms
  let animationRAF = null;

  // --- Crear cartas ---
  const cards = [];
  courses.forEach((c, i) => {
    const bg = `linear-gradient(150deg, ${c.color1}, ${c.color2}, ${c.color3})`;
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.index = i;
    card.innerHTML = `
      <div class="card-inner" style="background:${bg};">
        <div class="suit tl">${c.suit}</div>
        <div class="suit tr">${c.suit}</div>
        <div class="suit bl">${c.suit}</div>
        <div class="suit br">${c.suit}</div>
        <div class="icon">${c.icon}</div>
        <h2>${c.title}</h2>
        <p>${c.desc}</p>
        <span class="badge">${c.files.length} archivo${c.files.length === 1 ? '' : 's'}</span>
        <div class="tap-hint">👆 Toca para abrir</div>
      </div>`;
    carouselEl.appendChild(card);
    cards.push(card);
  });

  // --- Cálculo del offset circular (más cercano a 0 = frente) ---
  function getOffset(i) {
    let off = ((i - rotation) % N + N) % N;
    if (off >= N / 2) off -= N;
    return off;
  }

  // --- Actualizar transformaciones de todas las cartas ---
  function updateCards() {
    cards.forEach((card, i) => {
      const off    = getOffset(i);
      const absOff = Math.abs(off);
      const sign   = Math.sign(off) || 1;

      const x       = off * CARD_STEP;
      const z       = -Math.min(absOff, 1) * Math.abs(CARD_Z_SIDE)
                      - Math.max(0, absOff - 1) * 200;
      const rotY    = -sign * Math.min(absOff, 1) * CARD_ROT_Y;
      const scale   = 1 - Math.min(absOff, 1) * (1 - CARD_SCALE);
      const opacity = absOff <= 1
                      ? 1
                      : Math.max(0, 1 - (absOff - 1) * 2);
      const zIndex  = 20 - Math.round(absOff * 5);

      card.style.transform  = `translate3d(${x}px, 0, ${z}px) rotateY(${rotY}deg) scale(${scale})`;
      card.style.opacity    = opacity;
      card.style.zIndex     = zIndex;
      card.style.pointerEvents = absOff > 1.2 ? 'none' : 'auto';
      card.dataset.center   = absOff < 0.5 ? '1' : '0';
    });
  }

  // --- Animación de snap con easing ---
  function animateTo(target, duration = SNAP_DURATION) {
    if (animationRAF) cancelAnimationFrame(animationRAF);
    const start     = rotation;
    const startTime = performance.now();
    const distance  = target - start;

    function step(now) {
      const t = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3); // easeOutCubic
      rotation = start + distance * eased;
      updateCards();
      if (t < 1) {
        animationRAF = requestAnimationFrame(step);
      } else {
        rotation = target;
        updateCards();
        animationRAF = null;
      }
    }
    animationRAF = requestAnimationFrame(step);
  }

  function getCurrentIndex() {
    return ((Math.round(rotation) % N) + N) % N;
  }

  function shortestTarget(index) {
    const currentMod = ((rotation % N) + N) % N;
    let diff = index - currentMod;
    if (diff >  N / 2) diff -= N;
    if (diff < -N / 2) diff += N;
    return Math.round(rotation + diff);
  }

  // --- Drag con Pointer Events (mouse + touch) ---
  wrapEl.addEventListener('pointerdown', onPointerDown);

  function onPointerDown(e) {
    if (animationRAF) {
      cancelAnimationFrame(animationRAF);
      animationRAF = null;
    }
    isDragging = true;
    justDragged = false;
    startX = e.clientX;
    startRotation = rotation;
    lastMoveX = e.clientX;
    lastMoveTime = performance.now();
    velocity = 0;

    window.addEventListener('pointermove', onPointerMove);
    window.addEventListener('pointerup', onPointerUp);
    window.addEventListener('pointercancel', onPointerUp);
  }

  function onPointerMove(e) {
    if (!isDragging) return;
    const dx = e.clientX - startX;
    if (Math.abs(dx) > DRAG_THRESHOLD) justDragged = true;

    rotation = startRotation - dx / CARD_STEP;
    updateCards();

    const now = performance.now();
    const dt  = now - lastMoveTime;
    if (dt > 0) {
      const v = (e.clientX - lastMoveX) / dt;
      velocity = velocity * 0.6 + v * 0.4;
    }
    lastMoveX = e.clientX;
    lastMoveTime = now;
  }

  function onPointerUp() {
    if (!isDragging) return;
    isDragging = false;
    window.removeEventListener('pointermove', onPointerMove);
    window.removeEventListener('pointerup', onPointerUp);
    window.removeEventListener('pointercancel', onPointerUp);

    // Si hace mucho que no se movía, olvidar velocidad
    if (performance.now() - lastMoveTime > 100) velocity = 0;

    // Momentum suave (clamp)
    const momentum = Math.max(-1.5, Math.min(1.5, velocity * 0.4));
    const target   = Math.round(rotation + momentum);
    animateTo(target, SNAP_DURATION);
  }

  // --- Click en carta: centrar o abrir modal ---
  cards.forEach((card, i) => {
    card.addEventListener('click', () => {
      if (justDragged) { justDragged = false; return; }
      const current = getCurrentIndex();
      if (i === current) {
        openModal(courses[i]);
      } else {
        animateTo(shortestTarget(i));
      }
    });
  });

  // --- Rueda del mouse ---
  wrapEl.addEventListener('wheel', (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 1 : -1;
    animateTo(Math.round(rotation) + delta, 400);
  }, { passive: false });

  // --- Teclado ---
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
    if (e.key === 'ArrowRight') animateTo(Math.round(rotation) + 1, 400);
    if (e.key === 'ArrowLeft')  animateTo(Math.round(rotation) - 1, 400);
  });

  // --- Modal ---
  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function openModal(c) {
    const filesHtml = c.files.length
      ? c.files.map(f => `
          <a class="file-item"
             href="data:application/octet-stream;base64,${f.data}"
             download="${f.name}">
            <div class="file-name">
              <span>📄</span><span>${f.name}</span>
            </div>
            <span class="download-btn">⬇ ${formatSize(f.size)}</span>
          </a>`).join('')
      : '<div class="empty">📭 Sin archivos todavía.<br>Sube materiales desde el panel lateral.</div>';

    modalContent.innerHTML = `
      <button class="close-btn" onclick="closeModal()">✕</button>
      <div class="modal-header">
        <div class="modal-icon">${c.icon}</div>
        <div>
          <h2>${c.title}</h2>
          <p>${c.desc}</p>
        </div>
      </div>
      <h3 class="files-title">📁 Archivos del curso</h3>
      ${filesHtml}`;
    modalEl.classList.add('open');
  }

  window.closeModal = function () { modalEl.classList.remove('open'); };
  modalEl.addEventListener('click', (e) => {
    if (e.target === modalEl) closeModal();
  });

  // --- Render inicial ---
  updateCards();
})();
</script>
</body>
</html>
"""

html = HTML_TEMPLATE.replace("__COURSES_JSON__", courses_json)
components.html(html, height=920, scrolling=False)
