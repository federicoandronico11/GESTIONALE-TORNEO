"""
data_manager.py — Gestione persistenza JSON e modelli dati
"""
import json, os, random
from datetime import datetime
from pathlib import Path

DATA_FILE = "beach_volley_data.json"

# ─── STRUTTURA DATI DEFAULT ──────────────────────────────────────────────────

def empty_state():
    return {
        "fase": "setup",          # setup | gironi | eliminazione | proclamazione
        "torneo": {
            "nome": "",
            "tipo_tabellone": "Gironi + Playoff",   # o "Doppia Eliminazione"
            "formato_set": "Set Unico",              # o "Best of 3"
            "punteggio_max": 21,
            "data": str(datetime.today().date()),
        },
        "atleti": [],             # lista globale atleti: {id, nome, stats}
        "squadre": [],            # {id, nome, atleti:[id,id]}
        "gironi": [],             # [{nome, squadre:[id], partite:[...]}]
        "bracket": [],            # partite eliminazione diretta
        "ranking_globale": [],    # storico tornei per atleta
        "vincitore": None,
        "simulazione_al_ranking": True,
    }

# ─── LOAD / SAVE ─────────────────────────────────────────────────────────────

def load_state():
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # merge keys mancanti con default
        base = empty_state()
        for k, v in base.items():
            data.setdefault(k, v)
        return data
    return empty_state()

def save_state(state):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ─── ATLETI ──────────────────────────────────────────────────────────────────

def new_atleta(nome):
    return {
        "id": f"a_{nome.lower().replace(' ','_')}_{random.randint(1000,9999)}",
        "nome": nome,
        "stats": {
            "tornei": 0,
            "vittorie": 0,
            "sconfitte": 0,
            "set_vinti": 0,
            "set_persi": 0,
            "punti_fatti": 0,
            "punti_subiti": 0,
            "storico_posizioni": [],   # [(torneo_nome, posizione)]
        }
    }

def get_atleta_by_id(state, aid):
    for a in state["atleti"]:
        if a["id"] == aid:
            return a
    return None

# ─── SQUADRE ─────────────────────────────────────────────────────────────────

def new_squadra(nome, atleta1_id, atleta2_id):
    return {
        "id": f"sq_{random.randint(10000,99999)}",
        "nome": nome,
        "atleti": [atleta1_id, atleta2_id],
        "punti_classifica": 0,
        "set_vinti": 0,
        "set_persi": 0,
        "punti_fatti": 0,
        "punti_subiti": 0,
        "vittorie": 0,
        "sconfitte": 0,
    }

def get_squadra_by_id(state, sid):
    for s in state["squadre"]:
        if s["id"] == sid:
            return s
    return None

def nome_squadra(state, sid):
    s = get_squadra_by_id(state, sid)
    return s["nome"] if s else "?"

# ─── PARTITE ─────────────────────────────────────────────────────────────────

def new_partita(sq1_id, sq2_id, fase="girone", girone=None):
    return {
        "id": f"p_{random.randint(100000,999999)}",
        "sq1": sq1_id,
        "sq2": sq2_id,
        "fase": fase,
        "girone": girone,
        "set_sq1": 0,
        "set_sq2": 0,
        "punteggi": [],          # [(p1,p2), (p1,p2), ...]
        "in_battuta": 1,         # 1 o 2
        "confermata": False,
        "vincitore": None,
    }

# ─── SIMULAZIONE ─────────────────────────────────────────────────────────────

def simula_set(pmax, tie_break=False):
    limit = 15 if tie_break else pmax
    a, b = 0, 0
    while True:
        if random.random() > 0.5:
            a += 1
        else:
            b += 1
        if a >= limit or b >= limit:
            if abs(a - b) >= 2:
                return a, b
            if a > limit + 6 or b > limit + 6:
                return (a, b) if a > b else (b, a)

def simula_partita(state, partita):
    torneo = state["torneo"]
    pmax = torneo["punteggio_max"]
    formato = torneo["formato_set"]
    
    if formato == "Set Unico":
        p1, p2 = simula_set(pmax)
        partita["punteggi"] = [(p1, p2)]
        partita["set_sq1"] = 1 if p1 > p2 else 0
        partita["set_sq2"] = 1 if p2 > p1 else 0
    else:  # Best of 3
        sets_1, sets_2 = 0, 0
        punteggi = []
        while sets_1 < 2 and sets_2 < 2:
            tie = (sets_1 == 1 and sets_2 == 1)
            p1, p2 = simula_set(pmax, tie_break=tie)
            punteggi.append((p1, p2))
            if p1 > p2: sets_1 += 1
            else: sets_2 += 1
        partita["punteggi"] = punteggi
        partita["set_sq1"] = sets_1
        partita["set_sq2"] = sets_2
    
    partita["vincitore"] = partita["sq1"] if partita["set_sq1"] > partita["set_sq2"] else partita["sq2"]
    partita["confermata"] = True
    return partita

# ─── CLASSIFICA GIRONE ───────────────────────────────────────────────────────

def aggiorna_classifica_squadra(state, partita):
    """Aggiorna stats squadra dopo conferma risultato."""
    sq1 = get_squadra_by_id(state, partita["sq1"])
    sq2 = get_squadra_by_id(state, partita["sq2"])
    if not sq1 or not sq2:
        return

    s1v, s2v = partita["set_sq1"], partita["set_sq2"]
    p1_tot = sum(p[0] for p in partita["punteggi"])
    p2_tot = sum(p[1] for p in partita["punteggi"])

    sq1["set_vinti"] += s1v; sq1["set_persi"] += s2v
    sq2["set_vinti"] += s2v; sq2["set_persi"] += s1v
    sq1["punti_fatti"] += p1_tot; sq1["punti_subiti"] += p2_tot
    sq2["punti_fatti"] += p2_tot; sq2["punti_subiti"] += p1_tot

    if partita["vincitore"] == partita["sq1"]:
        sq1["vittorie"] += 1; sq1["punti_classifica"] += 3
        sq2["sconfitte"] += 1; sq2["punti_classifica"] += 1
    else:
        sq2["vittorie"] += 1; sq2["punti_classifica"] += 3
        sq1["sconfitte"] += 1; sq1["punti_classifica"] += 1

# ─── TRASFERIMENTO RANKING ATLETI ────────────────────────────────────────────

def trasferisci_al_ranking(state, podio):
    """podio = [(1, sq_id), (2, sq_id), (3, sq_id)]"""
    nome_torneo = state["torneo"]["nome"]
    n_squadre = len(state["squadre"])
    # Tutti gli atleti partecipanti ricevono aggiornamento stats
    atleti_aggiornati = set()
    
    # Prima aggiorna tutti con le stats di squadra
    for sq in state["squadre"]:
        for aid in sq["atleti"]:
            atleta = get_atleta_by_id(state, aid)
            if not atleta or aid in atleti_aggiornati: continue
            s = atleta["stats"]
            s["set_vinti"] += sq["set_vinti"]
            s["set_persi"] += sq["set_persi"]
            s["punti_fatti"] += sq["punti_fatti"]
            s["punti_subiti"] += sq["punti_subiti"]
            atleti_aggiornati.add(aid)
    
    # Poi aggiorna posizioni podio
    for pos, sq_id in podio:
        sq = get_squadra_by_id(state, sq_id)
        if not sq: continue
        for aid in sq["atleti"]:
            atleta = get_atleta_by_id(state, aid)
            if not atleta: continue
            s = atleta["stats"]
            s["tornei"] += 1
            s["storico_posizioni"].append((nome_torneo, pos))
            if pos == 1: s["vittorie"] += 1
            else: s["sconfitte"] += 1
    
    # Atleti non in podio: aggiorna tornei
    podio_atleti = {aid for _, sq_id in podio for aid in (get_squadra_by_id(state, sq_id) or {"atleti":[]})["atleti"]}
    for sq in state["squadre"]:
        for aid in sq["atleti"]:
            if aid not in podio_atleti:
                atleta = get_atleta_by_id(state, aid)
                if atleta:
                    atleta["stats"]["tornei"] += 1
                    atleta["stats"]["sconfitte"] += 1
                    # Posizione approssimativa
                    atleta["stats"]["storico_posizioni"].append((nome_torneo, n_squadre // 2))

# ─── GENERAZIONE GIRONI ──────────────────────────────────────────────────────

def genera_gironi(squadre_ids, num_gironi=2):
    random.shuffle(squadre_ids)
    gironi = []
    for i in range(num_gironi):
        squadre_girone = squadre_ids[i::num_gironi]
        partite = []
        for j in range(len(squadre_girone)):
            for k in range(j+1, len(squadre_girone)):
                partite.append(new_partita(squadre_girone[j], squadre_girone[k], "girone", i))
        gironi.append({
            "nome": f"Girone {'ABCDEFGH'[i]}",
            "squadre": squadre_girone,
            "partite": partite,
        })
    return gironi

# ─── GENERAZIONE BRACKET ─────────────────────────────────────────────────────

def genera_bracket_da_gironi(gironi):
    """Prende le prime 2 di ogni girone per il bracket."""
    teste_di_serie = []
    for g in gironi:
        classifica = sorted(
            g["squadre"],
            key=lambda sid: (
                next((sq for sq in []), {"punti_classifica": 0}).get("punti_classifica", 0)
            ),
            reverse=True
        )
        # usiamo l'ordine di squadre come proxy
        teste_di_serie.extend(g["squadre"][:2])
    
    bracket = []
    random.shuffle(teste_di_serie)
    for i in range(0, len(teste_di_serie), 2):
        if i+1 < len(teste_di_serie):
            bracket.append(new_partita(teste_di_serie[i], teste_di_serie[i+1], "eliminazione"))
    return bracket
