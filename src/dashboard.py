import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

from user import get_wallets  
from ingestion import enrich_wallet_with_price  # ou incluez la fonction enrich_wallet_with_price ici
from ai_utils import ask_portfolio_question, suggest_optimized_allocation  # nouveau

# Titre du dashboard
st.title("InvestmentWallet - Dashboard")

st.header("Portefeuille de l'utilisateur")
st.markdown("Voici la liste des wallets récupérés via l'API Bitpanda.")

# Récupération des données avec normalisation pour obtenir un DataFrame
try:
    df_wallets = get_wallets(process=True)
except Exception as e:
    st.error(f"Erreur lors de la récupération des wallets : {e}")
    st.stop()

# Afficher le DataFrame dans le dashboard
st.dataframe(df_wallets)

st.header("Répartition du portefeuille")
# Filtrer les entrées dont la valeur totale n'est pas nulle ou manquante
df_valid = df_wallets.dropna(subset=["total_value"])
df_valid = df_valid[df_valid["total_value"] > 0]

if df_valid.empty:
    st.warning("Aucun actif avec une valeur totale positive n'a été trouvé pour le moment.")
else:
    # Agréger la valeur totale par symbole (par exemple, BTC, ETH, etc.)
    aggregated = df_valid.groupby("symbol")["total_value"].sum()

    # Création du graphique en camembert
    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.pie(aggregated, labels=aggregated.index, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 5})
    
    fig.tight_layout()

    # Afficher le graphique dans Streamlit
    st.pyplot(fig)


st.header("🤖 Assistant IA - Portfolio Chat")

# Interface de chat
with st.expander("Poser une question sur votre portefeuille"):
    user_question = st.text_input("Posez votre question ici (ex : Quel est mon actif le plus rentable ?)")
    if user_question:
        with st.spinner("L'IA réfléchit..."):
            try:
                answer = ask_portfolio_question(df_wallets, user_question)
                st.markdown("**Réponse de l'assistant :**")
                st.markdown(answer)
            except Exception as e:
                st.error(f"Erreur lors de l'appel à l'IA : {e}")

# Suggestion d'allocation optimisée
with st.expander("💡 Demander une allocation optimisée"):
    if st.button("Générer une proposition"):
        with st.spinner("L'IA analyse votre portefeuille..."):
            try:
                suggestion = suggest_optimized_allocation(df_wallets)
                st.markdown("**Suggestion d'allocation :**")
                st.markdown(suggestion)
            except Exception as e:
                st.error(f"Erreur IA : {e}")    

# Quelques indications supplémentaires pour l'utilisateur
st.markdown(
    """
    **Instructions complémentaires :**
    - Ce dashboard se met à jour dès que vous actualisez la page.
    - Vous pouvez ajouter d'autres visualisations (courbes d'évolution, indicateurs de performance, etc.)
      pour enrichir votre dashboard.
    """
)
