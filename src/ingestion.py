import pandas as pd
import yfinance as yf
import time
import streamlit as st
from functools import lru_cache
from pathlib import Path


# Liste par défaut des symboles non disponibles sur Yahoo Finance
DEFAULT_UNSUPPORTED_SYMBOLS = {
    "BEST",
    "XYZ",
    "JUP",
    "AKT",
    "VSN",
    "MLC",
    "LINGO",
    "TRUMP",
    "PENGU",
    "ONDO",
    "AGIX",
    "KAS",
    "MELANIA",
}

# Emplacement de la liste personnalisée (si elle existe) fournie par l'utilisateur
UNSUPPORTED_SYMBOLS_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "unsupported_yfinance_symbols.txt"
)

#  Dictionnaire de cache local pour éviter les requêtes répétées
_price_cache = {}


@lru_cache(maxsize=1)
def get_unsupported_symbols():
    """Charge la liste des symboles non pris en charge par Yahoo Finance."""
    symbols = {symbol.upper() for symbol in DEFAULT_UNSUPPORTED_SYMBOLS}

    if UNSUPPORTED_SYMBOLS_FILE.exists():
        try:
            with open(UNSUPPORTED_SYMBOLS_FILE, "r", encoding="utf-8") as handle:
                for line in handle:
                    cleaned = line.strip().upper()
                    if not cleaned or cleaned.startswith("#"):
                        continue
                    symbols.add(cleaned)
        except OSError as exc:
            # Afficher l'erreur dans la console Streamlit sans interrompre l'exécution
            print(
                "Impossible de charger la liste personnalisée des symboles non supportés "
                f"({UNSUPPORTED_SYMBOLS_FILE}): {exc}"
            )

    return frozenset(symbols)

def get_crypto_price(symbol, retries=3, delay=2):
    """
    Récupère le prix en EUR depuis Yahoo Finance avec gestion des erreurs, retries et cache.
    """
    symbol_key = symbol.upper()

    if symbol_key in _price_cache:
        return _price_cache[symbol_key]

    if symbol_key in get_unsupported_symbols():
        print(f"[{symbol_key}] Ignoré : symbole non disponible sur Yahoo Finance.")
        _price_cache[symbol_key] = None
        return None

    ticker_str = f"{symbol_key}-EUR"
    for attempt in range(retries):
        try:
            ticker = yf.Ticker(ticker_str)
            price = ticker.info.get('regularMarketPrice')
            if price is not None:
                _price_cache[symbol_key] = price
                return price
            else:
                print(f"[{symbol_key}] Aucune donnée de prix trouvée.")
        except Exception as e:
            print(f"[{symbol_key}] Erreur récupération prix (tentative {attempt+1}): {e}")

        time.sleep(delay)

    print(f"[{symbol_key}] Erreur persistante ou rate limit. Aucun prix.")
    _price_cache[symbol_key] = None
    return None


def enrich_wallet_with_price(df_wallets: pd.DataFrame) -> pd.DataFrame:
    df_wallets = df_wallets.copy()
    df_wallets['symbol'] = df_wallets['symbol'].str.upper()
    symbols = df_wallets['symbol'].tolist()
    prices = []

    progress_bar = st.progress(0, text="Chargement des prix Yahoo Finance...")

    unsupported_symbols = get_unsupported_symbols()
    skipped_symbols = set()

    for i, symbol in enumerate(symbols):
        already_cached = symbol in _price_cache
        if symbol in unsupported_symbols:
            skipped_symbols.add(symbol)
        price = get_crypto_price(symbol)

        prices.append(price)
        progress = (i + 1) / len(symbols)
        progress_bar.progress(progress, text=f"Chargement des prix ({int(progress * 100)}%)")

        if symbol not in unsupported_symbols and not already_cached:
            time.sleep(0.75)

    progress_bar.empty()

    df_wallets['price'] = prices
    df_wallets['balance'] = pd.to_numeric(df_wallets['balance'], errors='coerce')
    df_wallets['total_value'] = df_wallets['balance'] * df_wallets['price']

    df_wallets = df_wallets.dropna(subset=["price", "total_value"])
    df_wallets = df_wallets[df_wallets["total_value"] > 0]

    df_wallets.attrs["unsupported_symbols"] = sorted(skipped_symbols)

    return df_wallets
