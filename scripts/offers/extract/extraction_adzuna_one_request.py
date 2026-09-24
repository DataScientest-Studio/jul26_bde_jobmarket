import json
import logging
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


# ----- Configuration

SEARCH_URL = "https://api.adzuna.com/v1/api/jobs/fr/search/153"

RAW_DIR = Path("data/raw/adzuna")

LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "jobmarket.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger("extraction_adzuna_one_request")


# ----- Récupération des identifiants Adzuna sous forme de variables d'environnement

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")


# ----- Première récupération d'offres d'emploi

def get_offers(querystring):
    """
    Récupère les offres d'emploi depuis l'API Adzuna.
    """
    response = requests.get(
        SEARCH_URL,
        params=querystring
    )

    response.raise_for_status()

    logger.info("Requête Adzuna réussie (HTTP %s).", response.status_code)

    return response


# ----- Enregistrement des données brutes

def save_raw_response(response):
    """
    Enregistre la réponse de l'API Adzuna au format JSON.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = RAW_DIR / f"adzuna_{timestamp}.json"

    data = response.json()

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    logger.info("Réponse brute enregistrée dans %s.", file_path)

    return file_path


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

    logger.info("Début de l'extraction Adzuna - requête unique.")

    # Indiquer ici les paramètres de la recherche d'offres d'emploi :
    # IDENTIFIANTS (ici, pas de requête OAuth pour récupérer un token. Adzuna demande app_id et app_key à chaque appel), mots-clés, lieu...
    querystring = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "where": "Hérault",
        "results_per_page": 50
    }

    response = get_offers(querystring)

    # Optionnel : exploration des données pour obtention
    # de la liste des clés par ordre alphabétique
    data = response.json()

    offers = data.get("results", [])
    logger.info("%s offres récupérées.", len(offers))

    all_keys = get_json_keys(offers)

    for key in sorted(all_keys):
        print(key)

    file_path = save_raw_response(response)
    print(f"Données enregistrées dans : {file_path}")

    logger.info("Extraction Adzuna terminée.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logger.exception("Arrêt du script à la suite d'une erreur.")
        raise
