import json
import math
import os
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


# ----- Configuration

SEARCH_URL = "https://api.adzuna.com/v1/api/jobs/fr/search"

RAW_DIR = Path("data/raw/adzuna")

RESULTS_PER_PAGE = 50
DELAY = 3

START_PAGE = 1


# ----- Récupération des identifiants Adzuna
# sous forme de variables d'environnement

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")


# ----- Récupération d'une page d'offres d'emploi

def get_offers(querystring, page):
    """
    Récupère une page d'offres d'emploi depuis l'API Adzuna.
    """

    url = f"{SEARCH_URL}/{page}"

    response = requests.get(
        url,
        params=querystring
    )

    response.raise_for_status()

    return response


# ----- Enregistrement des données brutes

def save_raw_response(response, timestamp, page):
    """
    Enregistre une page de la réponse de l'API Adzuna au format JSON.
    """

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    file_path = RAW_DIR / f"adzuna_{timestamp}_page_{page:03d}.json"

    data = response.json()

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

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

    querystring = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "where": "Hérault",
        "results_per_page": RESULTS_PER_PAGE
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ----- Première page de la reprise

    response = get_offers(querystring, START_PAGE)
    data = response.json()

    total_results = data["count"]

    total_pages = math.ceil(
        total_results / RESULTS_PER_PAGE
    )

    all_keys = set()
    total_downloaded = 0

    # Traitement de la page 154
    offers = data.get("results", [])

    save_raw_response(response, timestamp, START_PAGE)

    all_keys.update(
        get_json_keys(offers)
    )

    total_downloaded += len(offers)

    print(
        f"Page {START_PAGE}/{total_pages} - "
        f"{total_downloaded} nouvelles offres récupérées"
    )

    # ----- Pages suivantes

    for page in range(START_PAGE + 1, total_pages + 1):

        time.sleep(DELAY)

        response = get_offers(querystring, page)
        data = response.json()

        offers = data.get("results", [])

        if not offers:
            print(f"Aucune offre à la page {page}. Arrêt.")
            break

        save_raw_response(response, timestamp, page)

        all_keys.update(
            get_json_keys(offers)
        )

        total_downloaded += len(offers)

        print(
            f"Page {page}/{total_pages} - "
            f"{total_downloaded} nouvelles offres récupérées"
        )

    querystring = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "where": "Hérault",
        "results_per_page": RESULTS_PER_PAGE
    }

    # Même timestamp pour identifier toutes les pages appartenant à une même extraction
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ----- Première page

    response = get_offers(querystring, page=1)
    data = response.json()

    total_results = data["count"]

    total_pages = math.ceil(
        total_results / RESULTS_PER_PAGE
    )

    print(f"{total_results} offres disponibles.")
    print(f"{total_pages} pages à récupérer.")

    save_raw_response(response, timestamp, page=1)

    #all_keys = get_json_keys(data["results"])

    total_downloaded = len(data["results"])

    print(
        f"Page 1/{total_pages} - "
        f"{total_downloaded} offres récupérées"
    )

    # ----- Pages suivantes

    for page in range(START_PAGE+1, total_pages + 1):

        time.sleep(DELAY)

        response = get_offers(querystring, page)
        data = response.json()

        offers = data.get("results", [])

        if not offers:
            print(f"Aucune offre à la page {page}. Arrêt.")
            break

        save_raw_response(response, timestamp, page)

        #all_keys.update(
        #    get_json_keys(offers)
        #)

        total_downloaded += len(offers)

        print(
            f"Page {page}/{total_pages} - "
            f"{total_downloaded} offres récupérées"
        )

    # ----- Affichage des clés rencontrées

    #for key in sorted(all_keys):
    #    print(key)

    print(
        f"Extraction terminée : "
        f"{total_downloaded} offres récupérées."
    )


if __name__ == "__main__":
    main()