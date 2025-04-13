import pandas as pd
import os
import sys

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

if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    for category in ["etfs", "actions", "cryptos"]:
        process_category(category)
