import json
from pathlib import Path


RAW_DIR = Path("data/raw/adzuna")
PROCESSED_DIR = Path("data/processed/adzuna")


def load_json(file_path: Path):
    """Charge un fichier JSON."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, file_path: Path):
    """Enregistre les données normalisées au format JSON."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4,
        )


def to_float(value):
    """Convertit une valeur numérique en float si possible."""
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_salary(salary_min, salary_max):
    """
    Produit une valeur unique à partir de salary_min et salary_max.

    - si les deux valeurs existent : moyenne ;
    - si une seule existe : cette valeur ;
    - sinon : None.
    """
    minimum = to_float(salary_min)
    maximum = to_float(salary_max)

    if minimum is not None and maximum is not None:
        return (minimum + maximum) / 2

    if minimum is not None:
        return minimum

    if maximum is not None:
        return maximum

    return None

def normalize_offer(offer):
    """
    Transforme une offre Adzuna vers le schéma normalisé du projet.
    """
    company = offer.get("company") or {}
    category = offer.get("category") or {}
    location = offer.get("location") or {}
    area = location.get("area") or []

    return {
        "id": offer.get("id"),
        "title": offer.get("title"),
        "company": company.get("display_name"),
        "description": offer.get("description"),
        "creationDate": offer.get("created"),
        "contractType": offer.get("contract_type"),
        "contractTime": offer.get("contract_time"),
        "locationZipCode": None,
        "locationRegion": area[2] if len(area) > 2 else None,
        "locationCity": area[3] if len(area) > 2 else None,
        "locationLatitude": to_float(offer.get("latitude")),
        "locationLongitude": to_float(offer.get("longitude")),
        "salary": normalize_salary(
            offer.get("salary_min"),
            offer.get("salary_max"),
        ),
        "url": offer.get("redirect_url"),
        "codeNAF": None,
        "categoryLabel": category.get("label"),
        "romeCode": None,
        "romeLibelle": None,
        "skills": [],
        "education": None,
        "educationField": None,
    }


def process_file(raw_file: Path):
    """
    Normalise un fichier RAW Adzuna.

    La réponse Adzuna contient les offres dans la clé 'results'.
    Le fichier PROCESSED conserve le même nom que le fichier RAW.
    """
    raw_data = load_json(raw_file)

    offers = raw_data.get("results", [])

    if not isinstance(offers, list):
        raise ValueError(
            f"La clé 'results' de {raw_file} ne contient pas une liste."
        )

    normalized_offers = [normalize_offer(offer) for offer in offers]

    processed_file = PROCESSED_DIR / raw_file.name
    save_json(normalized_offers, processed_file)

    print(
        f"{raw_file.name} : "
        f"{len(normalized_offers)} offre(s) normalisée(s) "
        f"-> {processed_file}"
    )


def main():
    """
    Normalise tous les fichiers JSON présents dans data/raw/adzuna.
    """
    raw_files = sorted(RAW_DIR.glob("*.json"))

    if not raw_files:
        print(f"Aucun fichier JSON trouvé dans {RAW_DIR}")
        return

    for raw_file in raw_files:
        process_file(raw_file)


if __name__ == "__main__":
    main()
