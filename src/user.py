import os
import requests
import pandas as pd
from dotenv import load_dotenv
from preprocessing import load_and_process_wallets

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()
BITPANDAS_API_KEY = os.getenv('BITPANDAS_API_KEY')


# Définir l'URL de base et récupérer la clé API stockée dans les variables d'environnement
API_BASE_URL = "https://api.bitpanda.com/v1"

if BITPANDAS_API_KEY is None:
    raise ValueError("Clé API non trouvée. Veuillez définir BITPANDAS_API_KEY dans votre fichier .env.")

def api_get(endpoint):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "X-Api-Key": BITPANDAS_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()['data']
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur lors de l'appel à {endpoint}: {e}")


#------------------------------------------------------------------------------------

def get_wallets(process=False):
    data= api_get("/wallets")
    if process:
        return load_and_process_wallets(data)
    return data

def get_trades(process=False):
    data = api_get("/trades")
    if process:
        return pd.json_normalize(data)
    return data

def get_wallets_transactions(process=False):
    data = api_get("/wallets/transactions")
    if process:
        return pd.json_normalize(data)
    return data