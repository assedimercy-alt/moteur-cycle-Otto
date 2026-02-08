import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION ET STYLE ---
st.set_page_config(page_title="Simulateur Thermique EPL", layout="wide")

st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        background-color: #1e2129;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #3e4451;
        color: #00ffcc;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("im1.jpeg", use_container_width=True)
    except:
        st.info("im1.jpeg' non trouvé.")
    
    st.header("Configuration")
    cycle_choice = st.selectbox("Cycle", ["Otto (Beau de Rochas)", "Diesel"])
    gas_mode = st.radio("Modèle de Gaz", ["Gaz Simple", "Gaz Parfait"])
    
    st.subheader("Paramètres d'Entrée")
    v1 = st.number_input("Volume initial V1 (m³)", value=0.03308, format="%.5f")
    p1 = st.number_input("Pression initiale P1 (Pa)", value=101328)
    t1 = st.number_input("Température initiale T1 (K)", value=302)
    
    st.subheader("Variables de Modélisation")
    r_val = st.slider("Taux de Compression (r)", 5.0, 20.0, 8.80)
    t_max_val = st.slider("Température Max (K)", 1000, 3000, 2100)
    rpm = st.number_input("Régime (tr/min)", value=3000)

# --- FONCTION DE CALCUL PHYSIQUE ---
def compute_engine_data(r, t_max):
    R_gas, cv, gamma = 287.05, 718, (1.4 if gas_mode == "Gaz Simple" else 1.38)
    cp = gamma * cv
    m = (p1 * v1) / (R_gas * t1)
    
    # Points 1-2-3-4
    v2 = v1 / r
    p2 = p1 * (r**gamma)
    t2 = t1 * (r**(gamma-1))
    
    if cycle_choice == "Otto (Beau de Rochas)":
        v3, t3 = v2, t_max
        p3 = p2 * (t3 / t2)
        qin = m * cv * (t3 - t2)
    else:
        p3, t3 = p2, t_max
        v3 = v2 * (t3 / t2)
        qin = m * cp * (t3 - t2)
        
    v4, p4 = v1, p3 * (v3/v1)**gamma
    t4 = t3 * (v3/v1)**(gamma-1)
    w_net = qin - (m * cv * (t4 - t1))
    
    return {"r": r, "v": [v1, v2, v3, v4], "p": [p1, p2, p3, p4], "t": [t1, t2, t3, t4], 
            "w": w_net, "eta": w_net/qin, "m": m, "gamma": gamma}

res = compute_engine_data(r_val, t_max_val)

# --- INTERFACE PRINCIPALE ---
st.title("SIMULATEUR MOTEUR THERMIQUE - EPL")

# Navigation par Onglets
tab_labo, tab_param, tab_data = st.tabs(["🧪 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données du Cycle"])

with tab_labo:
    # Métriques encadrées
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rendement (η)", f"{res['eta']*100:.2f} %")
    c2.metric("Travail Net (W)", f"{res['w']:.2f} J")
    c3.metric("Puissance", f"{(res['w'] * rpm / 120)/1000:.1f} kW")
    c4.metric("Couple", f"{(res['w'] * rpm / 120) / (2 * np.pi * rpm / 60):.1f} N.m")

    # Graphiques
    col_a, col_b = st.columns(2)
    # Ici on placerait les fonctions go.Figure() PV, TS et TV définies précédemment
    st.info("Les diagrammes de Clapeyron, Entropique et T-V sont affichés ici.")

with tab_param:
    st.subheader("Analyse de l'efficacité")
    r_range = np.linspace(5, 20, 15)
    results = [compute_engine_data(rx, t_max_val)['eta'] for rx in r_range]
    
    fig_p = go.Figure(data=go.Scatter(x=r_range, y=results, mode='lines+markers', line=dict(color='#00ffcc')))
    fig_p.update_layout(title="Influence du taux de compression sur le rendement", 
                        xaxis_title="Taux r", yaxis_title="Rendement η", template="plotly_dark")
    st.plotly_chart(fig_p, use_container_width=True)

with tab_data:
    st.subheader("États Thermodynamiques Précis")
    data_table = {
        "Phase": ["Aspiration (1)", "Compression (2)", "Combustion (3)", "Détente (4)"],
        "Volume (m³)": res["v"],
        "Pression (bar)": [px/1e5 for px in res["p"]],
        "Température (K)": res["t"]
    }
    st.table(data_table)
