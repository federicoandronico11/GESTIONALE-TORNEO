"""
ranking_page.py — Pagina ranking completa + esportazione PDF grafico
"""
import streamlit as st
import pandas as pd
from data_manager import get_atleta_by_id, get_squadra_by_id


def calcola_punti_ranking(pos, n_squadre):
    """Assegna punti in proporzione al numero di squadre, a scaglioni da 10."""
    # n_squadre * 10 = punteggio massimo (1° posto)
    # Ogni posizione sottrae 10 punti
    pts_massimi = n_squadre * 10
    pts = pts_massimi - ((pos - 1) * 10)
    return max(0, pts)


def build_ranking_data(state):
    """Costruisce la classifica globale da tutti gli atleti."""
    atleti_stats = []
    
    for a in state["atleti"]:
        s = a["stats"]
        if s["tornei"] == 0:
            continue
        
        # Ricalcola punti ranking con formula proporzione squadre
        rank_pts = sum(
            calcola_punti_ranking(pos, _get_n_squadre_torneo(state, torneo_nome))
            for torneo_nome, pos in s["storico_posizioni"]
        )
        
        quoziente_punti = round(s["punti_fatti"] / max(s["set_vinti"] + s["set_persi"], 1), 2)
        quoziente_set = round(s["set_vinti"] / max(s["set_persi"], 1), 2)
        quoziente_vittorie = round(s["vittorie"] / max(s["tornei"], 1), 2)
        win_rate = round(s["vittorie"] / max(s["tornei"], 1) * 100, 1)
        
        # Medaglie
        medaglie_oro = sum(1 for _, pos in s["storico_posizioni"] if pos == 1)
        medaglie_argento = sum(1 for _, pos in s["storico_posizioni"] if pos == 2)
        medaglie_bronzo = sum(1 for _, pos in s["storico_posizioni"] if pos == 3)
        
        atleti_stats.append({
            "atleta": a,
            "id": a["id"],
            "nome": a["nome"],
            "tornei": s["tornei"],
            "vittorie": s["vittorie"],
            "sconfitte": s["sconfitte"],
            "set_vinti": s["set_vinti"],
            "set_persi": s["set_persi"],
            "punti_fatti": s["punti_fatti"],
            "punti_subiti": s["punti_subiti"],
            "quoziente_punti": quoziente_punti,
            "quoziente_set": quoziente_set,
            "quoziente_vittorie": quoziente_vittorie,
            "win_rate": win_rate,
            "rank_pts": rank_pts,
            "oro": medaglie_oro,
            "argento": medaglie_argento,
            "bronzo": medaglie_bronzo,
            "storico": s["storico_posizioni"],
        })
    
    atleti_stats.sort(key=lambda x: (-x["rank_pts"], -x["oro"], -x["argento"], -x["win_rate"]))
    return atleti_stats


def _get_n_squadre_torneo(state, torneo_nome):
    """Cerca il numero di squadre di un torneo passato (usa len squadre correnti come fallback)."""
    return max(len(state["squadre"]), 4)


def render_ranking_page(state):
    """Pagina completa del ranking globale."""
    st.markdown("## 🏅 Ranking Globale")
    
    ranking = build_ranking_data(state)
    
    if not ranking:
        st.info("Completa almeno un torneo per visualizzare il ranking.")
        return
    
    # Tabs
    tabs = st.tabs(["🏆 Classifica Generale", "👤 Schede Atleti", "📄 Esporta PDF Ranking"])
    
    with tabs[0]:
        _render_classifica_completa(state, ranking)
    
    with tabs[1]:
        _render_schede_atleti(state, ranking)
    
    with tabs[2]:
        _render_export_ranking_pdf(state, ranking)


def _render_classifica_completa(state, ranking):
    n_squadre = len(state["squadre"])
    
    st.markdown(f"""
    <div style="background:var(--bg-card2);border:1px solid var(--border);border-radius:var(--radius);
        padding:12px 20px;margin-bottom:20px;font-size:0.8rem;color:var(--text-secondary)">
        💡 <strong>Formula punti:</strong> {n_squadre} squadre × 10 = 
        <strong style="color:var(--accent-gold)">{n_squadre*10} pt per il 1°</strong> 
        · Ogni posizione successiva: -10 pt · Totale si accumula tra tornei
    </div>
    """, unsafe_allow_html=True)
    
    # Podio Top 3
    if len(ranking) >= 3:
        col1, col2, col3 = st.columns(3)
        podio_cols = [(col2, ranking[0], "🥇", "#ffd700", "1°"),
                      (col1, ranking[1], "🥈", "#c0c0c0", "2°"),
                      (col3, ranking[2], "🥉", "#cd7f32", "3°")]
        
        for col, atleta, medal, color, pos in podio_cols:
            with col:
                st.markdown(f"""
                <div style="background:var(--bg-card);border:2px solid {color};
                    border-radius:var(--radius);padding:20px;text-align:center;
                    margin-top:{'0' if pos=='1°' else '20px'}">
                    <div style="font-size:2.5rem">{medal}</div>
                    <div style="font-family:var(--font-display);font-size:1.3rem;
                        font-weight:800;color:{color};text-transform:uppercase">
                        {atleta['nome']}
                    </div>
                    <div style="color:var(--text-secondary);font-size:0.85rem;margin:4px 0">
                        {atleta['rank_pts']} pt ranking
                    </div>
                    <div style="font-size:0.75rem;color:{color}">
                        🥇{atleta['oro']} 🥈{atleta['argento']} 🥉{atleta['bronzo']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabella completa
    html = """
    <table class="rank-table">
    <tr>
        <th>#</th>
        <th style="text-align:left">ATLETA</th>
        <th>PTS</th>
        <th>TORNEI</th>
        <th>🥇</th><th>🥈</th><th>🥉</th>
        <th>V</th><th>P</th>
        <th>SET V</th><th>SET P</th>
        <th>Q.SET</th><th>WIN%</th>
    </tr>"""
    
    pos_cls = {1: "gold", 2: "silver", 3: "bronze"}
    for i, a in enumerate(ranking):
        pos = i + 1
        cls = pos_cls.get(pos, "")
        html += f"""<tr>
            <td><span class="rank-pos {cls}">{pos}</span></td>
            <td style="text-align:left;font-weight:700">{a['nome']}</td>
            <td style="font-weight:800;color:var(--accent-gold)">{a['rank_pts']}</td>
            <td>{a['tornei']}</td>
            <td style="color:#ffd700">{a['oro']}</td>
            <td style="color:#c0c0c0">{a['argento']}</td>
            <td style="color:#cd7f32">{a['bronzo']}</td>
            <td style="color:var(--green)">{a['vittorie']}</td>
            <td style="color:var(--accent1)">{a['sconfitte']}</td>
            <td>{a['set_vinti']}</td>
            <td>{a['set_persi']}</td>
            <td>{a['quoziente_set']}</td>
            <td>{a['win_rate']}%</td>
        </tr>"""
    
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)


def _render_schede_atleti(state, ranking):
    if not ranking:
        return
    
    nomi = [a["nome"] for a in ranking]
    sel = st.selectbox("🔍 Seleziona Atleta", nomi, key="rank_career_sel")
    atleta_data = next((a for a in ranking if a["nome"] == sel), None)
    if not atleta_data:
        return
    
    a = atleta_data
    
    # Card statistiche
    st.markdown(f"""
    <div class="career-card">
        <div class="career-name">👤 {a['nome']}</div>
        <div style="color:var(--accent-gold);font-size:0.85rem;margin-top:4px">
            🏅 {a['rank_pts']} punti ranking
        </div>
        <div class="stat-grid">
            <div class="stat-box"><div class="stat-value" style="color:var(--accent-gold)">{a['rank_pts']}</div><div class="stat-label">Rank Pts</div></div>
            <div class="stat-box"><div class="stat-value">{a['tornei']}</div><div class="stat-label">Tornei</div></div>
            <div class="stat-box"><div class="stat-value" style="color:#ffd700">{a['oro']}</div><div class="stat-label">🥇 Ori</div></div>
            <div class="stat-box"><div class="stat-value" style="color:#c0c0c0">{a['argento']}</div><div class="stat-label">🥈 Argenti</div></div>
            <div class="stat-box"><div class="stat-value" style="color:#cd7f32">{a['bronzo']}</div><div class="stat-label">🥉 Bronzi</div></div>
            <div class="stat-box"><div class="stat-value" style="color:var(--green)">{a['vittorie']}</div><div class="stat-label">Vittorie</div></div>
            <div class="stat-box"><div class="stat-value" style="color:var(--accent1)">{a['sconfitte']}</div><div class="stat-label">Sconfitte</div></div>
            <div class="stat-box"><div class="stat-value">{a['set_vinti']}</div><div class="stat-label">Set Vinti</div></div>
            <div class="stat-box"><div class="stat-value">{a['set_persi']}</div><div class="stat-label">Set Persi</div></div>
            <div class="stat-box"><div class="stat-value">{a['quoziente_set']}</div><div class="stat-label">Q.Set</div></div>
            <div class="stat-box"><div class="stat-value">{a['quoziente_punti']}</div><div class="stat-label">Q.Punti</div></div>
            <div class="stat-box"><div class="stat-value">{a['win_rate']}%</div><div class="stat-label">Win Rate</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Grafici
    if a["storico"]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📈 Andamento Posizioni")
            df_pos = pd.DataFrame({
                "Torneo": [t for t, _ in a["storico"]],
                "Posizione": [p for _, p in a["storico"]],
            }).set_index("Torneo")
            # Inverti: 1° = valore alto
            max_pos = df_pos["Posizione"].max()
            df_pos["Posizione Inv"] = max_pos + 1 - df_pos["Posizione"]
            st.line_chart(df_pos["Posizione Inv"], height=200, color="#e8002d")
            st.caption("↑ = Migliore posizione")
        
        with col2:
            st.markdown("#### 📊 Punti Ranking per Torneo")
            n_sq = len(state["squadre"]) or 8
            df_pts = pd.DataFrame({
                "Torneo": [t for t, _ in a["storico"]],
                "Punti": [calcola_punti_ranking(p, n_sq) for _, p in a["storico"]],
            }).set_index("Torneo")
            st.bar_chart(df_pts, height=200, color="#ffd700")
        
        # Storico dettagliato
        st.markdown("#### 📋 Storico Tornei")
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        n_sq_curr = len(state["squadre"]) or 8
        for t_nome, pos in a["storico"]:
            icon = medals.get(pos, f"#{pos}")
            pts = calcola_punti_ranking(pos, n_sq_curr)
            st.markdown(f"• {icon} **{t_nome}** — {pos}° posto → +{pts} pt ranking")


def _render_export_ranking_pdf(state, ranking):
    st.markdown("### 📄 Esporta Ranking in PDF")
    st.info("Genera un PDF grafico professionale con il ranking completo e le statistiche.")
    
    if st.button("🖨️ GENERA PDF RANKING", use_container_width=True):
        try:
            pdf_path = _genera_pdf_ranking(state, ranking)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇️ SCARICA PDF RANKING",
                    f,
                    file_name="ranking_beach_volley.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Errore generazione PDF: {e}")
            import traceback
            st.code(traceback.format_exc())


def _genera_pdf_ranking(state, ranking):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import mm

    pdf_path = "/tmp/ranking_beach_volley.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                            leftMargin=15*mm, rightMargin=15*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    
    DARK = colors.HexColor("#0a0a0f")
    RED = colors.HexColor("#e8002d")
    GOLD = colors.HexColor("#ffd700")
    BLUE = colors.HexColor("#0070f3")
    GREEN = colors.HexColor("#00c851")
    SILVER = colors.HexColor("#c0c0c0")
    BRONZE = colors.HexColor("#cd7f32")
    LIGHT = colors.HexColor("#f0f0f0")
    WHITE = colors.white

    styles = getSampleStyleSheet()
    title_s = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=24,
                              textColor=RED, spaceAfter=4, alignment=1)
    sub_s = ParagraphStyle("sub", fontName="Helvetica", fontSize=11,
                            textColor=colors.grey, spaceAfter=12, alignment=1)
    h2_s = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14,
                           textColor=DARK, spaceBefore=14, spaceAfter=8)
    info_s = ParagraphStyle("info", fontName="Helvetica", fontSize=9,
                             textColor=colors.grey, spaceAfter=6)

    story = []

    # Titolo
    story.append(Paragraph("🏐 BEACH VOLLEY RANKING GLOBALE", title_s))
    torneo_nome = state["torneo"]["nome"] or "Stagione"
    n_tornei = max((a["tornei"] for a in ranking), default=0)
    story.append(Paragraph(f"{torneo_nome} · {n_tornei} torneo/i disputato/i · {len(ranking)} atleti classificati", sub_s))
    story.append(HRFlowable(width="100%", thickness=3, color=RED))
    story.append(Spacer(1, 10))
    
    # Formula punti
    n_sq = len(state["squadre"]) or 8
    story.append(Paragraph(
        f"Formula punti: {n_sq} squadre × 10 = {n_sq*10} pt per il 1° posto. Ogni posizione successiva -10 pt. I punti si accumulano tra tornei.",
        info_s
    ))
    story.append(Spacer(1, 8))

    # Top 3 podio
    if len(ranking) >= 3:
        story.append(Paragraph("PODIO", h2_s))
        podio_data = [["", "ATLETA", "PUNTI RANKING", "TORNEI", "🥇", "🥈", "🥉", "WIN%"]]
        medals_colors = [GOLD, SILVER, BRONZE]
        for i in range(min(3, len(ranking))):
            a = ranking[i]
            podio_data.append([
                f"{['1°','2°','3°'][i]}",
                a["nome"],
                str(a["rank_pts"]),
                str(a["tornei"]),
                str(a["oro"]),
                str(a["argento"]),
                str(a["bronzo"]),
                f"{a['win_rate']}%",
            ])
        
        pt = Table(podio_data, colWidths=[12*mm, 50*mm, 28*mm, 18*mm, 12*mm, 12*mm, 12*mm, 18*mm])
        pt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#fff8dc")),
            ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#f5f5f5")),
            ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#fdf5e6")),
            ("FONTNAME", (0, 1), (-1, 3), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("ALIGN", (0, 0), (1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("ROWHEIGHT", (0, 1), (-1, 3), 16),
        ]))
        story.append(pt)
        story.append(Spacer(1, 12))
    
    # Classifica completa
    story.append(Paragraph("CLASSIFICA COMPLETA", h2_s))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    story.append(Spacer(1, 6))
    
    full_data = [["#", "ATLETA", "PTS", "T", "V", "P", "SV", "SP", "Q.SET", "WIN%"]]
    for i, a in enumerate(ranking):
        full_data.append([
            str(i + 1),
            a["nome"],
            str(a["rank_pts"]),
            str(a["tornei"]),
            str(a["vittorie"]),
            str(a["sconfitte"]),
            str(a["set_vinti"]),
            str(a["set_persi"]),
            str(a["quoziente_set"]),
            f"{a['win_rate']}%",
        ])
    
    ft = Table(full_data, colWidths=[10*mm, 52*mm, 18*mm, 10*mm, 10*mm, 10*mm, 12*mm, 12*mm, 16*mm, 16*mm])
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT, WHITE]),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dddddd")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        # Prima riga d'oro
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#fff8dc")),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
    ]))
    story.append(ft)
    
    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Documento generato da Beach Volley Tournament Manager Pro",
        ParagraphStyle("footer", fontName="Helvetica", fontSize=7, textColor=colors.grey, alignment=1)
    ))
    
    doc.build(story)
    return pdf_path
