import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION ---
st.set_page_config(page_title="Simulateur EPL", layout="wide")

# --- CSS : POLICE RÉDUITE ET MÉTRIQUES ENCADRÉES ---
st.markdown("""
    <style>
    html, body, [class*="css"] { font-size: 0.95rem; } 
    [data-testid="stMetricValue"] {
        background-color: #1e2129;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #3e4451;
        color: #00ffcc;
        font-size: 1.2rem !important;
    }
    [data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR AVEC LOGO ---
with st.sidebar:
    try:
        st.image("im1.jpeg", use_container_width=True)
    except:
        st.info("Logo absent")
    
    st.header("Configuration")
    cycle_choice = st.selectbox("Cycle", ["Otto (Beau de Rochas)", "Diesel"])
    gas_mode = st.radio("Modèle de Gaz", ["Gaz Simple", "Gaz Parfait"])
    
    st.subheader("Entrées")
    v1 = st.number_input("V1 (m³)", value=0.03308, format="%.5f")
    p1 = st.number_input("P1 (Pa)", value=101328)
    t1 = st.number_input("T1 (K)", value=302)
    
    r_val = st.slider("r (Compression)", 5.0, 20.0, 9.50)
    t_max_val = st.slider("T_max (K)", 1000, 3000, 2100)
    rpm = st.number_input("Régime (tr/min)", value=3000)

# --- MOTEUR DE CALCUL ---
def get_cycle_data(r, t_max):
    R_gas, cv = 287.05, 718
    gamma = 1.4 if gas_mode == "Gaz Simple" else 1.38
    cp = gamma * cv
    m = (p1 * v1) / (R_gas * t1)
    
    # Points de transition
    v2 = v1 / r
    p2 = p1 * (r**gamma)
    t2 = t1 * (r**(gamma-1))
    
    if cycle_choice == "Otto (Beau de Rochas)":
        v3, t3 = v2, t_max
        p3 = p2 * (t3 / t2)
        v_comb, p_comb, t_comb = np.full(30, v2), np.linspace(p2, p3, 30), np.linspace(t2, t3, 30)
        s_comb = cv * np.log(t_comb/t2)
        qin = m * cv * (t3 - t2)
    else: # Diesel
        p3, t3 = p2, t_max
        v3 = v2 * (t3 / t2)
        v_comb, p_comb, t_comb = np.linspace(v2, v3, 30), np.full(30, p2), np.linspace(t2, t3, 30)
        s_comb = cp * np.log(t_comb/t2)
        qin = m * cp * (t3 - t2)
    
    # Courbes
    v12 = np.linspace(v1, v2, 30)
    p12, t12 = p1*(v1/v12)**gamma, t1*(v1/v12)**(gamma-1)
    
    v34 = np.linspace(v3, v1, 30)
    p34, t34 = p3*(v3/v34)**gamma, t3*(v3/v34)**(gamma-1)
    
    t41 = np.linspace(t34[-1], t1, 30)
    s41 = s_comb[-1] + cv * np.log(t41/t34[-1])

    w_net = qin - (m * cv * (t34[-1] - t1))
    return {
        "phases": [
            (v12, p12, t12, np.zeros(30), "1-2 Comp."),
            (v_comb, p_comb, t_comb, s_comb, "2-3 Comb."),
            (v34, p34, t34, np.full(30, s_comb[-1]), "3-4 Détente"),
            (np.full(30, v1), np.linspace(p34[-1], p1, 30), t41, s41, "4-1 Échap.")
        ],
        "metrics": {"eta": w_net/qin, "w": w_net, "m": m}
    }

res = get_cycle_data(r_val, t_max_val)

# --- AFFICHAGE ---
st.title("SIMULATEUR MOTEUR THERMIQUE - EPL")
t_lab, t_param, t_data = st.tabs(["📊 Labo Virtuel", "📈 Étude Paramétrique", "📋 Données"])

with t_lab:
    # Métriques
    m1, m2, m3, m4 = st.columns(4)
    pwr = (res["metrics"]["w"] * rpm / 120)
    m1.metric("Rendement (η)", f"{res['metrics']['eta']*100:.2f}%")
    m2.metric("Travail Net", f"{res['metrics']['w']:.2f} J")
    m3.metric("Puissance", f"{pwr/1000:.1f} kW")
    m4.metric("Couple", f"{(pwr/(2*np.pi*rpm/60)) if rpm>0 else 0:.1f} Nm")

    # Diagrammes
    c_a, c_b = st.columns(2)
    
    # Plotly Style
    layout_cfg = dict(template="plotly_dark", height=350, margin=dict(l=20, r=20, t=40, b=20), font=dict(size=10))

    # P-V
    fig_pv = go.Figure()
    for v, p, t, s, lbl in res["phases"]:
        fig_pv.add_trace(go.Scatter(x=v, y=p/1e5, name=lbl, line=dict(width=1.5)))
    fig_pv.update_layout(title="1. Diagramme de Clapeyron (P, V)", xaxis_title="V (m³)", yaxis_title="P (bar)", **layout_cfg)
    c_a.plotly_chart(fig_pv, use_container_width=True)

    # T-S
    fig_ts = go.Figure()
    for v, p, t, s, lbl in res["phases"]:
        fig_ts.add_trace(go.Scatter(x=s, y=t, name=lbl, line=dict(width=1.5)))
    fig_ts.update_layout(title="2. Diagramme Entropique (T, S)", xaxis_title="S (J/K)", yaxis_title="T (K)", **layout_cfg)
    c_b.plotly_chart(fig_ts, use_container_width=True)

    # T-V
    fig_tv = go.Figure()
    for v, p, t, s, lbl in res["phases"]:
        fig_tv.add_trace(go.Scatter(x=v, y=t, name=lbl, line=dict(width=1.5)))
    fig_tv.update_layout(title="3. Diagramme Température-Volume (T, V)", xaxis_title="V (m³)", yaxis_title="T (K)", **layout_cfg)
    st.plotly_chart(fig_tv, use_container_width=True)

with t_param:
    st.write("Analyse de l'influence de r sur le rendement")
    rx = np.linspace(5, 20, 20)
    ey = [get_cycle_data(i, t_max_val)["metrics"]["eta"] for i in rx]
    st.plotly_chart(go.Figure(data=go.Scatter(x=rx, y=ey), layout=layout_cfg), use_container_width=True)

with t_data:
    st.write("Valeurs aux points clés")
    st.json({"m (kg)": res["metrics"]["m"], "Taux r": r_val, "T_max": t_max_val})
