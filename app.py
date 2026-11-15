import base64
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# =========================================================
#  CONFIG
# =========================================================
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
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB por archivo

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
                files.append(
                    {
                        "name": f.name,
                        "size": f.stat().st_size,
                        "data": data,
                    }
                )
            except Exception:
                continue
    return files


# =========================================================
#  SIDEBAR – Subir / borrar archivos
# =========================================================
with st.sidebar:
    st.title("📤 Administrar archivos")
    st.caption("Sube material a cada curso")
    sel = st.selectbox(
        "Curso",
        list(COURSES.keys()),
        format_func=lambda k: COURSES[k]["title"],
    )
    uploaded = st.file_uploader(
        "Selecciona archivos",
        accept_multiple_files=True,
    )
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


# =========================================================
#  Datos para el componente HTML
# =========================================================
courses_data = []
for key, meta in COURSES.items():
    courses_data.append({"id": key, **meta, "files": get_files(key)})

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
    color: white;
    overflow-x: hidden;
    min-height: 100vh;
  }
  body { padding: 20px 10px 40px; }

  .header { text-align: center; margin-bottom: 10px; }
  .header h1 {
    font-size: clamp(1.4rem, 4vw, 2.4rem);
    margin: 0 0 6px;
    font-weight: 800;
    background: linear-gradient(90deg, #ff6b6b, #a29bfe, #00cec9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .header p { color: rgba(255,255,255,.6); margin: 0; font-size: .9rem; }

  .carousel-wrap {
    position: relative;
    width: 100%; max-width: 1100px;
    margin: 30px auto 0;
    height: 470px;
    perspective: 2000px;
  }
  .carousel {
    position: relative; width: 100%; height: 100%;
    display: flex; align-items: center; justify-content: center;
    transform-style: preserve-3d;
  }

  .card {
    position: absolute;
    width: 240px; height: 360px;
    border-radius: 22px;
    cursor: pointer;
    transition: transform .65s cubic-bezier(.34,1.56,.64,1),
                opacity .45s ease, filter .4s ease;
    transform-style: preserve-3d;
    box-shadow: 0 25px 60px rgba(0,0,0,.6);
    will-change: transform, opacity;
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
  /* Brillo superior */
  .card-inner::before {
    content: ""; position: absolute; inset: 0;
    background: radial-gradient(circle at 30% 15%, rgba(255,255,255,.35), transparent 55%);
    pointer-events: none;
  }
  /* Borde interior */
  .card-inner::after {
    content: ""; position: absolute; inset: 0;
    border-radius: 22px;
    border: 2px solid rgba(255,255,255,.25);
    pointer-events: none;
  }

  /* ---- POSICIONES DEL CARRUSEL ---- */
  .card.pos-0 {
    transform: translateX(0) scale(1.18) translateZ(100px);
    z-index: 10;
    filter: brightness(1.12);
  }
  .card.pos-0:hover {
    transform: translateX(0) scale(1.22) translateZ(120px);
    box-shadow: 0 35px 80px rgba(0,0,0,.75);
  }
  .card.pos-1 {
    transform: translateX(280px) scale(.8) rotateY(-22deg);
    z-index: 5; opacity: .78;
  }
  .card.pos-2 {
    transform: translateX(-280px) scale(.8) rotateY(22deg);
    z-index: 5; opacity: .78;
  }

  .suit { position: absolute; font-size: 1.7rem; opacity: .32; color: #fff; }
  .suit.tl { top: 14px; left: 18px; }
  .suit.tr { top: 14px; right: 18px; }
  .suit.bl { bottom: 14px; left: 18px; transform: rotate(180deg); }
  .suit.br { bottom: 14px; right: 18px; transform: rotate(180deg); }

  .icon {
    font-size: 3.8rem;
    margin-bottom: 12px;
    filter: drop-shadow(0 8px 20px rgba(0,0,0,.4));
    position: relative; z-index: 1;
    animation: float 3.4s ease-in-out infinite;
  }
  @keyframes float {
    0%,100% { transform: translateY(0); }
    50%     { transform: translateY(-8px); }
  }

  .card h2 {
    font-size: 1.2rem; margin: 0 0 8px;
    line-height: 1.2; font-weight: 800;
    text-shadow: 0 2px 12px rgba(0,0,0,.4);
    position: relative; z-index: 1;
  }
  .card p {
    font-size: .78rem; margin: 0 0 14px;
    opacity: .93; line-height: 1.3;
    position: relative; z-index: 1;
  }
  .badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    background: rgba(255,255,255,.22);
    backdrop-filter: blur(8px);
    font-size: .7rem; font-weight: 700;
    border: 1px solid rgba(255,255,255,.35);
    position: relative; z-index: 1;
  }
  .tap-hint {
    font-size: .65rem; opacity: .85;
    margin-top: 10px;
    position: relative; z-index: 1;
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%,100% { opacity: .6; }
    50%     { opacity: 1; }
  }

  /* ---- DOTS ---- */
  .dots {
    display: flex; justify-content: center;
    gap: 12px; margin-top: 24px;
  }
  .dot {
    width: 11px; height: 11px; border-radius: 50%;
    background: rgba(255,255,255,.25);
    cursor: pointer; transition: all .3s;
  }
  .dot.active {
    background: linear-gradient(90deg, #ff6b6b, #a29bfe);
    transform: scale(1.4);
    box-shadow: 0 0 15px rgba(162,155,254,.7);
  }

  /* ---- MODAL ---- */
  .modal {
    position: fixed; inset: 0;
    background: rgba(5,5,20,.93);
    backdrop-filter: blur(14px);
    display: none;
    align-items: center; justify-content: center;
    z-index: 999;
    padding: 20px;
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
    display: flex; align-items: center;
    gap: 15px; margin-bottom: 16px;
    padding-right: 45px;
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
    font-size: .9rem; overflow: hidden; flex: 1;
    min-width: 0;
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

  .empty {
    text-align: center; padding: 40px 20px;
    opacity: .5; font-style: italic;
  }

  /* ---- RESPONSIVE ---- */
  @media (max-width: 700px) {
    .carousel-wrap { height: 410px; }
    .card { width: 200px; height: 300px; }
    .card.pos-0 { transform: translateX(0) scale(1.1); }
    .card.pos-1 { transform: translateX(130px) scale(.68) rotateY(-20deg); }
    .card.pos-2 { transform: translateX(-130px) scale(.68) rotateY(20deg); }
    .icon { font-size: 3rem; }
    .card h2 { font-size: 1.05rem; }
    .card p { font-size: .72rem; }
    .modal-content { padding: 22px; }
  }
  @media (max-width: 400px) {
    .card { width: 170px; height: 260px; }
    .card.pos-1 { transform: translateX(100px) scale(.6) rotateY(-20deg); }
    .card.pos-2 { transform: translateX(-100px) scale(.6) rotateY(20deg); }
  }
</style>
</head>
<body>

<div class="header">
  <h1>🎓 Cursos de Física &amp; Biofísica</h1>
  <p>Desliza o toca las cartas para explorar el material</p>
</div>

<div class="carousel-wrap">
  <div class="carousel" id="carousel"></div>
</div>

<div class="dots" id="dots"></div>

<div class="modal" id="modal">
  <div class="modal-content" id="modalContent"></div>
</div>

<script id="courses-data" type="application/json">__COURSES_JSON__</script>
<script>
  const courses = JSON.parse(document.getElementById('courses-data').textContent);
  let current = 0;
  const carousel = document.getElementById('carousel');
  const dotsEl   = document.getElementById('dots');
  const modal    = document.getElementById('modal');
  const modalContent = document.getElementById('modalContent');

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  function render() {
    carousel.innerHTML = '';
    dotsEl.innerHTML   = '';

    courses.forEach((c, i) => {
      const pos = (i - current + courses.length) % courses.length;
      const bg  = `linear-gradient(150deg, ${c.color1}, ${c.color2}, ${c.color3})`;

      const card = document.createElement('div');
      card.className = `card pos-${pos}`;
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
          ${pos === 0 ? '<div class="tap-hint">👆 Toca para abrir</div>' : ''}
        </div>`;

      card.addEventListener('click', () => {
        if (pos === 0) {
          openModal(c);
        } else {
          current = i;
          render();
        }
      });
      carousel.appendChild(card);

      const dot = document.createElement('div');
      dot.className = 'dot' + (pos === 0 ? ' active' : '');
      dot.addEventListener('click', () => { current = i; render(); });
      dotsEl.appendChild(dot);
    });
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
    modal.classList.add('open');
  }

  function closeModal() { modal.classList.remove('open'); }

  modal.addEventListener('click', e => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
    if (e.key === 'ArrowRight') { current = (current + 1) % courses.length; render(); }
    if (e.key === 'ArrowLeft')  { current = (current - 1 + courses.length) % courses.length; render(); }
  });

  // Gestos táctiles (swipe)
  let touchStartX = 0;
  carousel.addEventListener('touchstart', e => {
    touchStartX = e.touches[0].clientX;
  }, { passive: true });
  carousel.addEventListener('touchend', e => {
    const dx = e.changedTouches[0].clientX - touchStartX;
    if (Math.abs(dx) > 50) {
      current = (current + (dx < 0 ? 1 : -1) + courses.length) % courses.length;
      render();
    }
  });

  render();
</script>
</body>
</html>
"""

html = HTML_TEMPLATE.replace("__COURSES_JSON__", courses_json)
components.html(html, height=900, scrolling=False)
