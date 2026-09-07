import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import BulkWriteError


PROCESSED_DIR = Path("data/processed")

load_dotenv()


def get_collection():
    client = MongoClient(
        host=os.getenv("MONGO_HOST"),
        port=int(os.getenv("MONGO_PORT")),
        username=os.getenv("MONGO_USER"),
        password=os.getenv("MONGO_PASSWORD"),
        authSource=os.getenv("MONGO_DB"),
    )

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
        inserted = error.details["nInserted"]

        print(
            f"{file_path} : "
            f"{inserted} offre(s) insérée(s), "
            f"{len(offers) - inserted} offre(s) ignorée(s)."
        )


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