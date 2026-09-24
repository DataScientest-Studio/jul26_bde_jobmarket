import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import BulkWriteError


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

load_dotenv()


def get_collection():
    client = MongoClient(os.getenv("MONGO_ATLAS_URI"))

    db = client[os.getenv("MONGO_DB")]

    return db["offers"]


def load_json(file_path):
    """Charge un fichier JSON normalisé."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def process_file(file_path, collection):
    """Insère dans MongoDB les offres contenues dans un fichier JSON."""

    offers = load_json(file_path)

    if not offers:
        print(f"{file_path} : aucune offre.")
        return

    try:
        result = collection.insert_many(
            offers,
            ordered=False,
        )

        print(
            f"{file_path} : "
            f"{len(result.inserted_ids)} offre(s) insérée(s)."
        )

    except BulkWriteError as error:
        write_errors = error.details.get("writeErrors", [])

        duplicate_errors = [
            err for err in write_errors
            if err.get("code") == 11000
        ]

        other_errors = [
            err for err in write_errors
            if err.get("code") != 11000
        ]

        inserted = error.details.get("nInserted", 0)

        print(f"{inserted} offres insérées")
        print(f"{len(duplicate_errors)} doublons ignorés")

        if other_errors:
            print("Erreurs MongoDB inattendues :", other_errors)
            raise
            
    
def main():
    collection = get_collection()

    processed_files = sorted(PROCESSED_DIR.rglob("*.json"))

    if not processed_files:
        print(f"Aucun fichier JSON trouvé dans {PROCESSED_DIR}")
        return

    for file_path in processed_files:
        process_file(file_path, collection)


if __name__ == "__main__":
    main()