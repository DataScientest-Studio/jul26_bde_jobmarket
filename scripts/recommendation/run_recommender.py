from database import load_offers
from preprocessing import prepare_offer_text
from recommender import (
    build_tfidf_matrix,
    recommend,
)


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

    text = " ".join(df["text"].dropna())

    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        stopwords=set(french_stopwords),
        collocations=False,
    ).generate(text)

    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    main()