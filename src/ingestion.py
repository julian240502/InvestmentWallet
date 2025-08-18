import pandas as pd
import yfinance as yf
import time
import streamlit as st

#  Dictionnaire de cache local pour éviter les requêtes répétées
_price_cache = {}

def get_crypto_price(symbol, retries=3, delay=2):
    """
    Récupère le prix en EUR depuis Yahoo Finance avec gestion des erreurs, retries et cache.
    """
    if symbol in _price_cache:
        return _price_cache[symbol]

    ticker_str = f"{symbol}-EUR"
    for attempt in range(retries):
        try:
            ticker = yf.Ticker(ticker_str)
            price = ticker.info.get('regularMarketPrice')
            if price is not None:
                _price_cache[symbol] = price
                return price
            else:
                print(f"[{symbol}] Aucune donnée de prix trouvée.")
        except Exception as e:
            print(f"[{symbol}] Erreur récupération prix (tentative {attempt+1}): {e}")

        time.sleep(delay)

    print(f"[{symbol}] Erreur persistante ou rate limit. Aucun prix.")
    _price_cache[symbol] = None
    return None


def enrich_wallet_with_price(df_wallets: pd.DataFrame) -> pd.DataFrame:
    df_wallets = df_wallets.copy()
    symbols = df_wallets['symbol'].tolist()
    prices = []

    progress_bar = st.progress(0, text="Chargement des prix Yahoo Finance...")

    for i, symbol in enumerate(symbols):
        price = get_crypto_price(symbol)

        prices.append(price)
        progress = (i + 1) / len(symbols)
        progress_bar.progress(progress, text=f"Chargement des prix ({int(progress * 100)}%)")

        time.sleep(1.5)

    progress_bar.empty()

    df_wallets['price'] = prices
    df_wallets['balance'] = pd.to_numeric(df_wallets['balance'], errors='coerce')
    df_wallets['total_value'] = df_wallets['balance'] * df_wallets['price']

    df_wallets = df_wallets.dropna(subset=["price", "total_value"])
    df_wallets = df_wallets[df_wallets["total_value"] > 0]

    return df_wallets