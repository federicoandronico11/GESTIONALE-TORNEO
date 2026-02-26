"""
theme_manager.py — Sistema temi: 5 stili grafici + colori custom + logo
"""
import streamlit as st
import json, base64
from pathlib import Path

THEMES = {
    "Futuristico": {
        "bg_primary": "#050510",
        "bg_card": "#0d0d20",
        "bg_card2": "#141428",
        "accent1": "#00f5ff",
        "accent2": "#7b2fff",
        "accent_gold": "#ffd700",
        "text_primary": "#e0e8ff",
        "text_secondary": "#7080a0",
        "border": "#1a1a40",
        "green": "#00ff88",
        "font_display": "Orbitron",
        "font_body": "Exo 2",
        "font_url": "https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;600&display=swap",
        "card_radius": "4px",
        "extra_css": """
        .match-card { border-left: 3px solid var(--accent1) !important; }
        .tournament-header { background: linear-gradient(135deg, #050510, #0d1030, #050510) !important; border-bottom: 2px solid var(--accent1) !important; }
        .tournament-title { color: var(--accent1) !important; text-shadow: 0 0 30px rgba(0,245,255,0.5) !important; }
        .stButton > button { background: transparent !important; border: 1px solid var(--accent1) !important; color: var(--accent1) !important; }
        .stButton > button:hover { background: var(--accent1) !important; color: #000 !important; box-shadow: 0 0 20px var(--accent1) !important; }
        """
    },
    "Stile FC 26": {
        "bg_primary": "#0a0e1a",
        "bg_card": "#111827",
        "bg_card2": "#1a2235",
        "accent1": "#00d4aa",
        "accent2": "#ff6b35",
        "accent_gold": "#ffc72c",
        "text_primary": "#ffffff",
        "text_secondary": "#8899bb",
        "border": "#1e2d45",
        "green": "#00d4aa",
        "font_display": "Bebas Neue",
        "font_body": "Rajdhani",
        "font_url": "https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@400;500;600;700&display=swap",
        "card_radius": "8px",
        "extra_css": """
        .match-card-header { background: var(--accent1) !important; color: #000 !important; }
        .tournament-header { background: linear-gradient(135deg, #0a0e1a 0%, #162040 50%, #0a0e1a 100%) !important; border-bottom: 3px solid var(--accent1) !important; }
        .fase-badge.active { background: var(--accent1) !important; border-color: var(--accent1) !important; color: #000 !important; }
        .stButton > button { background: var(--accent1) !important; color: #000 !important; font-weight: 800 !important; }
        """
    },
    "Minimal": {
        "bg_primary": "#f5f5f0",
        "bg_card": "#ffffff",
        "bg_card2": "#f0f0eb",
        "accent1": "#1a1a1a",
        "accent2": "#666666",
        "accent_gold": "#c9a227",
        "text_primary": "#1a1a1a",
        "text_secondary": "#888888",
        "border": "#e0e0d8",
        "green": "#2d6a4f",
        "font_display": "DM Serif Display",
        "font_body": "DM Sans",
        "font_url": "https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap",
        "card_radius": "2px",
        "extra_css": """
        html, body, [class*="css"] { background-color: #f5f5f0 !important; color: #1a1a1a !important; }
        .match-card { border: 1px solid #ddd !important; box-shadow: none !important; }
        .tournament-header { background: #ffffff !important; border-bottom: 2px solid #1a1a1a !important; }
        .stButton > button { background: #1a1a1a !important; color: white !important; border-radius: 0 !important; }
        [data-testid="stSidebar"] { background: #fff !important; border-right: 1px solid #e0e0d8 !important; }
        """
    },
    "Retro Gaming": {
        "bg_primary": "#0f0f23",
        "bg_card": "#1a1a2e",
        "bg_card2": "#16213e",
        "accent1": "#ff6b6b",
        "accent2": "#ffd93d",
        "accent_gold": "#ffd93d",
        "text_primary": "#e8e8e8",
        "text_secondary": "#7f7f9f",
        "border": "#2a2a4a",
        "green": "#6bcb77",
        "font_display": "Press Start 2P",
        "font_body": "VT323",
        "font_url": "https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap",
        "card_radius": "0px",
        "extra_css": """
        * { image-rendering: pixelated !important; }
        .tournament-title { font-size: 1.8rem !important; letter-spacing: 2px !important; }
        .match-card { border: 3px solid var(--accent1) !important; border-radius: 0 !important; box-shadow: 4px 4px 0 var(--accent2) !important; }
        .stButton > button { border-radius: 0 !important; border: 3px solid var(--accent1) !important; background: #0f0f23 !important; color: var(--accent1) !important; box-shadow: 3px 3px 0 var(--accent1) !important; font-family: 'Press Start 2P', monospace !important; font-size: 0.6rem !important; }
        .stButton > button:hover { box-shadow: none !important; transform: translate(3px, 3px) !important; }
        .fase-badge { border-radius: 0 !important; border: 2px solid var(--accent2) !important; }
        """
    },
    "Dynamic": {
        "bg_primary": "#0a0a0f",
        "bg_card": "#13131a",
        "bg_card2": "#1a1a24",
        "accent1": "#e8002d",
        "accent2": "#0070f3",
        "accent_gold": "#ffd700",
        "text_primary": "#ffffff",
        "text_secondary": "#a0a0b0",
        "border": "#2a2a3a",
        "green": "#00c851",
        "font_display": "Barlow Condensed",
        "font_body": "Barlow",
        "font_url": "https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;800&family=Barlow:wght@400;500;600&display=swap",
        "card_radius": "12px",
        "extra_css": ""
    }
}

THEME_FILE = "beach_volley_theme.json"

def load_theme_config():
    if Path(THEME_FILE).exists():
        with open(THEME_FILE, "r") as f:
            return json.load(f)
    return {
        "theme_name": "Dynamic",
        "color_primary": "#e8002d",
        "color_secondary": "#0070f3",
        "color_detail": "#ffd700",
        "logo_b64": None,
        "logo_name": None,
    }

def save_theme_config(cfg):
    with open(THEME_FILE, "w") as f:
        json.dump(cfg, f)

def get_active_theme(cfg):
    t = THEMES.get(cfg["theme_name"], THEMES["Dynamic"]).copy()
    # Override con colori custom se modificati
    t["accent1"] = cfg.get("color_primary", t["accent1"])
    t["accent2"] = cfg.get("color_secondary", t["accent2"])
    t["accent_gold"] = cfg.get("color_detail", t["accent_gold"])
    return t

def inject_theme_css(cfg):
    t = get_active_theme(cfg)
    logo_b64 = cfg.get("logo_b64")
    
    # Logo HTML
    if logo_b64:
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:60px;object-fit:contain;margin-bottom:8px">'
    else:
        logo_html = '<div style="font-size:3rem">🏐</div>'
    
    css = f"""
    <style>
    @import url('{t["font_url"]}');
    
    :root {{
        --bg-primary: {t["bg_primary"]};
        --bg-card: {t["bg_card"]};
        --bg-card2: {t["bg_card2"]};
        --accent1: {t["accent1"]};
        --accent-red: {t["accent1"]};
        --accent-blue: {t["accent2"]};
        --accent-gold: {t["accent_gold"]};
        --text-primary: {t["text_primary"]};
        --text-secondary: {t["text_secondary"]};
        --border: {t["border"]};
        --green: {t["green"]};
        --radius: {t["card_radius"]};
        --font-display: '{t["font_display"]}', sans-serif;
        --font-body: '{t["font_body"]}', sans-serif;
    }}

    html, body, [class*="css"] {{
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: var(--font-body) !important;
    }}

    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 1rem !important; max-width: 1200px !important; }}

    .tournament-header {{
        background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-card2) 50%, var(--bg-primary) 100%);
        border-bottom: 3px solid var(--accent1);
        padding: 20px 30px;
        text-align: center;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }}
    .tournament-header::before {{
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 300%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent);
        animation: shimmer 4s infinite;
    }}
    @keyframes shimmer {{ to {{ left: 100%; }} }}
    .tournament-title {{
        font-family: var(--font-display) !important;
        font-size: 2.6rem !important;
        font-weight: 800 !important;
        letter-spacing: 3px !important;
        text-transform: uppercase !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
    }}
    .tournament-subtitle {{
        color: var(--accent1);
        font-size: 0.8rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        font-weight: 600;
        margin-top: 4px;
    }}

    .fase-badge {{
        display: inline-flex; align-items: center; gap: 8px;
        background: var(--bg-card2); border: 1px solid var(--border);
        border-radius: 20px; padding: 6px 16px;
        font-size: 0.75rem; font-weight: 600; letter-spacing: 2px;
        text-transform: uppercase; color: var(--text-secondary);
        margin: 4px; transition: all 0.3s;
    }}
    .fase-badge.active {{ background: var(--accent1); border-color: var(--accent1); color: white; }}
    .fase-badge.done {{ background: var(--bg-card2); border-color: var(--green); color: var(--green); }}

    .match-card {{
        background: var(--bg-card); border: 1px solid var(--border);
        border-radius: var(--radius); margin-bottom: 12px; overflow: hidden;
        transition: border-color 0.2s;
    }}
    .match-card:hover {{ border-color: #555; }}
    .match-card.confirmed {{ border-left: 4px solid var(--green); }}
    .match-card-header {{
        background: var(--bg-card2); padding: 8px 16px;
        font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase;
        color: var(--text-secondary); font-weight: 600;
        font-family: var(--font-display);
    }}
    .match-body {{ padding: 16px; display: flex; align-items: center; gap: 12px; }}
    .team-side {{ flex: 1; text-align: center; }}
    .team-name {{ font-family: var(--font-display); font-size: 1.4rem; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }}
    .team-red .team-name {{ color: var(--accent1); }}
    .team-blue .team-name {{ color: var(--accent2); }}
    .team-players {{ font-size: 0.75rem; color: var(--text-secondary); margin-top: 4px; }}
    .score-center {{ text-align: center; min-width: 100px; }}
    .score-sets {{ font-family: var(--font-display); font-size: 3rem; font-weight: 800; color: white; line-height: 1; }}
    .score-parziale {{ font-size: 0.75rem; color: var(--text-secondary); margin-top: 4px; }}

    .rank-table {{ width: 100%; border-collapse: collapse; }}
    .rank-table th {{
        background: var(--bg-card2); color: var(--text-secondary);
        font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase;
        padding: 10px 14px; text-align: center; border-bottom: 1px solid var(--border);
        font-family: var(--font-display);
    }}
    .rank-table td {{ padding: 12px 14px; text-align: center; border-bottom: 1px solid var(--border); font-size: 0.9rem; }}
    .rank-table tr:hover td {{ background: var(--bg-card2); }}
    .rank-pos {{ font-family: var(--font-display); font-weight: 800; font-size: 1.2rem; }}
    .rank-pos.gold {{ color: var(--accent-gold); }}
    .rank-pos.silver {{ color: #c0c0c0; }}
    .rank-pos.bronze {{ color: #cd7f32; }}

    .podio-container {{ display: flex; align-items: flex-end; justify-content: center; gap: 12px; padding: 30px 0; }}
    .podio-step {{ text-align: center; border-radius: var(--radius) var(--radius) 0 0; padding: 20px 24px 16px; min-width: 150px; }}
    .podio-1 {{ background: linear-gradient(180deg, #b8860b, var(--accent-gold)); height: 180px; display: flex; flex-direction: column; justify-content: flex-end; }}
    .podio-2 {{ background: linear-gradient(180deg, #808080, #c0c0c0); height: 140px; display: flex; flex-direction: column; justify-content: flex-end; }}
    .podio-3 {{ background: linear-gradient(180deg, #8b4513, #cd7f32); height: 110px; display: flex; flex-direction: column; justify-content: flex-end; }}
    .podio-rank {{ font-family: var(--font-display); font-size: 2rem; font-weight: 800; color: rgba(0,0,0,0.7); }}
    .podio-name {{ font-weight: 700; font-size: 0.9rem; color: rgba(0,0,0,0.9); text-transform: uppercase; letter-spacing: 1px; }}

    .winner-banner {{
        background: linear-gradient(135deg, #b8860b, var(--accent-gold), #b8860b);
        border-radius: var(--radius); padding: 30px; text-align: center;
        margin: 20px 0; animation: pulse-gold 2s ease-in-out infinite;
    }}
    @keyframes pulse-gold {{
        0%, 100% {{ box-shadow: 0 0 20px rgba(255,215,0,0.4); }}
        50% {{ box-shadow: 0 0 50px rgba(255,215,0,0.8); }}
    }}
    .winner-title {{ font-family: var(--font-display); font-size: 1rem; letter-spacing: 4px; text-transform: uppercase; color: rgba(0,0,0,0.7); font-weight: 600; }}
    .winner-name {{ font-family: var(--font-display); font-size: 3rem; font-weight: 800; color: #000; text-transform: uppercase; letter-spacing: 2px; }}
    .winner-players {{ color: rgba(0,0,0,0.8); font-size: 1rem; font-weight: 600; }}

    .career-card {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 24px; margin-bottom: 16px; }}
    .career-name {{ font-family: var(--font-display); font-size: 2rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; }}
    .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 12px; margin-top: 16px; }}
    .stat-box {{ background: var(--bg-card2); border-radius: var(--radius); padding: 12px; text-align: center; }}
    .stat-value {{ font-family: var(--font-display); font-size: 1.8rem; font-weight: 700; color: var(--accent2); }}
    .stat-label {{ font-size: 0.65rem; letter-spacing: 1.5px; text-transform: uppercase; color: var(--text-secondary); margin-top: 4px; }}

    /* SIDEBAR ENHANCED */
    [data-testid="stSidebar"] {{
        background: var(--bg-card) !important;
        border-right: 2px solid var(--border) !important;
    }}
    [data-testid="stSidebar"] .sidebar-section {{
        background: var(--bg-card2);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 12px;
        margin-bottom: 12px;
    }}
    [data-testid="stSidebar"] .sidebar-section-title {{
        font-family: var(--font-display);
        font-size: 0.65rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--accent1);
        font-weight: 700;
        margin-bottom: 10px;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--border);
    }}

    .stButton > button {{
        background: var(--accent1) !important; color: white !important;
        border: none !important; border-radius: var(--radius) !important;
        font-family: var(--font-display) !important; font-weight: 700 !important;
        letter-spacing: 1.5px !important; text-transform: uppercase !important;
        font-size: 0.85rem !important; padding: 10px 20px !important;
        transition: all 0.2s !important;
    }}
    .stButton > button:hover {{ opacity: 0.85 !important; transform: translateY(-1px) !important; }}

    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {{
        background: var(--bg-card2) !important; border: 1px solid var(--border) !important;
        color: var(--text-primary) !important; border-radius: var(--radius) !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{ background: transparent !important; gap: 4px !important; }}
    .stTabs [data-baseweb="tab"] {{
        background: var(--bg-card2) !important; color: var(--text-secondary) !important;
        border-radius: var(--radius) var(--radius) 0 0 !important;
        border: 1px solid var(--border) !important;
        font-family: var(--font-display) !important;
        font-weight: 600 !important; letter-spacing: 1px !important; text-transform: uppercase !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: var(--accent1) !important; color: white !important;
        border-color: var(--accent1) !important;
    }}

    [data-testid="metric-container"] {{
        background: var(--bg-card) !important; border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important; padding: 12px !important;
    }}
    hr {{ border-color: var(--border) !important; }}

    /* SEGNAPUNTI LIVE */
    .segnapunti-overlay {{
        background: var(--bg-primary);
        border: 2px solid var(--accent1);
        border-radius: 16px;
        padding: 30px;
        margin-bottom: 20px;
    }}
    .segnapunti-score {{
        font-family: var(--font-display);
        font-size: 7rem;
        font-weight: 900;
        line-height: 1;
        text-align: center;
    }}
    .segnapunti-team {{
        font-family: var(--font-display);
        font-size: 2rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-align: center;
    }}
    .segnapunti-btn {{
        font-size: 3rem;
        background: var(--bg-card2);
        border: 2px solid var(--border);
        border-radius: var(--radius);
        cursor: pointer;
        transition: all 0.1s;
        padding: 10px 30px;
    }}

    {t.get("extra_css", "")}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    return logo_html


def render_personalization_page(cfg):
    """Pagina completa di personalizzazione tema."""
    st.markdown("## 🎨 Personalizzazione App")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🖼️ Tema Grafico")
        
        tema_idx = list(THEMES.keys()).index(cfg.get("theme_name", "Dynamic"))
        tema_scelto = st.selectbox(
            "Scegli Tema",
            list(THEMES.keys()),
            index=tema_idx,
            format_func=lambda x: {
                "Futuristico": "🚀 Futuristico",
                "Stile FC 26": "⚽ Stile FC 26",
                "Minimal": "⬜ Minimal",
                "Retro Gaming": "🕹️ Retro Gaming",
                "Dynamic": "⚡ Dynamic (DAZN)",
            }.get(x, x)
        )
        cfg["theme_name"] = tema_scelto
        
        st.markdown("### 🎨 Colori Custom")
        c1, c2, c3 = st.columns(3)
        with c1:
            cfg["color_primary"] = st.color_picker("🔴 Colore Primario", cfg.get("color_primary", "#e8002d"))
        with c2:
            cfg["color_secondary"] = st.color_picker("🔵 Colore Secondario", cfg.get("color_secondary", "#0070f3"))
        with c3:
            cfg["color_detail"] = st.color_picker("✨ Colore Dettagli", cfg.get("color_detail", "#ffd700"))
    
    with col2:
        st.markdown("### 🖼️ Logo Personalizzato")
        
        if cfg.get("logo_b64"):
            import base64
            st.markdown("**Logo attuale:**")
            st.markdown(f'<img src="data:image/png;base64,{cfg["logo_b64"]}" style="max-height:80px;border-radius:8px">', unsafe_allow_html=True)
            if st.button("🗑️ Rimuovi Logo"):
                cfg["logo_b64"] = None
                cfg["logo_name"] = None
                save_theme_config(cfg)
                st.rerun()
        
        logo_file = st.file_uploader("Carica Logo (PNG/JPG)", type=["png","jpg","jpeg","webp"])
        if logo_file:
            import base64
            b64 = base64.b64encode(logo_file.read()).decode()
            cfg["logo_b64"] = b64
            cfg["logo_name"] = logo_file.name
            st.success(f"✅ Logo '{logo_file.name}' caricato!")
        
        # Anteprima tema
        st.markdown("### 👁️ Anteprima Tema")
        t = get_active_theme(cfg)
        st.markdown(f"""
        <div style="background:{t['bg_primary']};border:1px solid {t['border']};border-radius:{t['card_radius']};padding:20px;text-align:center">
            <div style="font-family:'{t['font_display']}',sans-serif;font-size:1.5rem;font-weight:800;color:{t['accent1']};letter-spacing:2px;text-transform:uppercase">
                🏐 BEACH VOLLEY
            </div>
            <div style="display:flex;justify-content:center;gap:16px;margin-top:12px">
                <div style="background:{t['bg_card']};border:1px solid {t['border']};border-radius:{t['card_radius']};padding:10px 20px">
                    <span style="color:{t['accent1']};font-weight:700">TEAM RED</span>
                    <span style="color:{t['text_secondary']};margin:0 8px">vs</span>
                    <span style="color:{t['accent2']};font-weight:700">TEAM BLU</span>
                </div>
            </div>
            <div style="display:flex;justify-content:center;gap:8px;margin-top:8px">
                <span style="background:{t['accent1']};color:white;padding:4px 12px;border-radius:{t['card_radius']};font-size:0.75rem;font-weight:700">PRIMARIO</span>
                <span style="background:{t['accent2']};color:white;padding:4px 12px;border-radius:{t['card_radius']};font-size:0.75rem;font-weight:700">SECONDARIO</span>
                <span style="background:{t['accent_gold']};color:#000;padding:4px 12px;border-radius:{t['card_radius']};font-size:0.75rem;font-weight:700">DETTAGLI</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    if st.button("💾 SALVA TEMA", use_container_width=True, type="primary"):
        save_theme_config(cfg)
        st.success("✅ Tema salvato! Ricarica la pagina per vedere le modifiche complete.")
        st.rerun()
