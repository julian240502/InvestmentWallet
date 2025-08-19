import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from user import get_wallets  
from ingestion import enrich_wallet_with_price  
from ai_utils import ask_portfolio_question, suggest_optimized_allocation

# Symbols ignored (not available or unsupported by Yahoo Finance)
SYMBOL_BLACKLIST = ['BEST', 'XYZ', 'JUP', 'AKT', 'VSN', 'MLC', 'LINGO', 'TRUMP', 'PENGU', 'ONDO', 'AGIX', 'KAS']

@st.cache_data
def get_and_enrich_wallets():
    df = get_wallets(process=True)
    df = df[~df['symbol'].isin(SYMBOL_BLACKLIST)]
    df = enrich_wallet_with_price(df)
    return df

st.title("InvestmentWallet - Dashboard")

st.header("User Portfolio")
st.markdown("Below is the list of wallets retrieved from the Bitpanda API.")

if "wallets" not in st.session_state:
    with st.spinner("Loading portfolio..."):
        try:
            df = get_and_enrich_wallets()
            st.session_state.wallets = df
        except Exception as e:
            st.error(f"Error retrieving wallet data: {e}")
            st.stop()

# Always use the cached version
df_wallets = st.session_state.wallets

if df_wallets.empty:
    st.warning("No wallet found or all wallets are marked as deleted.")

# Show the final DataFrame
st.dataframe(df_wallets[["symbol", "balance", "price", "total_value"]].reset_index(drop=True))

# Portfolio breakdown
st.header("Portfolio Breakdown")

if df_wallets.empty:
    st.warning("No asset with usable total value was found.")
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

# AI Assistant
st.header("🤖 AI Assistant - Portfolio Chat")

# Chat interface
st.subheader("Ask a question about your portfolio")

user_question = st.text_input("Type your question here (e.g., What is my most valuable asset?)")
if user_question:
    with st.spinner("Thinking..."):
        try:
            answer = ask_portfolio_question(df_wallets, user_question)
            st.markdown("**Assistant's response:**")
            st.markdown(answer)
        except Exception as e:
            st.error(f"AI response error: {e}")

# Allocation suggestion
st.subheader("Request an optimized allocation")

if st.button("Generate a suggestion"):
    with st.spinner("The assistant is analyzing your portfolio..."):
        try:
            suggestion = suggest_optimized_allocation(df_wallets)
            st.markdown("**Optimized allocation suggestion:**")
            st.markdown(suggestion)
        except Exception as e:
            st.error(f"AI error: {e}") 

# Additional user guidance
st.markdown(
    """
    **Additional information:**
    - This dashboard refreshes every time the page is reloaded.
    """
)
