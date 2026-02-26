"""
segnapunti_live.py — Segnapunti LIVE gigante a schermo intero
"""
import streamlit as st
from data_manager import (
    save_state, get_squadra_by_id, aggiorna_classifica_squadra
)


def render_segnapunti_live(state):
    """Segnapunti a schermo intero con pulsanti giganti."""
    
    st.markdown("""
    <div style="text-align:center;margin-bottom:10px">
        <span style="font-family:var(--font-display);font-size:0.7rem;letter-spacing:4px;
            text-transform:uppercase;color:var(--accent1);font-weight:700">
            🔴 SEGNAPUNTI LIVE
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Selezione partita attiva
    partite_disponibili = _get_partite_disponibili(state)
    
    if not partite_disponibili:
        st.info("⏳ Nessuna partita disponibile. Avvia il torneo e vai alla fase Gironi o Eliminazione.")
        return
    
    nomi_partite = [p["label"] for p in partite_disponibili]
    idx_sel = st.session_state.get("segnapunti_partita_idx", 0)
    
    sel = st.selectbox(
        "Seleziona Partita",
        range(len(nomi_partite)),
        format_func=lambda i: nomi_partite[i],
        index=min(idx_sel, len(nomi_partite)-1),
        key="segnapunti_sel"
    )
    st.session_state.segnapunti_partita_idx = sel
    
    partita_info = partite_disponibili[sel]
    partita = partita_info["partita"]
    
    if partita["confermata"]:
        sq_v = get_squadra_by_id(state, partita["vincitore"])
        st.success(f"✅ Partita conclusa. Vincitore: **{sq_v['nome'] if sq_v else '?'}**")
        return
    
    sq1 = get_squadra_by_id(state, partita["sq1"])
    sq2 = get_squadra_by_id(state, partita["sq2"])
    
    # Inizializza stato live nella session
    key_base = f"live_{partita['id']}"
    if f"{key_base}_s1" not in st.session_state:
        st.session_state[f"{key_base}_s1"] = 0  # set vinti sq1
        st.session_state[f"{key_base}_s2"] = 0  # set vinti sq2
        st.session_state[f"{key_base}_p1"] = 0  # punti set corrente sq1
        st.session_state[f"{key_base}_p2"] = 0  # punti set corrente sq2
        st.session_state[f"{key_base}_battuta"] = 1
        st.session_state[f"{key_base}_punteggi_sets"] = []
    
    s1 = st.session_state[f"{key_base}_s1"]
    s2 = st.session_state[f"{key_base}_s2"]
    p1 = st.session_state[f"{key_base}_p1"]
    p2 = st.session_state[f"{key_base}_p2"]
    battuta = st.session_state[f"{key_base}_battuta"]
    pmax = state["torneo"]["punteggio_max"]
    formato = state["torneo"]["formato_set"]
    
    # ─── SCOREBOARD GIGANTE ──────────────────────────────────────────────────
    
    battuta_icon1 = "🏐" if battuta == 1 else ""
    battuta_icon2 = "🏐" if battuta == 2 else ""
    
    st.markdown(f"""
    <div class="segnapunti-overlay">
        <!-- INTESTAZIONE SET -->
        <div style="text-align:center;margin-bottom:16px">
            <span style="background:var(--bg-card2);padding:6px 20px;border-radius:20px;
                font-size:0.75rem;letter-spacing:3px;text-transform:uppercase;color:var(--text-secondary);font-family:var(--font-display)">
                SET CORRENTE · {s1} – {s2}
            </span>
        </div>
        
        <!-- SCORE PRINCIPALE -->
        <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:20px;align-items:center">
            <!-- SQUADRA 1 -->
            <div style="text-align:center">
                <div class="segnapunti-team" style="color:var(--accent1)">{battuta_icon1} {sq1['nome'] if sq1 else '?'}</div>
                <div style="color:var(--text-secondary);font-size:0.8rem;margin:4px 0 16px">
                    {_players_str(state, sq1)}
                </div>
                <div class="segnapunti-score" style="color:var(--accent1)">{p1}</div>
            </div>
            
            <!-- DIVISORE -->
            <div style="text-align:center">
                <div style="font-family:var(--font-display);font-size:0.7rem;letter-spacing:3px;
                    color:var(--text-secondary);text-transform:uppercase">VS</div>
                <div style="font-size:1.5rem;margin:10px 0;color:var(--text-secondary)">|</div>
                <div style="font-size:0.7rem;color:var(--text-secondary);letter-spacing:2px">
                    MAX {pmax}
                </div>
            </div>
            
            <!-- SQUADRA 2 -->
            <div style="text-align:center">
                <div class="segnapunti-team" style="color:var(--accent2)">{battuta_icon2} {sq2['nome'] if sq2 else '?'}</div>
                <div style="color:var(--text-secondary);font-size:0.8rem;margin:4px 0 16px">
                    {_players_str(state, sq2)}
                </div>
                <div class="segnapunti-score" style="color:var(--accent2)">{p2}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ─── PULSANTI GRANDI ─────────────────────────────────────────────────────
    
    col1, col_mid, col2 = st.columns([5, 1, 5])
    
    with col1:
        st.markdown(f"<div style='text-align:center;color:var(--accent1);font-family:var(--font-display);font-weight:700;font-size:1.1rem;margin-bottom:8px'>{sq1['nome'] if sq1 else '?'}</div>", unsafe_allow_html=True)
        c1a, c1b, c1c = st.columns([2, 2, 1])
        with c1a:
            if st.button("➕ PUNTO", key=f"{key_base}_add1", use_container_width=True):
                st.session_state[f"{key_base}_p1"] += 1
                st.session_state[f"{key_base}_battuta"] = 1
                _check_set_win(state, key_base, pmax, formato)
                st.rerun()
        with c1b:
            if st.button("➖ Annulla", key=f"{key_base}_sub1", use_container_width=True):
                st.session_state[f"{key_base}_p1"] = max(0, st.session_state[f"{key_base}_p1"] - 1)
                st.rerun()
        with c1c:
            if st.button("🏐", key=f"{key_base}_batt1", use_container_width=True, help="Assegna battuta"):
                st.session_state[f"{key_base}_battuta"] = 1
                st.rerun()
    
    with col_mid:
        st.markdown("<div style='text-align:center;padding-top:40px;color:var(--text-secondary)'>|</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<div style='text-align:center;color:var(--accent2);font-family:var(--font-display);font-weight:700;font-size:1.1rem;margin-bottom:8px'>{sq2['nome'] if sq2 else '?'}</div>", unsafe_allow_html=True)
        c2a, c2b, c2c = st.columns([2, 2, 1])
        with c2a:
            if st.button("➕ PUNTO", key=f"{key_base}_add2", use_container_width=True):
                st.session_state[f"{key_base}_p2"] += 1
                st.session_state[f"{key_base}_battuta"] = 2
                _check_set_win(state, key_base, pmax, formato)
                st.rerun()
        with c2b:
            if st.button("➖ Annulla", key=f"{key_base}_sub2", use_container_width=True):
                st.session_state[f"{key_base}_p2"] = max(0, st.session_state[f"{key_base}_p2"] - 1)
                st.rerun()
        with c2c:
            if st.button("🏐", key=f"{key_base}_batt2", use_container_width=True, help="Assegna battuta"):
                st.session_state[f"{key_base}_battuta"] = 2
                st.rerun()
    
    # ─── SET HISTORY ─────────────────────────────────────────────────────────
    
    sets_history = st.session_state.get(f"{key_base}_punteggi_sets", [])
    if sets_history:
        st.markdown("**Set Giocati:**")
        for i, (a, b) in enumerate(sets_history):
            winner = sq1["nome"] if a > b else sq2["nome"]
            col = "var(--accent1)" if a > b else "var(--accent2)"
            st.markdown(f"""
            <span style="background:var(--bg-card2);border-radius:4px;padding:4px 12px;
                margin-right:8px;font-size:0.85rem">
                Set {i+1}: <strong style="color:var(--accent1)">{a}</strong> – 
                <strong style="color:var(--accent2)">{b}</strong>
                <span style="color:{col};font-size:0.75rem;margin-left:6px">({winner})</span>
            </span>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # ─── AZIONI FINALI ───────────────────────────────────────────────────────
    
    col_a, col_b, col_c = st.columns([2, 2, 2])
    
    with col_a:
        if st.button("🔄 Reset Set Corrente", use_container_width=True):
            st.session_state[f"{key_base}_p1"] = 0
            st.session_state[f"{key_base}_p2"] = 0
            st.rerun()
    
    with col_b:
        if st.button("🔄 Reset TUTTO", use_container_width=True):
            for k in [f"{key_base}_s1", f"{key_base}_s2", f"{key_base}_p1",
                      f"{key_base}_p2", f"{key_base}_battuta", f"{key_base}_punteggi_sets"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
    
    with col_c:
        sets_giocati = st.session_state.get(f"{key_base}_punteggi_sets", [])
        if sets_giocati and (s1 > s2 or s2 > s1):
            if st.button("📤 INVIA AL TABELLONE ✅", use_container_width=True):
                _invia_al_tabellone(state, partita, key_base)
                save_state(state)
                st.success("✅ Dati inviati al tabellone!")
                st.rerun()


def _check_set_win(state, key_base, pmax, formato):
    """Controlla se un set è stato vinto e aggiorna contatori."""
    p1 = st.session_state[f"{key_base}_p1"]
    p2 = st.session_state[f"{key_base}_p2"]
    s1 = st.session_state[f"{key_base}_s1"]
    s2 = st.session_state[f"{key_base}_s2"]
    
    set_corrente = s1 + s2
    # In Best of 3, il terzo set (tie-break) si gioca a 15
    is_tiebreak = (formato == "Best of 3" and set_corrente == 2)
    limit = 15 if is_tiebreak else pmax
    
    won = False
    if p1 >= limit and p1 - p2 >= 2:
        # Sq1 vince set
        st.session_state[f"{key_base}_punteggi_sets"].append((p1, p2))
        st.session_state[f"{key_base}_s1"] += 1
        st.session_state[f"{key_base}_p1"] = 0
        st.session_state[f"{key_base}_p2"] = 0
        won = True
    elif p2 >= limit and p2 - p1 >= 2:
        # Sq2 vince set
        st.session_state[f"{key_base}_punteggi_sets"].append((p1, p2))
        st.session_state[f"{key_base}_s2"] += 1
        st.session_state[f"{key_base}_p1"] = 0
        st.session_state[f"{key_base}_p2"] = 0
        won = True


def _invia_al_tabellone(state, partita, key_base):
    """Trasferisce i dati del segnapunti live alla partita nel torneo."""
    sets = st.session_state.get(f"{key_base}_punteggi_sets", [])
    # Aggiungi set corrente se ha punti
    p1_curr = st.session_state.get(f"{key_base}_p1", 0)
    p2_curr = st.session_state.get(f"{key_base}_p2", 0)
    if p1_curr > 0 or p2_curr > 0:
        sets = sets + [(p1_curr, p2_curr)]
    
    if not sets:
        return
    
    s1v = sum(1 for a, b in sets if a > b)
    s2v = sum(1 for a, b in sets if b > a)
    
    partita["punteggi"] = sets
    partita["set_sq1"] = s1v
    partita["set_sq2"] = s2v
    partita["vincitore"] = partita["sq1"] if s1v >= s2v else partita["sq2"]
    partita["in_battuta"] = st.session_state.get(f"{key_base}_battuta", 1)
    partita["confermata"] = True
    
    aggiorna_classifica_squadra(state, partita)
    
    # Pulizia session
    for k in [f"{key_base}_s1", f"{key_base}_s2", f"{key_base}_p1",
              f"{key_base}_p2", f"{key_base}_battuta", f"{key_base}_punteggi_sets"]:
        if k in st.session_state:
            del st.session_state[k]


def _get_partite_disponibili(state):
    """Raccoglie tutte le partite non ancora confermate."""
    partite = []
    fase = state["fase"]
    
    if fase in ["gironi", "eliminazione", "proclamazione"]:
        for g in state.get("gironi", []):
            for p in g["partite"]:
                sq1 = get_squadra_by_id(state, p["sq1"])
                sq2 = get_squadra_by_id(state, p["sq2"])
                if sq1 and sq2:
                    partite.append({
                        "partita": p,
                        "label": f"[{g['nome']}] {sq1['nome']} vs {sq2['nome']} {'✅' if p['confermata'] else '🔴'}"
                    })
    
    if fase in ["eliminazione", "proclamazione"]:
        for p in state.get("bracket", []):
            sq1 = get_squadra_by_id(state, p["sq1"])
            sq2 = get_squadra_by_id(state, p["sq2"])
            if sq1 and sq2:
                partite.append({
                    "partita": p,
                    "label": f"[Playoff] {sq1['nome']} vs {sq2['nome']} {'✅' if p['confermata'] else '🔴'}"
                })
    
    return partite


def _players_str(state, sq):
    if not sq: return ""
    from data_manager import get_atleta_by_id
    names = [get_atleta_by_id(state, aid)["nome"] for aid in sq["atleti"] if get_atleta_by_id(state, aid)]
    return " · ".join(names)
