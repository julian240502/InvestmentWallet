import pandas as pd
import os
import sys
from ingestion import enrich_wallet_with_price

def load_data(file_path):
    # Chargement du CSV en DataFrame
    return pd.read_csv(file_path)

def clean_data(df):
    # Supprimer les lignes totalement vides ou avec des valeurs aberrantes
    df = df.dropna(how="all")
    # Remplir ou supprimer les valeurs manquantes selon le cas
    df = df.fillna(method='ffill').fillna(method='bfill')
    return df

def process_category(category_name):
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", f"{category_name}.csv")
    df = load_data(file_path)
    df_clean = clean_data(df)
    
    # Enregistrer le DataFrame nettoyé
    output_path = os.path.join(os.path.dirname(__file__), "..","data", "processed",f"{category_name}_processed.csv")
    df_clean.to_csv(output_path)
    print(f"Traitement terminé pour {category_name}. Données sauvegardées dans {output_path}")

def load_and_process_wallets(df):
    # Créer une copie du DataFrame pour éviter de modifier l'original
    df = pd.json_normalize(df)
    df_processed = df.copy()
    df_processed.rename(columns={
        "id": "wallet_id",
        "attributes.cryptocoin_id": "cryptocoin_id",
        "attributes.cryptocoin_symbol": "symbol",
        "attributes.balance": "balance",
        "attributes.is_default": "is_default",
        "attributes.name": "wallet_name",
        "attributes.pending_transactions_count": "pending_tx_count",
        "attributes.deleted": "deleted"
    }, inplace=True)
    
    # Convertir la colonne balance en numérique
    df_processed['balance'] = pd.to_numeric(df_processed['balance'], errors='coerce')
    # Filtrer les wallets non supprimés
    df_processed = df_processed[df_processed['deleted'] == False]
    df_processed=df_processed[['symbol','balance']]

    df_processed = enrich_wallet_with_price(df_processed)
    
    return df_processed
