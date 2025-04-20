import pandas as pd
import yfinance as yf
import numpy as np

import yfinance as yf

def get_crypto_price(symbol):
    """
    Récupère le prix en euro d'un actif via Yahoo Finance.
    Pour toute valeur non référencée (par exemple, si le prix n'est pas disponible),
    la fonction affiche un avertissement et retourne None.

    Args:
        symbol (str): Le symbole de l'actif (par exemple 'BTC', 'ETH', 'BEST', etc.).

    Returns:
        float or None: Le prix en euro ou None si aucune donnée n'est disponible.
    """
    ticker_str = f"{symbol}-EUR"
    ticker = yf.Ticker(ticker_str)
    try:
        price = ticker.info.get('regularMarketPrice')
    except Exception as e:
        print(f"Erreur lors de la récupération du ticker {ticker_str} : {e}")
        return None

    if price is None:
        print(f"Attention : Le symbole '{symbol}' n'est pas référencé sur Yahoo Finance. Aucune donnée de prix disponible.")
        return None
    return price


def enrich_wallet_with_price(df_wallets):
    """
    Enrichit le DataFrame des wallets avec le prix (en euro) et la valeur totale (balance * prix).
    Pour les actifs dont le symbole n'est pas référencé, le prix sera None.

    Args:
        df_wallets (pd.DataFrame): DataFrame contenant les données des wallets,
                                   avec au moins les colonnes 'symbol' et 'balance'.

    Returns:
        pd.DataFrame: Le DataFrame enrichi avec les colonnes 'price' et 'total_value'.
    """
    # Appliquer la fonction get_crypto_price à la colonne 'symbol'
    df_wallets['price'] = df_wallets['symbol'].apply(get_crypto_price)
    
    # Convertir 'balance' en numérique si ce n'est pas déjà fait
    df_wallets['balance'] = pd.to_numeric(df_wallets['balance'], errors='coerce')
    
    # Calculer la valeur totale de chaque wallet : balance * price.
    # Si 'price' est None, le résultat sera NaN.
    df_wallets['total_value'] = df_wallets['balance'] * df_wallets['price']
    return df_wallets
