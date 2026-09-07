import json
import re
import numpy as np
from pathlib import Path


RAW_DIR = Path("data/raw/france_travail")
PROCESSED_DIR = Path("data/processed/france_travail")


CATEGORY_LABELS = {
    "A": "Agriculture / Pêche / Espaces verts et naturels / Soins aux animaux",
    "B": "Arts / Artisanat d'art",
    "C": "Banque / Assurance",
    "C15": "Immobilier",
    "D": "Commerce / Vente",
    "E": "Communication / Multimédia",
    "F": "Bâtiment / Travaux Publics",
    "G": "Hôtellerie - Restauration / Tourisme / Animation",
    "H": "Industrie",
    "I": "Installation / Maintenance",
    "J": "Santé",
    "K": "Services à la personne / à la collectivité",
    "L": "Spectacle",
    "L14": "Sport",
    "M": "Achats / Comptabilité / Gestion",
    "M13": "Direction d'entreprise",
    "M14": "Conseil / Études",
    "M15": "Ressources Humaines",
    "M16": "Secrétariat / Assistanat",
    "M17": "Marketing / Stratégie commerciale",
    "M18": "Informatique / Télécommunication",
    "N": "Transport / Logistique",
    "UNKNOWN": "Non classé / Domaine inconnu",
}


ROME_SUBCATEGORIES = {
    "C15",
    "L14",
    "M13",
    "M14",
    "M15",
    "M16",
    "M17",
    "M18",
}


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


def extract_labels(items, key="libelle"):
    """
    Extrait les valeurs d'un champ dans une liste.

    Exemple :
        [{"libelle": "Python"}, {"libelle": "SQL"}]
    devient :
        ["Python", "SQL"]
    """
    if not isinstance(items, list):
        return []

    return [
        item[key]
        for item in items
        if isinstance(item, dict)
        and isinstance(item.get(key), str)
        and item[key].strip()
    ]


def parse_salary(label):
    """
    Extrait une valeur numérique depuis salaire.libelle.

    Si deux montants en euros sont présents, leur moyenne est utilisée.
    Exemple :
        "Mensuel de 1800 Euros à 2200 Euros"
        -> 2000.0

    Attention :
    cette fonction normalise la représentation numérique mais pas
    la périodicité du salaire (horaire, mensuel, annuel).
    """
    if not isinstance(label, str) or not label.strip():
        return None

    matches = re.findall(
        r"(\d[\d\s]*(?:[.,]\d+)?)\s*(?:€|euros?)",
        label,
        flags=re.IGNORECASE,
    )

    if not matches:
        return None

    amounts = []

    for value in matches:
        normalized_value = value.replace(" ", "").replace(",", ".")

        try:
            amounts.append(float(normalized_value))
        except ValueError:
            continue

    if not amounts:
        return None

    if len(amounts) >= 2:
        return np.mean(amounts)

    return amounts[0]


def normalize_category(rome_code):
    """
    Détermine la catégorie normalisée à partir du code ROME.

    Les sous-domaines explicitement présents dans le mapping sont conservés.
    Par exemple :
        M1805 -> M18 / Informatique / Télécommunication
        C1504 -> C15 / Immobilier

    Pour les autres codes, la première lettre définit le grand domaine.
    """
    if not isinstance(rome_code, str) or not rome_code.strip():
        return "UNKNOWN", CATEGORY_LABELS["UNKNOWN"]

    normalized_rome_code = rome_code.strip().upper()
    subcategory = normalized_rome_code[:3]

    if subcategory in ROME_SUBCATEGORIES:
        category = subcategory
    else:
        main_category = normalized_rome_code[0]
        category = (
            main_category
            if main_category in CATEGORY_LABELS
            else "UNKNOWN"
        )

    return category, CATEGORY_LABELS[category]


def normalize_offer(offer):
    """
    Transforme une offre France Travail vers le schéma normalisé du projet.
    """
    entreprise = offer.get("entreprise") or {}
    lieu_travail = offer.get("lieuTravail") or {}
    salaire = offer.get("salaire") or {}
    origine_offre = offer.get("origineOffre") or {}

    location_label = (offer.get("lieuTravail") or {}).get("libelle", "")
    location_region, separator, location_city = location_label.partition(" - ")
    if not separator:
        location_region = None
        location_city = None

    rome_code = offer.get("romeCode")
    category, category_label = normalize_category(rome_code)

    return {
        "source": "France Travail",
        "source_id": offer.get("id"),
        "title": offer.get("intitule"),
        "company": entreprise.get("nom"),
        "description": offer.get("description"),
        "creationDate": offer.get("dateCreation"),
        "contractType": offer.get("typeContrat"),
        "contractTime": offer.get("dureeTravailLibelleConverti"),
        "locationZipCode": lieu_travail.get("codePostal"),
        "locationDepartment": location_region,
        "locationCity": location_city,
        "locationLatitude": to_float(lieu_travail.get("latitude")),
        "locationLongitude": to_float(lieu_travail.get("longitude")),
        "salary": parse_salary(salaire.get("libelle")),
        "url": origine_offre.get("urlOrigine"),
        "codeNAF": offer.get("codeNAF"),
        "category": category,
        "categoryLabel": category_label,
        "romeCode": rome_code,
        "romeLibelle": offer.get("romeLibelle"),
        "skills": extract_labels(offer.get("competences"), key="libelle"),
        "education": extract_labels(offer.get("formations"), key="niveauLibelle"),
        "educationField": extract_labels(offer.get("formations"), key="domaineLibelle")
    }


def process_file(raw_file: Path):
    """
    Normalise un fichier RAW France Travail.

    La réponse France Travail contient les offres dans la clé 'resultats'.
    Le fichier PROCESSED conserve le même nom que le fichier RAW.
    """
    raw_data = load_json(raw_file)

    offers = raw_data.get("resultats", [])

    if not isinstance(offers, list):
        raise ValueError(
            f"La clé 'resultats' de {raw_file} ne contient pas une liste."
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
    Normalise tous les fichiers JSON présents dans data/raw/france_travail.
    """
    raw_files = sorted(RAW_DIR.glob("*.json"))

    if not raw_files:
        print(f"Aucun fichier JSON trouvé dans {RAW_DIR}")
        return

    for raw_file in raw_files:
        process_file(raw_file)


if __name__ == "__main__":
    main()
