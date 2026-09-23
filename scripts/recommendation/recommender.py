import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_tfidf_matrix(df: pd.DataFrame):
    """
    Transforme le texte des offres en matrice TF-IDF.
    """

    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        max_features=5000,
    )

    tfidf_matrix = vectorizer.fit_transform(
        df["text"]
    )

    return vectorizer, tfidf_matrix


def recommend(
    df: pd.DataFrame,
    vectorizer,
    tfidf_matrix,
    keywords: str,
    locationDepartment: str | None = None,
    categoryLabel: str | None = None,
    top_n: int = 10,
):
    """
    Recommande les offres les plus proches
    des préférences de l'utilisateur.
    """

    if not keywords.strip():
        raise ValueError(
            "Les mots-clés utilisateur ne peuvent pas être vides."
        )

    # Transformation des préférences utilisateur
    user_vector = vectorizer.transform([keywords])

    # Calcul de la similarité entre l'utilisateur
    # et chacune des offres
    similarities = cosine_similarity(
        user_vector,
        tfidf_matrix,
    )[0]

    results = df.copy()

    results["score"] = similarities

    # Filtre géographique
    if locationDepartment is not None:
        results = results[
            results["locationDepartment"] == locationDepartment
        ]

    # Filtre sur le grand domaine
    if categoryLabel is not None:
        results = results[
            results["categoryLabel"] == categoryLabel
        ]

    # Classement du score le plus élevé au plus faible
    results = results.sort_values(
        by="score",
        ascending=False,
    )

    return results.head(top_n)