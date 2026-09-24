from database import load_offers
from preprocessing import prepare_offer_text
from recommender import (
    build_tfidf_matrix,
    recommend,
)

# test du wordcloud
from recommender import show_wordcloud

def main():

    print("Chargement des offres depuis MongoDB...")

    df = load_offers()

    if df.empty:
        print("Aucune offre trouvée dans MongoDB.")
        return

    print(f"{len(df)} offres chargées.")

    # Préparation du texte
    df = prepare_offer_text(df)

    print("Construction de la matrice TF-IDF...")

    vectorizer, tfidf_matrix = build_tfidf_matrix(df)

    # -----------------------------------
    # Préférences utilisateur de test
    # -----------------------------------

    preferences = {
        "keywords": (
            "data engineer python sql "
            "docker pipelines de données"
        ),
        "locationDepartment": "34",
        "categoryLabel": "Informatique / Télécommunication",
    }

    recommendations = recommend(
        df=df,
        vectorizer=vectorizer,
        tfidf_matrix=tfidf_matrix,
        keywords=preferences["keywords"],
        locationDepartment=preferences["locationDepartment"],
        categoryLabel=preferences["categoryLabel"],
        top_n=10,
    )

    columns = [
        "title",
        "company",
        "locationCity",
        "categoryLabel",
        "score",
    ]

    print("\nOffres recommandées :\n")

    print(
        recommendations[columns].to_string(
            index=False
        )
    )

    # Test du wordcloud
    show_wordcloud(df)

if __name__ == "__main__":
    main()