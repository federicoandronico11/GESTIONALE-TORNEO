"""
app.py — Beach Volley Tournament Manager Pro v2
Avvia con: streamlit run app.py
"""
import streamlit as st
from data_manager import load_state, save_state
from theme_manager import load_theme_config, save_theme_config, inject_theme_css, render_personalization_page
from ranking_page import build_ranking_data
from fase_setup import render_setup
from fase_gironi import render_gironi
from fase_eliminazione import render_eliminazione
from fase_proclamazione import render_proclamazione
from segnapunti_live import render_segnapunti_live
from ranking_page import render_ranking_page
from incassi import render_incassi

# ─── CONFIGURAZIONE PAGINA ───────────────────────────────────────────────────

st.set_page_config(
    page_title="🏐 Beach Volley Tournament",
    page_icon="🏐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CARICAMENTO STATO ───────────────────────────────────────────────────────

if "state" not in st.session_state:
    st.session_state.state = load_state()
if "theme_cfg" not in st.session_state:
    st.session_state.theme_cfg = load_theme_config()
if "current_page" not in st.session_state:
    st.session_state.current_page = "torneo"
if "segnapunti_open" not in st.session_state:
    st.session_state.segnapunti_open = False

state = st.session_state.state
theme_cfg = st.session_state.theme_cfg

# ─── CSS TEMA ─────────────────────────────────────────────────────────────────

logo_html = inject_theme_css(theme_cfg)

# ─── HELPER: RENDER HEADER ────────────────────────────────────────────────────

def render_header():
    nome = state["torneo"]["nome"] or "Beach Volley"
    st.markdown(f"""
    <div class="tournament-header">
        {logo_html}
        <div class="tournament-title">🏐 {nome}</div>
        <div class="tournament-subtitle">Tournament Manager Pro</div>
    </div>
    """, unsafe_allow_html=True)
    
    fasi_ord = ["setup", "gironi", "eliminazione", "proclamazione"]
    fase_corrente = state["fase"]
    idx_corrente = fasi_ord.index(fase_corrente)
    fasi_label = [("setup","⚙️ Setup"), ("gironi","🔵 Gironi"), ("eliminazione","⚡ Eliminazione"), ("proclamazione","🏆 Finale")]
    
    html = '<div style="display:flex;justify-content:center;flex-wrap:wrap;gap:8px;margin-bottom:20px;">'
    for i, (k, label) in enumerate(fasi_label):
        if i < idx_corrente: css = "fase-badge done"; icon = "✓ "
        elif i == idx_corrente: css = "fase-badge active"; icon = ""
        else: css = "fase-badge"; icon = ""
        html += f'<span class="{css}">{icon}{label}</span>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    # ── LOGO E TITOLO ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;padding:16px 0 12px">
        {logo_html}
        <div style="font-family:var(--font-display);font-size:1.3rem;font-weight:800;
            letter-spacing:2px;text-transform:uppercase;color:var(--text-primary)">
            Beach Volley
        </div>
        <div style="color:var(--accent1);font-size:0.6rem;letter-spacing:4px;
            text-transform:uppercase;font-weight:700;margin-top:2px">
            Tournament Manager Pro
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border-color:var(--border);margin:0 0 12px'>", unsafe_allow_html=True)
    
    # ── SEZIONE: NAVIGAZIONE TORNEO ──────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;
        color:var(--accent1);font-weight:700;margin-bottom:8px;padding:0 2px">
        ⚡ NAVIGAZIONE TORNEO
    </div>
    """, unsafe_allow_html=True)
    
    fase_corrente = state["fase"]
    fasi_ord = ["setup", "gironi", "eliminazione", "proclamazione"]
    idx_attuale = fasi_ord.index(fase_corrente)
    
    nav_items = [
        ("setup", "⚙️  Setup & Iscrizioni"),
        ("gironi", "🔵  Fase a Gironi"),
        ("eliminazione", "⚡  Eliminazione Diretta"),
        ("proclamazione", "🏆  Proclamazione"),
    ]
    
    for i, (k, label) in enumerate(nav_items):
        disabled = i > idx_attuale
        if disabled:
            st.markdown(f"""
            <div style="padding:9px 14px;margin-bottom:4px;border-radius:var(--radius);
                border:1px solid var(--border);opacity:0.3;cursor:not-allowed;
                font-size:0.82rem;color:var(--text-secondary);background:var(--bg-card2)">
                🔒 {label}
            </div>
            """, unsafe_allow_html=True)
        else:
            is_active = (k == fase_corrente and st.session_state.current_page == "torneo")
            if is_active:
                st.markdown(f"""
                <div style="padding:9px 14px;margin-bottom:4px;border-radius:var(--radius);
                    background:var(--accent1);font-weight:700;font-size:0.82rem;
                    color:white;letter-spacing:0.5px;cursor:pointer">
                    ▶ {label}
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(label, key=f"nav_{k}", use_container_width=True):
                    state["fase"] = k
                    st.session_state.current_page = "torneo"
                    save_state(state)
                    st.rerun()
    
    st.markdown("<hr style='border-color:var(--border);margin:14px 0 12px'>", unsafe_allow_html=True)
    
    # ── SEZIONE: STRUMENTI ───────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;
        color:var(--accent1);font-weight:700;margin-bottom:8px;padding:0 2px">
        🛠️ STRUMENTI
    </div>
    """, unsafe_allow_html=True)
    
    # Segnapunti LIVE - pulsante prominente
    segna_label = "🔴 Chiudi Segnapunti" if st.session_state.segnapunti_open else "🏐 SEGNAPUNTI LIVE"
    segna_color = "var(--green)" if not st.session_state.segnapunti_open else "var(--accent1)"
    if st.button(segna_label, use_container_width=True, key="btn_segnapunti"):
        st.session_state.segnapunti_open = not st.session_state.segnapunti_open
        st.session_state.current_page = "torneo"
        st.rerun()
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🏅 Ranking", use_container_width=True, key="btn_ranking"):
            st.session_state.current_page = "ranking"
            st.rerun()
    with col_t2:
        if st.button("💰 Incassi", use_container_width=True, key="btn_incassi"):
            st.session_state.current_page = "incassi"
            st.rerun()
    
    if st.button("🎨 Personalizzazione Tema", use_container_width=True, key="btn_theme"):
        st.session_state.current_page = "theme"
        st.rerun()
    
    st.markdown("<hr style='border-color:var(--border);margin:14px 0 12px'>", unsafe_allow_html=True)
    
    # ── SEZIONE: INFO TORNEO ─────────────────────────────────────────────────
    if state["torneo"]["nome"]:
        st.markdown("""
        <div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;
            color:var(--accent1);font-weight:700;margin-bottom:8px;padding:0 2px">
            📋 TORNEO ATTIVO
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background:var(--bg-card2);border:1px solid var(--border);
            border-radius:var(--radius);padding:12px;margin-bottom:12px">
            <div style="font-family:var(--font-display);font-size:1.05rem;font-weight:700;
                color:var(--text-primary);margin-bottom:8px">{state['torneo']['nome']}</div>
            <div style="display:flex;flex-direction:column;gap:4px">
                <div style="font-size:0.78rem;color:var(--text-secondary)">📅 {state['torneo']['data']}</div>
                <div style="font-size:0.78rem;color:var(--text-secondary)">📊 {state['torneo']['tipo_tabellone']}</div>
                <div style="font-size:0.78rem;color:var(--text-secondary)">🏐 {state['torneo']['formato_set']} · Max {state['torneo']['punteggio_max']} pt</div>
                <div style="font-size:0.78rem;color:var(--text-secondary)">👥 {len(state['squadre'])} squadre</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ── SEZIONE: TOP RANKING ─────────────────────────────────────────────────
    ranking_data = build_ranking_data(state)
    if ranking_data:
        st.markdown("""
        <div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;
            color:var(--accent1);font-weight:700;margin-bottom:8px;padding:0 2px">
            🏅 TOP RANKING
        </div>
        """, unsafe_allow_html=True)
        
        medals = {0: "🥇", 1: "🥈", 2: "🥉"}
        ranking_html = '<div style="background:var(--bg-card2);border:1px solid var(--border);border-radius:var(--radius);padding:10px;margin-bottom:8px">'
        for i, a in enumerate(ranking_data[:5]):
            icon = medals.get(i, f"  #{i+1}")
            pts = a["rank_pts"]
            border = "border-bottom:1px solid var(--border);" if i < min(4, len(ranking_data)-1) else ""
            ranking_html += f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                padding:6px 0;{border}font-size:0.8rem">
                <span style="display:flex;gap:6px;align-items:center">
                    <span>{icon}</span>
                    <span style="color:var(--text-primary);font-weight:600">{a['nome']}</span>
                </span>
                <span style="color:var(--accent-gold);font-weight:800;
                    font-family:var(--font-display);font-size:0.9rem">{pts}</span>
            </div>"""
        ranking_html += '</div>'
        st.markdown(ranking_html, unsafe_allow_html=True)
        
        if st.button("→ Classifica Completa", key="btn_rank_full", use_container_width=True):
            st.session_state.current_page = "ranking"
            st.rerun()
    
    st.markdown("<hr style='border-color:var(--border);margin:14px 0 12px'>", unsafe_allow_html=True)
    
    # ── SEZIONE: SALVATAGGIO ─────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:0.6rem;letter-spacing:3px;text-transform:uppercase;
        color:var(--accent1);font-weight:700;margin-bottom:8px;padding:0 2px">
        💾 DATI
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Salva", use_container_width=True, key="btn_save"):
            save_state(state)
            st.toast("✅ Salvato!", icon="💾")
    with col2:
        if st.button("⚠️ Reset", use_container_width=True, key="btn_reset_toggle"):
            st.session_state.show_reset = not st.session_state.get("show_reset", False)
            st.rerun()
    
    if st.session_state.get("show_reset", False):
        st.warning("⚠️ Questa azione cancellerà il torneo corrente. Gli atleti saranno mantenuti.")
        if st.button("🔴 CONFERMA RESET", use_container_width=True, key="btn_reset_confirm"):
            from data_manager import empty_state
            atleti_bkp = state["atleti"]
            nuovo = empty_state()
            nuovo["atleti"] = atleti_bkp
            st.session_state.state = nuovo
            save_state(nuovo)
            st.session_state.show_reset = False
            st.session_state.current_page = "torneo"
            st.rerun()
    
    st.markdown("""
    <div style="font-size:0.65rem;color:var(--text-secondary);text-align:center;margin-top:4px">
        📁 beach_volley_data.json
    </div>
    """, unsafe_allow_html=True)


# ─── ROUTING PRINCIPALE ──────────────────────────────────────────────────────

page = st.session_state.current_page

# ── SEGNAPUNTI LIVE (overlay sopra tutto quando aperto) ──────────────────────
if st.session_state.segnapunti_open:
    st.markdown("""
    <div style="background:linear-gradient(90deg,rgba(232,0,45,0.1),transparent,rgba(232,0,45,0.1));
        border:1px solid var(--accent1);border-radius:8px;padding:8px 20px;
        margin-bottom:16px;text-align:center">
        <span style="font-family:var(--font-display);font-size:0.65rem;letter-spacing:4px;
            text-transform:uppercase;color:var(--accent1);font-weight:700">
            🔴 LIVE · SEGNAPUNTI ATTIVO
        </span>
    </div>
    """, unsafe_allow_html=True)
    render_segnapunti_live(state)
    st.divider()

# ── PAGINE ───────────────────────────────────────────────────────────────────

if page == "torneo":
    render_header()
    fase = state["fase"]
    if fase == "setup":
        render_setup(state)
    elif fase == "gironi":
        render_gironi(state)
    elif fase == "eliminazione":
        render_eliminazione(state)
    elif fase == "proclamazione":
        render_proclamazione(state)

elif page == "ranking":
    render_header()
    render_ranking_page(state)

elif page == "incassi":
    render_header()
    render_incassi(state)

elif page == "theme":
    render_personalization_page(theme_cfg)
    st.session_state.theme_cfg = theme_cfg

# ─── AUTOSAVE SILENZIOSO ─────────────────────────────────────────────────────
save_state(state)
