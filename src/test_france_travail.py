import json
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


# ----- Configuration

TOKEN_URL = (
    "https://entreprise.francetravail.fr/"
    "connexion/oauth2/access_token?realm=/partenaire"
)

SEARCH_URL = (
    "https://api.francetravail.io/"
    "partenaire/offresdemploi/v2/offres/search"
)

RAW_DIR = Path("data/raw/france_travail")

# ----- Récupération des identifiants France Travail sous forme de variables d'environnement

load_dotenv()

CLIENT_ID = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
CLIENT_SECRET = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")


# ----- Authentification

def get_access_token():
    """
    Obtient un token d'accès à l'API France Travail.
    """
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "api_offresdemploiv2 o2dsoffre"
    }

    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()

    return response.json()["access_token"]


# ----- Première récupération d'offres d'emploi

def get_offers(token, querystring):
    """
    Récupère les offres d'emploi depuis l'API France Travail.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(
        SEARCH_URL,
        headers=headers,
        params=querystring
    )

    response.raise_for_status()
    #print(response.status_code)
    #pprint(response.json())

    return response


# ----- Enregistrement des données brutes

def save_raw_response(response):
    """
    Enregistre la réponse de l'API France Travail au format JSON.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = RAW_DIR / f"france_travail_{timestamp}.json"

    data = response.json()

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    return file_path

# ----- Cartographier les clés de premier niveau des données

#offers = data["resultats"]

#all_keys = set()

#for offer in offers:
#    all_keys.update(offer.keys())

#for key in sorted(all_keys):
#    print(key)


# ----- Cartographier l'ensemble des clés du JSON

def get_json_keys(data, prefix=""):
    """
    Récupère de manière récursive les chemins des clés d'un objet JSON.
    """
    keys = set()

    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.add(full_key)
            keys.update(get_json_keys(value, full_key))

    elif isinstance(data, list):
        for item in data:
            keys.update(get_json_keys(item, prefix))

    return keys


# ----- Programme principal 

def main():
    
    # Indiquer ici les paramètres de la recherche d'offres d'emploi : 
    # mots-clés, lieu...
    querystring = {
        "motsCles": "boulanger",
        "departement": "48"
    }

    token = get_access_token()

    response = get_offers(token, querystring)

    # Optionnel : exploration des données pour obtention de la liste des clés (ici, par ordre alphabétique)
    data = response.json()
    
    all_keys = get_json_keys(data["resultats"])
    
    for key in sorted(all_keys):
        print(key)

    file_path = save_raw_response(response)
    print(f"Données enregistrées dans : {file_path}")


if __name__ == "__main__":
    main()