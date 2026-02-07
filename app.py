import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Simulateur Cycle d'Otto", layout="wide")

st.title("🚗 Simulateur Interactif du Cycle d'Otto")
st.markdown("""
Cette application trace le diagramme **Pression-Volume (P-V)** d'un moteur à allumage commandé.
""")

# --- Barre latérale pour les réglages ---
st.sidebar.header("Paramètres Techniques")
r = st.sidebar.slider("Rapport de compression (r)", 5.0, 12.0, 8.5, 0.5)
gamma = st.sidebar.slider("Indice adiabatique (gamma)", 1.2, 1.5, 1.4)
P1 = st.sidebar.number_input("Pression initiale P1 (Pa)", value=101325)
T1 = st.sidebar.number_input("Température initiale T1 (K)", value=300)

# Constantes pour le tracé
V_cylindree = 0.0005 # 0.5 Litre
V2 = V_cylindree / (r - 1)
V1 = V2 + V_cylindree

# --- Calcul des phases ---

# 1 -> 2 : Compression Isentropique
v_12 = np.linspace(V1, V2, 100)
p_12 = P1 * (V1 / v_12)**gamma

# 2 -> 3 : Apport de chaleur (Isochore)
# On simule une augmentation de pression due à l'explosion
P2 = p_12[-1]
P3 = P2 * 2.8 # Facteur d'explosion arbitraire pour le visuel

# 3 -> 4 : Détente Isentropique
v_34 = np.linspace(V2, V1, 100)
p_34 = P3 * (V2 / v_34)**gamma

# --- Création du Graphique ---
fig, ax = plt.subplots(figsize=(10, 6))

# Tracé des courbes
ax.plot(v_12, p_12, 'b-', linewidth=2, label='1->2: Compression Isentropique')
ax.plot([V2, V2], [P2, P3], 'r-', linewidth=2, label='2->3: Combustion (Isochore)')
ax.plot(v_34, p_34, 'g-', linewidth=2, label='3->4: Détente Isentropique')
ax.plot([V1, V1], [p_34[-1], P1], 'y-', linewidth=2, label='4->1: Échappement (Isochore)')

# Mise en forme
ax.set_xlabel("Volume (m³)")
ax.set_ylabel("Pression (Pa)")
ax.set_title("Diagramme P-V du Cycle d'Otto")
ax.grid(True, linestyle='--', alpha=0.7)
ax.legend()

# Affichage sur Streamlit
col1, col2 = st.columns([2, 1])

with col1:
    st.pyplot(fig)

with col2:
    st.subheader("Résultats théoriques")
    # Formule du rendement thermique
    rendement = 1 - (1 / (r**(gamma - 1)))
    st.metric("Rendement Thermique", f"{rendement:.2%}")
    
    st.info(f"""
    **Points clés :**
    - Volume max (V1) : {V1*1000:.2f} L
    - Volume min (V2) : {V2*1000:.2f} L
    - Pression max (P3) : {P3/100000:.2f} bar
    """) 
