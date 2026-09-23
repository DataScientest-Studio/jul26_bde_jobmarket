import json
import os
from datetime import datetime
from pathlib import Path
import time
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

RANGE_SIZE = 150
DELAY = 0.25
MAX_RANGE_END = 12000

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

def save_raw_response(response, timestamp, start, end):
    """
    Enregistre une tranche de résultats de l'API France Travail.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    file_path = (
        RAW_DIR
        / f"france_travail_{timestamp}_range_{start:04d}_{end:04d}.json"
    )

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

    querystring = {
        "grandDomaine": "N",
        "departement": "34"
    }

    token = get_access_token()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    all_keys = set()
    total_downloaded = 0

    for start in range(0, MAX_RANGE_END + 1, RANGE_SIZE):

        end = min(
            start + RANGE_SIZE - 1,
            MAX_RANGE_END
        )

        querystring["range"] = f"{start}-{end}"

        response = get_offers(
            token,
            querystring
        )

        data = response.json()
        offers = data.get("resultats", [])

        total_downloaded += len(offers)

        all_keys.update(
            get_json_keys(offers)
        )

        file_path = save_raw_response(
            response,
            timestamp,
            start,
            end
        )

        print(
            f"Range {start}-{end} : "
            f"{len(offers)} offres récupérées "
            f"(HTTP {response.status_code})"
        )

        print(
            f"Content-Range : "
            f"{response.headers.get('Content-Range')}"
        )

        print(
            f"Total récupéré : {total_downloaded}"
        )

        # HTTP 200 : tous les résultats ont été parcourus.
        # HTTP 206 : il reste des résultats.
        content_range = response.headers.get("Content-Range")

        if content_range:
            total_results = int(content_range.split("/")[-1])

            if total_downloaded >= total_results:
                break

        time.sleep(DELAY)

    print(
        f"\nExtraction terminée : "
        f"{total_downloaded} offres récupérées."
    )

    # Optionnel : affichage de toutes les clés rencontrées
    #for key in sorted(all_keys):
    #    print(key)
        

if __name__ == "__main__":
    main()