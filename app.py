import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="Simulateur Thermique EPL",
    page_icon="🔥",
    layout="wide"
)

# CSS personnalisé
st.markdown("""
<style>
    /* Style général */
    .main {
        padding: 0.5rem;
    }
    
    /* Header avec logo */
    .header-container {
        display: flex;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    
    .logo {
        height: 80px;
        margin-right: 20px;
    }
    
    .title {
        color: #1e3a8a;
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    
    .subtitle {
        color: #6b7280;
        font-size: 1rem;
        margin: 0;
    }
    
    /* Cartes */
    .card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #3b82f6;
    }
    
    .card-title {
        color: #1e40af;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    /* Paramètres */
    .param-label {
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.3rem;
        display: block;
    }
    
    /* Graphiques */
    .graph-container {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    /* Boutons */
    .stButton > button {
        width: 100%;
        background-color: #1e40af;
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.7rem;
        border-radius: 5px;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1e3a8a;
    }
    
    /* Tableaux */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }
    
    .data-table th {
        background-color: #f3f4f6;
        color: #1f2937;
        font-weight: bold;
        padding: 0.75rem;
        text-align: left;
        border-bottom: 2px solid #d1d5db;
    }
    
    .data-table td {
        padding: 0.75rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .data-table tr:hover {
        background-color: #f9fafb;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour créer le header avec logo
def create_header():
    col1, col2 = st.columns([1, 5])
    with col1:
        # Placeholder pour le logo - à remplacer par votre image
        st.image("im1.jpeg", 
                caption="", use_column_width=True)
    with col2:
        st.markdown("<h1 class='title'>SIMULATEUR MOTEUR THERMIQUE</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>École Polytechnique de Lille - Labo Virtuel</p>", unsafe_allow_html=True)
    
    st.markdown("---")

# Fonction pour calculer le cycle Otto
def calculate_otto_cycle(V1, P1, T1, r, T_max):
    gamma = 1.4
    R = 287.0
    
    # Points du cycle
    V1_val = V1
    P1_val = P1
    T1_val = T1
    
    V2 = V1_val / r
    P2 = P1_val * (r ** gamma)
    T2 = T1_val * (r ** (gamma - 1))
    
    V3 = V2
    T3 = T_max
    P3 = P2 * (T3 / T2)
    
    V4 = V1_val
    P4 = P3 / (r ** gamma)
    T4 = T3 / (r ** (gamma - 1))
    
    # Calcul de l'entropie
    cv = R / (gamma - 1)
    S1 = 0
    S2 = S1 + cv * np.log(T2/T1_val) + R * np.log(V2/V1_val)
    S3 = S2 + cv * np.log(T3/T2)
    S4 = S3 + cv * np.log(T4/T3) + R * np.log(V4/V3)
    
    # Calcul des performances
    m = (P1_val * V1_val) / (R * T1_val)  # Masse de gaz
    W_12 = m * cv * (T1_val - T2)
    Q_23 = m * cv * (T3 - T2)
    W_34 = m * cv * (T3 - T4)
    W_net = W_34 + W_12
    eta = 1 - 1/(r**(gamma-1))
    
    # Puissance et couple (valeurs théoriques)
    n_cyl = 4
    N = 3000 / 60  # tr/s
    Puissance = abs(W_net) * n_cyl * N / 2
    Couple = Puissance / (2 * np.pi * N)
    
    return {
        'V': [V1_val, V2, V3, V4, V1_val],
        'P': [P1_val/1000, P2/1000, P3/1000, P4/1000, P1_val/1000],
        'T': [T1_val, T2, T3, T4, T1_val],
        'S': [S1, S2, S3, S4, S1],
        'rendement': eta,
        'travail_net': abs(W_net),
        'puissance': Puissance/1000,
        'couple': Couple,
        'points': [
            {'V': V1_val, 'P': P1_val/1000, 'T': T1_val, 'S': S1},
            {'V': V2, 'P': P2/1000, 'T': T2, 'S': S2},
            {'V': V3, 'P': P3/1000, 'T': T3, 'S': S3},
            {'V': V4, 'P': P4/1000, 'T': T4, 'S': S4}
        ]
    }

# Fonction pour créer les graphiques
def create_plots(results):
    # Diagramme P-V
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    
    V = results['V']
    P = results['P']
    
    # Courbe avec couleurs différentes par segment
    colors = ['#ef4444', '#10b981', '#3b82f6', '#f59e0b']
    labels = ['1-2 Compression', '2-3 Combustion', '3-4 Détente', '4-1 Échappement']
    
    for i in range(4):
        ax1.plot(V[i:i+2], P[i:i+2], color=colors[i], linewidth=3, label=labels[i])
        ax1.plot(V[i], P[i], 'ko', markersize=8)
        ax1.text(V[i]*1.02, P[i]*1.02, f'{i+1}', fontsize=12, fontweight='bold')
    
    ax1.set_xlabel('Volume (m³)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Pression (kPa)', fontsize=12, fontweight='bold')
    ax1.set_title('Diagramme de Clapeyron (P-V)', fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.legend(loc='upper right')
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    # Diagramme T-S
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    
    S = results['S']
    T = results['T']
    
    for i in range(4):
        ax2.plot(S[i:i+2], T[i:i+2], color=colors[i], linewidth=3, label=labels[i])
        ax2.plot(S[i], T[i], 'ko', markersize=8)
        ax2.text(S[i]*1.02, T[i]*1.02, f'{i+1}', fontsize=12, fontweight='bold')
    
    ax2.set_xlabel('Entropie (J/K)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Température (K)', fontsize=12, fontweight='bold')
    ax2.set_title('Diagramme Entropique (T-S)', fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3, linestyle='--')
    ax2.legend(loc='upper left')
    
    return fig1, fig2

# Application principale
def main():
    # Header avec logo
    create_header()
    
    # Deux colonnes principales
    col_left, col_right = st.columns([1.2, 2])
    
    with col_left:
        st.markdown("""
        <div class='card'>
            <div class='card-title'>Simulateur Thermique EPL</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sélection du cycle
        cycle_type = st.selectbox(
            "**Cycle thermique**",
            ["Otto (Beau de Rochas)", "Diesel"],
            key="cycle_type"
        )
        
        st.markdown("**Modèle de Gaz**")
        st.markdown("- Gaz Simple")
        
        # Paramètres d'entrée
        st.markdown("<div class='card-title'>Paramètres d'Entrée</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            V1 = st.number_input(
                "Volume initial $V_1$ (m³)",
                min_value=0.001,
                max_value=1.0,
                value=0.03,
                format="%.5f",
                step=0.001,
                key="V1"
            )
        
        with col2:
            P1 = st.number_input(
                "Pression initiale $P_1$ (Pa)",
                min_value=50000,
                max_value=200000,
                value=101328,
                step=1000,
                key="P1"
            )
        
        T1 = st.number_input(
            "Température initiale $T_1$ (K)",
            min_value=250,
            max_value=400,
            value=302,
            step=5,
            key="T1"
        )
        
        # Variables de modélisation
        st.markdown("<div class='card-title'>Variables de Modélisation</div>", unsafe_allow_html=True)
        
        r = st.slider(
            "Taux de Compression ($r$)",
            min_value=6.0,
            max_value=15.0,
            value=9.5,
            step=0.1,
            key="r"
        )
        
        T_max = st.slider(
            "Température Max ($T_{max}$) (K)",
            min_value=1500,
            max_value=2500,
            value=2100,
            step=50,
            key="T_max"
        )
        
        # Calcul automatique
        results = calculate_otto_cycle(V1, P1, T1, r, T_max)
        
        # Données du cycle
        st.markdown("<div class='card-title'>Données du Cycle</div>", unsafe_allow_html=True)
        
        # Création du tableau des résultats
        data_html = f"""
        <table class='data-table'>
            <tr>
                <th>Paramètre</th>
                <th>Valeur</th>
            </tr>
            <tr>
                <td>Rendement ($\\eta$)</td>
                <td><strong>{results['rendement']*100:.2f} %</strong></td>
            </tr>
            <tr>
                <td>Travail Net</td>
                <td><strong>{results['travail_net']:.2f} J</strong></td>
            </tr>
            <tr>
                <td>Puissance</td>
                <td><strong>{results['puissance']:.1f} kW</strong></td>
            </tr>
            <tr>
                <td>Couple</td>
                <td><strong>{results['couple']:.1f} N.m</strong></td>
            </tr>
        </table>
        """
        st.markdown(data_html, unsafe_allow_html=True)
        
        # Points du cycle
        st.markdown("<div class='card-title'>Points du Cycle</div>", unsafe_allow_html=True)
        
        points_html = """
        <table class='data-table'>
            <tr>
                <th>Point</th>
                <th>V (m³)</th>
                <th>P (kPa)</th>
                <th>T (K)</th>
            </tr>
        """
        for i, point in enumerate(results['points'], 1):
            points_html += f"""
            <tr>
                <td><strong>{i}</strong></td>
                <td>{point['V']:.5f}</td>
                <td>{point['P']:.1f}</td>
                <td>{point['T']:.1f}</td>
            </tr>
            """
        points_html += "</table>"
        st.markdown(points_html, unsafe_allow_html=True)
    
    with col_right:
        st.markdown("<div class='card-title'>Labo Virtuel - Visualisation</div>", unsafe_allow_html=True)
        
        # Graphiques
        fig1, fig2 = create_plots(results)
        
        # Affichage des graphiques
        st.markdown("### 1. Diagramme de Clapeyron (P, V)")
        st.pyplot(fig1)
        
        st.markdown("### 2. Diagramme Entropique (T, S)")
        st.pyplot(fig2)
        
        # Légende des phases
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.markdown("""
            <div style='background-color: #ef4444; padding: 5px 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;'>
                1-2 Compression
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown("""
            <div style='background-color: #10b981; padding: 5px 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;'>
                2-3 Combustion
            </div>
            """, unsafe_allow_html=True)
        with col_c:
            st.markdown("""
            <div style='background-color: #3b82f6; padding: 5px 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;'>
                3-4 Détente
            </div>
            """, unsafe_allow_html=True)
        with col_d:
            st.markdown("""
            <div style='background-color: #f59e0b; padding: 5px 10px; border-radius: 5px; text-align: center; color: white; font-weight: bold;'>
                4-1 Échappement
            </div>
            """, unsafe_allow_html=True)
    
    # Section inférieure - Étude Paramétrique
    st.markdown("---")
    st.markdown("<div class='card-title'>Étude Paramétrique - Cycle Otto</div>", unsafe_allow_html=True)
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        with st.expander("**Phase 1-2: Compression**", expanded=True):
            st.markdown("""
            - **Transformation**: Adiabatique réversible
            - **Loi**: $P_1V_1^\\gamma = P_2V_2^\\gamma$
            - **Température**: $T_2 = T_1 \\times r^{\\gamma-1}$
            - Travail consommé
            """)
    
    with col_exp2:
        with st.expander("**Phase 2-3: Combustion**", expanded=True):
            st.markdown("""
            - **Transformation**: Isochore
            - **Volume constant**: $V_2 = V_3$
            - **Pression**: $P_3 = P_2 \\times \\frac{T_3}{T_2}$
            - Chaleur fournie au fluide
            """)
    
    with col_exp3:
        with st.expander("**Phase 3-4 & 4-1**", expanded=True):
            st.markdown("""
            **3-4: Détente**
            - Adiabatique réversible
            - Travail produit
            
            **4-1: Échappement**
            - Isochore
            - Chaleur rejetée
            - Retour à l'état initial
            """)
    
    # Note de bas de page
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #6b7280; font-size: 0.9rem; padding: 1rem;'>
            Simulateur Thermique EPL - École Polytechnique de Lille<br>
            Cycle Otto (Beau de Rochas) - Modèle de gaz parfait
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
