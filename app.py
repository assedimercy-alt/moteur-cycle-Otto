import streamlit as st
import numpy as np
import plotly.graph_objects as go 

# --- CONFIGURATION ---
st.set_page_config(page_title="Simulateur EPL", layout="wide")

# --- CSS PERSONNALISÉ POUR LE LOOK DARK ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { color: #00ffcc; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGO EN HAUT À GAUCHE ---
# Assurez-vous que 'epl_logo.png' est dans le même dossier que votre script Streamlit
# Ou spécifiez le chemin complet : st.image("chemin/vers/epl_logo.png", width=100)
st.image("im1.jpeg", width=100) # Ajustez la largeur selon vos besoins

# --- CONSTANTES ---
R = 287.05  # J/(kg.K)

def get_gas_properties(mode):
    if mode == "Gaz Simple":
        return 1.4, 718  # gamma, Cv
    else: # Gaz Parfait (Modèle simplifié ici, ajustable)
        return 1.38, 720

# --- MOTEUR DE CALCULS THERMO ---
def compute_cycle(type_cycle, V1, P1, T1, r, T_max, gamma, cv):
    m = (P1 * V1) / (R * T1)
    cp = gamma * cv

    # ÉTAT 1
    v = [V1]
    p = [P1]
    t = [T1]
    s = [0] # Entropie relative

    # 1 -> 2 : COMPRESSION ISENTROPIQUE (PV^gamma = Cst)
    v_comp = np.linspace(V1, V1/r, 50)
    p_comp = P1 * (V1 / v_comp)**gamma
    t_comp = T1 * (V1 / v_comp)**(gamma - 1)
    s_comp = np.zeros(50) 

    # ÉTAT 2
    V2, P2, T2 = v_comp[-1], p_comp[-1], t_comp[-1]

    if type_cycle == "Otto (Beau de Rochas)":
        # 2 -> 3 : COMBUSTION ISOCHORE (V = Cst)
        V3 = V2
        T3 = T_max
        P3 = P2 * (T3 / T2)
        v_comb = np.full(50, V2)
        p_comb = np.linspace(P2, P3, 50)
        t_comb = np.linspace(T2, T3, 50)
        s_comb = cv * np.log(t_comb / T2) # ds = cv ln(T/To)
        Qin = m * cv * (T3 - T2)
    else:
        # 2 -> 3 : COMBUSTION ISOBARE (P = Cst)
        P3 = P2
        T3 = T_max
        V3 = V2 * (T3 / T2)
        v_comb = np.linspace(V2, V3, 50)
        p_comb = np.full(50, P2)
        t_comb = np.linspace(T2, T3, 50)
        s_comb = cp * np.log(t_comb / T2)
        Qin = m * cp * (T3 - T2)

    # 3 -> 4 : DÉTENTE ISENTROPIQUE
    V4 = V1
    v_det = np.linspace(V3, V4, 50)
    p_det = P3 * (V3 / v_det)**gamma
    t_det = T3 * (V3 / v_det)**(gamma - 1)
    s_det = np.full(50, s_comb[-1])

    # ÉTAT 4
    P4, T4 = p_det[-1], t_det[-1]
    Qout = m * cv * (T4 - T1)

    # BILAN
    W_net = Qin - Qout
    rendement = W_net / Qin

    # Assemblage des courbes
    V_total = np.concatenate([v_comp, v_comb, v_det, [V1]])
    P_total = np.concatenate([p_comp, p_comb, p_det, [P1]])
    T_total = np.concatenate([t_comp, t_comb, t_det, [T1]])

    # Entropie 4->1 (Isochore refroidissement)
    t_echap = np.linspace(T4, T1, 50)
    s_echap = s_det[-1] + cv * np.log(t_echap / T4)
    S_total = np.concatenate([s_comp, s_comb, s_det, s_echap])

    return {
        "V": V_total, "P": P_total, "T": T_total, "S": S_total,
        "W": W_net, "eta": rendement, "P_max": P3, "T_max": T3, "m": m
    }

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    cycle_choice = st.selectbox("Cycle", ["Otto (Beau de Rochas)", "Diesel"])
    gas_mode = st.radio("Modèle de Gaz", ["Gaz Simple", "Gaz Parfait"])

    st.subheader("Paramètres d'Entrée")
    v1_in = st.number_input("Volume initial V1 (m³)", value=0.03, format="%.5f")
    p1_in = st.number_input("Pression initiale P1 (Pa)", value=101325)
    t1_in = st.number_input("Température initiale T1 (K)", value=300)

    st.subheader("Variables de Modélisation")
    r_in = st.slider("Taux de Compression (r)", 5.0, 25.0, 9.5)
    t_max_in = st.slider("Température Max (K)", 1000, 3000, 2100)

    rpm = st.slider("Régime (tr/min)", 1000, 6000, 3000)

# --- CALCULS ---
gamma, cv = get_gas_properties(gas_mode)
res = compute_cycle(cycle_choice, v1_in, p1_in, t1_in, r_in, t_max_in, gamma, cv)

# Puissance et Couple (Hypothèse moteur 4 temps : 1 cycle tous les 2 tours)
puissance = res["W"] * (rpm / 120) 
couple = puissance / (2 * np.pi * rpm / 60) if rpm > 0 else 0

# --- INTERFACE PRINCIPALE ---
st.title("SIMULATEUR MOTEUR THERMIQUE - EPL")

tab1, tab2, tab3 = st.tabs(["📊 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données du Cycle"])

with tab1:
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Rendement (η)", f"{res['eta']*100:.2f}%")
    kpi2.metric("Travail Net", f"{res['W']:.2f} J")
    kpi3.metric("Puissance", f"{puissance/1000:.1f} kW")
    kpi4.metric("Couple", f"{couple:.1f} N.m")

    c1, c2 = st.columns(2)

    # Graphique P-V
    fig_pv = go.Figure()
    # On découpe pour colorer chaque phase
    fig_pv.add_trace(go.Scatter(x=res["V"][:50], y=res["P"][:50]/1e5, name="Compression", line=dict(color='#00d4ff', width=1.5)))
    fig_pv.add_trace(go.Scatter(x=res["V"][50:100], y=res["P"][50:100]/1e5, name="Combustion", line=dict(color='#ff4b4b', width=1.5)))
    fig_pv.add_trace(go.Scatter(x=res["V"][100:150], y=res["P"][100:150]/1e5, name="Détente", line=dict(color='#ffeb3b', width=1.5)))
    fig_pv.update_layout(title="Diagramme de Clapeyron (P, V)", xaxis_title="Volume (m³)", yaxis_title="Pression (bar)", template="plotly_dark", height=450)
    c1.plotly_chart(fig_pv, use_container_width=True)

    # Graphique T-S
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(x=res["S"], y=res["T"], name="Cycle", line=dict(color='#00ffcc', width=1.5)))
    fig_ts.update_layout(title="Diagramme Entropique (T, S)", xaxis_title="Entropie (J/K)", yaxis_title="Température (K)", template="plotly_dark", height=450)
    c2.plotly_chart(fig_ts, use_container_width=True)

with tab2:
    st.subheader("Analyse de l'influence du taux de compression")
    r_range = np.linspace(5, 20, 20)
    etas = [1 - (1/r**(gamma-1)) for r in r_range] # Formule Otto simplifiée
    fig_param = go.Figure()
    fig_param.add_trace(go.Scatter(x=r_range, y=etas, mode='lines+markers', name="η vs r"))
    fig_param.update_layout(title="Rendement Théorique en fonction de r", template="plotly_dark")
    st.plotly_chart(fig_param)

with tab3:
    st.subheader("États thermodynamiques")
    # Extraction des points clés (1, 2, 3, 4)
    data = {
        "Point": ["1 (Aspiration)", "2 (Compression)", "3 (Explosion)", "4 (Échappement)"],
        "Volume (m³)": [res["V"][0], res["V"][49], res["V"][99], res["V"][149]],
        "Pression (bar)": [res["P"][0]/1e5, res["P"][49]/1e5, res["P"][99]/1e5, res["P"][149]/1e5],
        "Température (K)": [res["T"][0], res["T"][49], res["T"][99], res["T"][149]],
    }
    st.table(data)
