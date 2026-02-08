import streamlit as st
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Simulateur thermique EPL", layout="wide")

# --- CSS POUR LES MÉTRIQUES ENCADRÉES (Style sombre) ---
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

# --- BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    # Placement du logo en haut de la sidebar
    try:
        st.image("im1.jpeg", use_container_width=True)
    except:
        st.error("im1.jpeg introuvable.")
    
    st.header("Configuration")
    cycle_choice = st.selectbox("Cycle", ["Otto (Beau de Rochas)", "Diesel"])
    gas_mode = st.radio("Modèle de Gaz", ["Gaz Simple", "Gaz Parfait"])
    
    st.subheader("Paramètres d'Entrée")
    v1 = st.number_input("Volume initial V1 (m³)", value=0.03308, format="%.5f")
    p1 = st.number_input("Pression initiale P1 (Pa)", value=101328)
    t1 = st.number_input("Température initiale T1 (K)", value=302)
    
    st.subheader("Variables de Modélisation")
    r = st.slider("Taux de Compression (r)", 5.0, 20.0, 8.80)
    t_max = st.slider("Température Max (K)", 1000, 3000, 2100)
    rpm = st.number_input("Régime (tr/min)", value=3000)

# --- CONSTANTES ET PHYSIQUE ---
R = 287.05
gamma = 1.4 if gas_mode == "Gaz Simple" else 1.38
cv = 718
cp = gamma * cv
m = (p1 * v1) / (R * t1)

# Calcul des points clés
v2 = v1 / r
p2 = p1 * (r**gamma)
t2 = t1 * (r**(gamma-1))

if cycle_choice == "Otto (Beau de Rochas)":
    v3, t3 = v2, t_max
    p3 = p2 * (t3 / t2)
    qin = m * cv * (t3 - t2)
else: # Diesel
    p3, t3 = p2, t_max
    v3 = v2 * (t3 / t2)
    qin = m * cp * (t3 - t2)

v4 = v1
p4 = p3 * (v3/v4)**gamma
t4 = t3 * (v3/v4)**(gamma-1)
qout = m * cv * (t4 - t1)

w_net = qin - qout
rendement = w_net / qin
puissance = w_net * (rpm / 120)
couple = puissance / (2 * np.pi * rpm / 60) if rpm > 0 else 0

# --- INTERFACE PRINCIPALE ---
st.title("SIMULATEUR MOTEUR THERMIQUE - EPL")

# Métriques encadrées
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rendement (η)", f"{rendement*100:.2f} %")
c2.metric("Travail Net (W)", f"{w_net:.2f} J")
c3.metric("Puissance", f"{puissance/1000:.1f} kW")
c4.metric("Couple", f"{couple:.1f} N.m")

# --- GRAPHIQUE T-S (BOUCLE COMPLÈTE) ---
def get_ts_data():
    # 1-2 Compression
    t12 = np.linspace(t1, t2, 30)
    s12 = np.zeros(30) # Isentropique
    # 2-3 Combustion
    t23 = np.linspace(t2, t3, 30)
    s23 = (cv if cycle_choice == "Otto (Beau de Rochas)" else cp) * np.log(t23/t2)
    # 3-4 Détente
    t34 = np.linspace(t3, t4, 30)
    s34 = np.full(30, s23[-1]) # Isentropique
    # 4-1 Refroidissement (Retour au début)
    t41 = np.linspace(t4, t1, 30)
    s41 = s34[-1] + cv * np.log(t41/t4)
    return (s12, t12), (s23, t23), (s34, t34), (s41, t41)

(s12, t12), (s23, t23), (s34, t34), (s41, t41) = get_ts_data()

fig_ts = go.Figure()
fig_ts.add_trace(go.Scatter(x=s12, y=t12, name="1-2 Compression Isentropique", line=dict(color='cyan', width=1.5)))
fig_ts.add_trace(go.Scatter(x=s23, y=t23, name="2-3 Apport Chaleur (Combustion)", line=dict(color='red', width=1.5)))
fig_ts.add_trace(go.Scatter(x=s34, y=t34, name="3-4 Détente Isentropique", line=dict(color='yellow', width=1.5)))
fig_ts.add_trace(go.Scatter(x=s41, y=t41, name="4-1 Échappement (Isochore)", line=dict(color='lime', width=1.5)))

fig_ts.update_layout(
    title="2. Diagramme Entropique (T, S)",
    xaxis_title="Entropie (S) [J/K]", yaxis_title="Température (T) [K]",
    template="plotly_dark", height=500,
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
)

st.plotly_chart(fig_ts, use_container_width=True)
