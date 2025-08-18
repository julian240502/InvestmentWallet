import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

from user import get_wallets  
from ingestion import enrich_wallet_with_price  
from ai_utils import ask_portfolio_question, suggest_optimized_allocation  # nouveau

# Symboles ignorés (non référencés ou non valorisables dans Yahoo Finance)
SYMBOL_BLACKLIST = ['BEST', 'XYZ','JUP','AKT','VSN','MLC','LINGO','TRUMP','PENGU','ONDO','AGIX','KAS']


@st.cache_data
def get_and_enrich_wallets():
    df = get_wallets(process=True)
    df = df[~df['symbol'].isin(SYMBOL_BLACKLIST)]
    df = enrich_wallet_with_price(df)
    return df

st.title("InvestmentWallet - Dashboard")

st.header("Portefeuille de l'utilisateur")
st.markdown("Voici la liste des wallets récupérés via l'API Bitpanda.")

if "wallets" not in st.session_state:
    with st.spinner("Chargement du portefeuille..."):
        try:
            df = get_and_enrich_wallets()
            st.session_state.wallets = df
        except Exception as e:
            st.error(f"Erreur lors de la récupération : {e}")
            st.stop()

# Toujours utiliser la version stockée en session
df_wallets = st.session_state.wallets


if df_wallets.empty:
    st.warning("Aucun wallet trouvé ou tous les wallets sont supprimés.")

# Affichage du tableau final
st.dataframe(df_wallets[["symbol", "balance", "price", "total_value"]].reset_index(drop=True))

# Répartition du portefeuille
st.header("Répartition du portefeuille")

if df_wallets.empty:
    st.warning("Aucun actif avec une valeur totale exploitable n'a été trouvé.")
else:
    aggregated = df_wallets.groupby("symbol")["total_value"].sum()

    fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
    ax.pie(
        aggregated,
        labels=aggregated.index,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 6}
    )
    fig.tight_layout()
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
    """
)
