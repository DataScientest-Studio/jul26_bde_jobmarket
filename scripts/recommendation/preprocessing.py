import pandas as pd

TEXT_COLUMNS = [
    "title",
    "description",
    "categoryLabel",
]


def prepare_offer_text(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les données textuelles utilisées par le système de recommandation.
    Crée une nouvelle colonne "text".
    """

    df = df.copy()

    for column in TEXT_COLUMNS:
        if column not in df.columns:
            raise ValueError(
                f"La colonne '{column}' est absente du DataFrame."
            )

        df[column] = df[column].fillna("")

    df["text"] = (
        df["title"]
        + " "
        + df["description"]
        + " "
        + df["categoryLabel"]
    )

    return df