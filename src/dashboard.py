import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

from user import get_wallets
from ingestion import enrich_wallet_with_price, get_unsupported_symbols
from ai_utils import ask_portfolio_question, suggest_optimized_allocation

st.set_page_config(
    page_title="InvestmentWallet Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .main {
            background: linear-gradient(135deg, rgba(245, 248, 255, 0.9), rgba(255, 255, 255, 0.95));
            padding-top: 1rem;
        }
        div.block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1100px;
        }
        .metric-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0px 12px 32px rgba(15, 23, 42, 0.08);
            border: 1px solid rgba(148, 163, 184, 0.25);
        }
        .metric-card h3 {
            font-size: 0.95rem !important;
            color: #475569;
            margin-bottom: 0.25rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .metric-card p {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0f172a;
        }
        .section-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1e293b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def get_and_enrich_wallets():
    df = get_wallets(process=True)
    unsupported_symbols = get_unsupported_symbols()
    df["symbol"] = df["symbol"].str.upper()
    df = df[~df['symbol'].isin(unsupported_symbols)]
    df = enrich_wallet_with_price(df)
    return df

st.title("💼 InvestmentWallet Dashboard")
st.caption("Dernière mise à jour : {}".format(datetime.now().strftime("%d %B %Y - %H:%M")))

st.sidebar.title("Portfolio Controls")
st.sidebar.caption(
    "Ajustez la vue du portefeuille, rafraîchissez les données et explorez des insights en temps réel."
)
refresh_clicked = st.sidebar.button("🔄 Rafraîchir les données", use_container_width=True)
if refresh_clicked:
    st.session_state.pop("wallets", None)
    st.experimental_rerun()

st.sidebar.markdown("---")

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
unsupported_filtered = df_wallets.attrs.get("unsupported_symbols", [])

if unsupported_filtered:
    st.sidebar.warning(
        "Les actifs suivants ont été ignorés car ils ne sont pas disponibles sur Yahoo Finance : "
        + ", ".join(unsupported_filtered)
    )

if df_wallets.empty:
    st.warning("No wallet found or all wallets are marked as deleted.")

unique_symbols = sorted(df_wallets["symbol"].unique())
selected_symbols = st.sidebar.multiselect(
    "Sélectionnez les actifs à afficher",
    options=unique_symbols,
    default=unique_symbols,
)

max_portfolio_value = float(df_wallets["total_value"].max() or 0)
min_threshold = st.sidebar.slider(
    "Valeur minimale par actif (€)",
    min_value=0.0,
    max_value=max(100.0, round(max_portfolio_value, 2)),
    value=0.0,
    step=max(10.0, round(max_portfolio_value / 20, 2)) if max_portfolio_value else 10.0,
)

filtered_wallets = df_wallets[df_wallets["symbol"].isin(selected_symbols)]
filtered_wallets = filtered_wallets[filtered_wallets["total_value"] >= min_threshold]

st.markdown("### Portefeuille Utilisateur")
st.markdown("Retrouvez ci-dessous une vue consolidée de vos actifs Bitpanda.")

if filtered_wallets.empty:
    st.info("Aucun actif ne correspond aux filtres sélectionnés.")
else:
    aggregated = filtered_wallets.groupby("symbol", as_index=False)["total_value"].sum()
    total_value = aggregated["total_value"].sum()
    top_asset_row = aggregated.sort_values("total_value", ascending=False).head(1)
    top_asset = top_asset_row.iloc[0]["symbol"] if not top_asset_row.empty else "-"
    top_asset_value = top_asset_row.iloc[0]["total_value"] if not top_asset_row.empty else 0.0

    metric_cols = st.columns(3)
    with metric_cols[0]:
        st.markdown("<div class='metric-card'><h3>Valeur Totale</h3><p>{:,.2f} €</p></div>".format(total_value), unsafe_allow_html=True)
    with metric_cols[1]:
        st.markdown(
            "<div class='metric-card'><h3>Nombre d'actifs</h3><p>{}</p></div>".format(
                aggregated.shape[0]
            ),
            unsafe_allow_html=True,
        )
    with metric_cols[2]:
        st.markdown(
            "<div class='metric-card'><h3>Actif Principal</h3><p>{} ({:,.2f} €)</p></div>".format(
                top_asset, top_asset_value
            ),
            unsafe_allow_html=True,
        )

    st.markdown("#### Détail des positions")
    st.dataframe(
        filtered_wallets[["symbol", "balance", "price", "total_value"]].reset_index(drop=True),
        use_container_width=True,
    )

# Portfolio breakdown
st.markdown("---")
st.markdown("<p class='section-title'>Répartition du portefeuille</p>", unsafe_allow_html=True)

if filtered_wallets.empty:
    st.warning("No asset with usable total value was found.")
else:
    chart_view = st.radio(
        "Choisissez le type de visualisation",
        options=("Diagramme en anneau", "Barres dynamiques"),
        horizontal=True,
    )

    aggregated = filtered_wallets.groupby("symbol", as_index=False)["total_value"].sum()
    total_sum = aggregated["total_value"].sum()
    aggregated["part"] = aggregated["total_value"] / total_sum if total_sum else 0

    if chart_view == "Diagramme en anneau":
        chart = (
            alt.Chart(aggregated)
            .mark_arc(innerRadius=60, outerRadius=120)
            .encode(
                theta=alt.Theta("total_value", stack=True, title="Valeur totale (€)"),
                color=alt.Color("symbol", legend=alt.Legend(title="Symboles")),
                tooltip=[
                    alt.Tooltip("symbol", title="Actif"),
                    alt.Tooltip("total_value", title="Valeur (€)", format=",.2f"),
                    alt.Tooltip("part", title="Part", format=".1%"),
                ],
            )
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        chart = (
            alt.Chart(aggregated)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("symbol", sort="-y", title="Actifs"),
                y=alt.Y("total_value", title="Valeur totale (€)", stack=None),
                color=alt.Color("symbol", legend=None),
                tooltip=[
                    alt.Tooltip("symbol", title="Actif"),
                    alt.Tooltip("total_value", title="Valeur (€)", format=",.2f"),
                    alt.Tooltip("part", title="Part", format=".1%"),
                ],
            )
        ).interactive()
        st.altair_chart(chart, use_container_width=True)

    st.info(
        "💡 Astuce : utilisez la barre latérale pour filtrer vos actifs et visualiser des scénarios spécifiques."
    )

# AI Assistant
st.markdown("---")
st.header("🤖 Assistant IA - Dialogue Portfolio")

# Chat interface
st.subheader("Posez une question sur votre portefeuille")
st.caption("L'assistant s'appuie sur vos données actuelles pour offrir des insights personnalisés.")

user_question = st.text_input("Exemple : Quel est mon actif le plus performant ?")
if user_question:
    with st.spinner("Thinking..."):
        try:
            answer = ask_portfolio_question(df_wallets, user_question)
            st.markdown("**Assistant's response:**")
            st.markdown(answer)
        except Exception as e:
            st.error(f"AI response error: {e}")

# Allocation suggestion
st.subheader("Demander une allocation optimisée")
st.caption("Obtenez une proposition d'équilibrage de portefeuille en fonction de vos positions actuelles.")

if st.button("✨ Générer une suggestion", use_container_width=True):
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
    - Utilisez la barre latérale pour ajuster les filtres et focaliser votre analyse.
    - Les suggestions IA ne constituent pas un conseil d'investissement.
    """
)
