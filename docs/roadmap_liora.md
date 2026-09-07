# Job Market - Etape 1 - Collecte des données

L'étape 1 du projet Job Market consiste à récupérer des données relatives à des offres d'emploi par l'intermédiaire de plusieurs API.

Après extraction d'un premier jeu de données brutes, la difficulté de l'exercice provient du fait que les attributs ne sont pas identiques selon les sources.
Il convient donc de **normaliser** les données afin de créer **un seul schéma de données**.

Les sources proposées sont l'API France Travai et le site Indeed.
Toutefois, le site Indeed ne propose pas d'API spécifique à la recherche d'offres d'emploi, et nécessiterait donc d'employer une méthode de scraping.
Afin de disposer de données déjà ordonnées et de rester efficace dans la récolte de données, nous opterons pour les sources suivantes :

* API France Travail
* API Adzuna

L'objectif est de :

* documenter les champs disponibles dans chaque source ;
* identifier leur type de données ;
* comprendre leur signification ;
* préparer l'harmonisation des données entre les différentes API ;
* définir les champs qui seront conservés dans le modèle final.

> 2 fichiers JSON sont joints à ce document pour présenter un échantillon des données extraites des API France Travail et Adzuna.

---

# 1. API France Travail

## 1.1 Structure générale de la réponse
Après authentification 0Auth2, nous obtenons un token autorisant l'envoi de requête à l'API pour une durée limitée.
L'API est de type API REST et sera requêtée avec la bibliothèque `requests`de Pyhton.

La réponse de l'API France Travail contient notamment une clé `resultats`, qui contient une liste d'offres d'emploi.

Chaque élément de `resultats` correspond donc à une offre d'emploi.

---

## 1.2 Champs d'une offre

Nous listons ici les champs de premier niveau de chaque offre renvoyée par l'API France Travail.

| Champ                          | Type Python / JSON | Description                                                                        |
| ------------------------------ | ------------------ | ---------------------------------------------------------------------------------- |
| `id`                           | `str`              | Identifiant unique de l'offre France Travail                                       |
| `intitule`                     | `str`              | Intitulé de l'offre tel qu'il est publié                                           |
| `description`                  | `str`              | Description détaillée du poste                                                     |
| `dateCreation`                 | `str`              | Date et heure de création de l'offre, au format ISO 8601                           |
| `dateActualisation`            | `str`              | Date et heure de dernière actualisation                                            |
| `lieuTravail`                  | `dict`             | Informations géographiques sur le lieu de travail                                  |
| `romeCode`                     | `str`              | Code ROME du métier associé à l'offre, par exemple `D1102`                         |
| `romeLibelle`                  | `str`              | Libellé du métier ROME, par exemple `Boulanger / Boulangère`                       |
| `appellationlibelle`           | `str`              | Appellation métier plus précise associée à l'offre                                 |
| `entreprise`                   | `dict`             | Informations sur l'entreprise                                                      |
| `typeContrat`                  | `str`              | Code du type de contrat, par exemple `CDI`                                         |
| `typeContratLibelle`           | `str`              | Libellé lisible du contrat                                                         |
| `natureContrat`                | `str`              | Nature du contrat, par exemple `Contrat travail` ou `Contrat apprentissage`        |
| `experienceExige`              | `str`              | Code indiquant le niveau/caractère exigé de l'expérience                           |
| `experienceLibelle`            | `str`              | Libellé de l'expérience demandée                                                   |
| `experienceCommentaire`        | `str`              | Précisions éventuelles sur l'expérience                                            |
| `formations`                   | `list[dict]`       | Formations ou diplômes demandés                                                    |
| `langues`                      | `list[dict]`       | Langues demandées                                                                  |
| `permis`                       | `list[dict]`       | Permis éventuellement demandés                                                     |
| `outilsBureautiques`           | `list[str]`        | Outils bureautiques demandés                                                       |
| `competences`                  | `list[dict]`       | Compétences techniques ou savoirs associés à l'offre                               |
| `salaire`                      | `dict`             | Informations relatives à la rémunération                                           |
| `dureeTravailLibelle`          | `str`              | Durée et éventuellement conditions horaires de travail                             |
| `dureeTravailLibelleConverti`  | `str`              | Forme normalisée du temps de travail, par exemple `Temps plein`                    |
| `complementExercice`           | `str`              | Complément relatif aux conditions d'exercice                                       |
| `conditionExercice`            | `str`              | Conditions particulières d'exercice                                                |
| `alternance`                   | `bool`             | Indique si l'offre relève de l'alternance                                          |
| `contact`                      | `dict`             | Informations de contact                                                            |
| `agence`                       | `dict`             | Informations sur l'agence France Travail                                           |
| `nombrePostes`                 | `int`              | Nombre de postes proposés                                                          |
| `accessibleTH`                 | `bool`             | Indique si l'offre est accessible aux travailleurs handicapés                      |
| `deplacementCode`              | `str`              | Code relatif aux déplacements professionnels                                       |
| `deplacementLibelle`           | `str`              | Description des déplacements professionnels                                        |
| `qualificationCode`            | `str`              | Code du niveau de qualification                                                    |
| `qualificationLibelle`         | `str`              | Libellé du niveau de qualification                                                 |
| `codeNAF`                      | `str`              | Code NAF de l'activité de l'établissement                                          |
| `secteurActivite`              | `str`              | Code du secteur d'activité                                                         |
| `secteurActiviteLibelle`       | `str`              | Libellé du secteur d'activité                                                      |
| `trancheEffectifEtab`          | `str`              | Tranche d'effectif de l'établissement, par exemple `1 ou 2 salariés`               |
| `qualitesProfessionnelles`     | `list[dict]`       | Qualités / savoir-être professionnels recherchés                                   |
| `origineOffre`                 | `dict`             | Informations sur l'origine de l'offre                                              |
| `offresManqueCandidats`        | `bool`             | Indique si l'offre est identifiée comme rencontrant des difficultés de recrutement |
| `contexteTravail`              | `dict`             | Informations structurées sur le contexte et les conditions de travail**            |
| `entrepriseAdaptee`            | `bool`             | Indique si l'employeur est une entreprise adaptée                                  |
| `employeurHandiEngage`         | `bool`             | Indique si l'employeur est identifié comme employeur handi-engagé                  |


---

# 2. Sous-structures France Travail

Certains champs sont eux-mêmes des objets ou des listes d'objets.
Nous traitons ici les champs considérés comme pertinents pour la suite du projet.

---

## 2.1 `lieuTravail`

| Champ source             | Type    | Description                        | 
| ------------------------ | ------- | ---------------------------------- | 
| `lieuTravail.libelle`    | `str`   | Localisation affichée dans l'offre | 
| `lieuTravail.codePostal` | `str`   | Code postal                        |
| `lieuTravail.commune`    | `str`   | Code ou identifiant de commune     |

---

## 2.2 `entreprise`

| Champ source                   | Type   | Description                            | 
| ------------------------------ | ------ | -------------------------------------- |
| `entreprise.nom`               | `str`  | Nom de l'entreprise                    | 
| `entreprise.description`       | `str`  | Description éventuelle de l'entreprise | 
| `entreprise.logo`              | `str`  | URL éventuelle du logo                 | 
| `entreprise.url`               | `str`  | URL éventuelle de l'entreprise         | 
| `entreprise.entrepriseAdaptee` | `bool` | Indique si l'entreprise est adaptée    | 

---

## 2.3 `salaire`

| Champ source          | Type  | Description                              | 
| --------------------- | ----- | ---------------------------------------- | 
| `salaire.libelle`     | `str` | Texte décrivant le salaire               | 

---

## 2.4 `competences`

Le champ `competences` contient une liste d'objets.

Exemple générique :

```json
[
    {
        "code": "...",
        "libelle": "...",
        "exigence": "..."
    }
]
```

| Champ source             | Type  | Description                  | 
| ------------------------ | ----- | ---------------------------- | 
| `competences[].code`     | `str` | Code de la compétence        | 
| `competences[].libelle`  | `str` | Description de la compétence | 
| `competences[].exigence` | `str` | Niveau d'exigence associé    | 

La notation `[]` signifie que `competences` est une liste et que les champs décrits appartiennent à chacun de ses éléments.

---

## 2.5 `formations`

| Champ source                  | Type  | Description          | 
| ----------------------------- | ----- | -------------------- | 
| `formations[].codeFormation`  | `str` | Code de formation    | 
| `formations[].domaineLibelle` | `str` | Domaine de formation | 
| `formations[].niveauLibelle`  | `str` | Niveau de formation  | 
| `formations[].commentaire`    | `str` | Commentaire éventuel |
| `formations[].exigence`       | `str` | Niveau d'exigence    |

---

# 3. API Adzuna


## 3.1 Structure générale 

La réponse de l'API Adzuna contient notamment une clé `results`, qui contient une liste d'offres d'emploi.

Chaque élément de `results` correspond donc à une offre d'emploi.

Tous les champs ne sont pas obligatoirement complétés, par exemple certaines offres possèdent `salary_min` et `salary_max`, alors que d'autres ne les possèdent pas.

---

## 3.2 Champs d'une offre

| Champ                 | Type Python / JSON | Description                                                                                          |
| --------------------- | ------------------ | ---------------------------------------------------------------------------------------------------- |
| `id`                  | `str`              | Identifiant unique de l'offre chez Adzuna                                                            |
| `title`               | `str`              | Intitulé de l'offre d'emploi                                                                         |
| `description`         | `str`              | Description textuelle de l'offre                                                                     |
| `created`             | `str`              | Date et heure de publication/création de l'offre au format ISO 8601                                  |
| `redirect_url`        | `str`              | URL Adzuna permettant d'accéder à l'offre originale                                                  |
| `company`             | `dict` / objet     | Informations sur l'entreprise ou l'organisme recruteur                                               |
| `category`            | `dict` / objet     | Catégorie métier attribuée par Adzuna                                                                |
| `location`            | `dict` / objet     | Informations géographiques associées à l'offre                                                       |
| `latitude`            | `float`            | Latitude approximative de l'offre                                                                    |
| `longitude`           | `float`            | Longitude approximative de l'offre                                                                   |
| `contract_type`       | `str`              | Type de contrat, par ex. `permanent` ou `contract`                                                   |
| `contract_time`       | `str`              | Temps de travail, par ex. `full_time` ou `part_time`                                                 |
| `salary_min`          | `int` ou `float`   | Borne basse du salaire associé à l'offre                                                             |
| `salary_max`          | `int` ou `float`   | Borne haute du salaire associé à l'offre                                                             |
| `salary_is_predicted` | `str`              | Indique si le salaire a été estimé par Adzuna ; dans l'extraction, la valeur est par exemple `"0"` |
| `adref`               | `str`              | Référence technique/interne utilisée par Adzuna pour identifier ou suivre l'annonce                  |
| `__CLASS__`           | `str`              | Métadonnée technique indiquant le type d'objet Adzuna retourné                                       |

---

# 4. Sous-structures Adzuna

Certains champs sont eux-mêmes des objets ou des listes d'objets.
Nous traitons ici les champs considérés comme pertinents pour la suite du projet.

---

## 4.1 `company`
company

|-- display_name       str

|-- __CLASS__          str

## 4.2 `category`
category

|-- tag                str

|-- label              str

|-- __CLASS__          str

## 4.3 `location`
location

|-- display_name       str

|-- area               list[str]

|-- __CLASS__          str

---

# Job Market - Etape 1 - Normalisation des données

Cette section définit le schéma commun à construire à partir des données France Travail et Adzuna.

L'API France Travail fournit des données plus riches que l'API Adzuna.
**Certains champs proposés par France Travail seront donc maintenus**, quitte à obtenir des valeurs "null" sur ces champs pour les modalités transmises par Adzuna.

Liste des champs France Travail maintenus après normalisation, malgré l'absence d'équivalence des champs Adzuna :

* **romeCode** : nomenclature de France Travail destinée à classifier les métiers et les emplois. La première lettre du code ROME fournit le code du grand domaine de l'offre d'emploi, par exemple :
    * A : Agriculture / Pêche / Espaces verts et naturels / Soins aux animaux
    * B : Arts / Artisanat d’art
    * C : Banque / Assurance
    * C15 : Immobilier
    * ...

* **codeNAF** : (Nomenclature d'activités française) ce code est attribué par l'INSEE à une entreprise ou à un établissement selon son _activité principale_.

* **competences** et **formations** sont également maintenus, dans les champs qui nous intéressent, afin d'étoffer les informations dans le futur dashboard du projet.

> Certains champs pourront éventuellement être complétés par des données issues de webscraping, notamment les données issues des entreprises les plus prolifiques.

---

# 1 Tableau final de mapping

Les données normalisées devront présenter un champ **`source`** qui indiquera soit France Travail soit Adzuna.

Le tableau suivant reprend le schéma normalisé proposé et précise, pour chaque champ, son type ainsi que sa correspondance dans les deux sources.

| Champ normalisé     | Type final   | France Travail (champ / type)              | Adzuna (champ / type)                        |
| ------------------- | ------------ | ------------------------------------------ | -------------------------------------------- |
| `source`            | `str`        | `France Travail` (`str`)                   | `Adzuna` (`str`)                             |
| `source_id`         | `str`        | `id` (`str`)                               | `id` (`str`)                                 |
| `title`             | `str`        | `intitule` (`str`)                         | `title` (`str`)                              |
| `company`           | `str`        | `entreprise.nom` (`str`)                   | `company.display_name` (`str`)               |
| `description`       | `str`        | `description` (`str`)                      | `description` (`str`)                        |
| `creationDate`      | `str`        | `dateCreation` (`str`)                     | `created` (`str`)                            |
| `contractType`      | `str`        | `typeContrat` (`str`)                      | `contract_type` (`str`)                      |
| `contractTime`      | `str`        | `dureeTravailLibelleConverti` (`str`)      | `contract_time` (`str`)                      |
| `locationZipCode`   | `str`        | `lieuTravail.codePostal` (`str`)           | —                                            |
| `locationDepartment`| `str`        | `lieuTravail.libelle` (`str`)              | `location.area[2]` (`list[str]`)             |
| `locationCity`      | `str`        | `lieuTravail.commune` (`str`)              | `location.area[3]` (`list[str]`)             |
| `locationLatitude`  | `float`      | `lieuTravail.latitude` (`float`)           | `latitude` (`float`)                         |
| `locationLongitude` | `float`      | `lieuTravail.longitude` (`float`)          | `longitude` (`float`)                        |
| `salary`            | `float`      | `salaire.libelle` (`str`)                  | `salary_min`, `salary_max` (`int` / `float`) |
| `url`               | `str`        | `origineOffre.urlOrigine` (`str`)          | `redirect_url` (`str`)                       |
| `codeNAF`           | `str`        | `codeNAF` (`str`)                          | —                                            |
| `romeCode`          | `str`        | `romeCode` (`str`)                         | —                                            |
| `category`          | `str`        | `romeCode` (`str`)                         | `category.tag` (`str`)                       |
| `categoryLabel`     | `str`        | `romeLibelle` (`str`)                      | `category.tag` (`str`)                       |
| `skills`            | `list[str]`  | `competences[].libelle` (`str`)            | —                                            |
| `education`         | `str`        | `formations[].niveauLibelle` (`str`)       | —                                            |
| `educationField`    | `str`        | `formations[].domaineLibelle` (`str`)      | —                                            |


# 2 Champs nécessitant une transformation des données

Les champs ayant besoin d'être processés avant intégration dans une BDD normalisée sont notamment :

## 2.1 API France Travail

*  `lieuTravail.libelle`  --> `locationDepartment` et `locationCity` : Le département (en chiffres) et le nom de la ville doivent être extraits d'une chaîne de caractère de la forme "34 - Montpellier". Cette construction du libellé est **uniforme** sur l'ensemble des offres d'emplois.
*  `salaire.libelle`  --> `salary` : le libellé fourni par France Travail est une chaîne de caractères saisie par l'API, mais dont le salaire doit être extrait. 
    * Idée : extraire le(s) salaire(s) de la chaîne de caractères grâce à leur format uniforme = 4 chiffres, 1 point, 1 chiffre.
    * Faire la moyenne des résultats obtenus, car il est parfois indiqué une fouchette de salaires.

## 2.2 API Adzuna

* `location.area` --> `locationDepartment` : Le département se trouve de manière **uniforme** en 3ème position dans la liste du champ. On prendre donc `locationRegion = location.area[2]`. Il faudra ensuite lui faire corresondre le **numéro du département**, ce qui est plus robuste que le nom en toutes lettres.
* `location.area` --> `locationCity` : Lorsqu'elle est indiquée, la ville se trouve de manière **uniforme** en 4ème position dans la liste du champ. On prendre donc `locationCity = location.area[3]` en prenant garde de **traiter le cas où aucune ville n'est renseignée**.
*  `salaire_min` et `salaire_max` --> `salary` : calculer la moyenne des 2 champs.

## 2.3 Les catégories d'offres d'emploi

La taxonomie commune du projet **Job Market** reprend les domaines et sous-domaines du référentiel **ROME de France Travail**.

L'objectif est de conserver la précision disponible chez France Travail :

- pour **France Travail**, `category` est déterminé à partir de `romeCode` ;
- pour **Adzuna**, `category.tag` est traduit vers la catégorie ROME la plus proche ;
  - `categoryLabel` contient le libellé lisible associé à `category` ;
  - les catégories absentes, trop générales ou inconnues sont classées dans `UNKNOWN`.

Ainsi, un `romeCode` France Travail égal à `M1805` donnerait le format suivant :

```json
{
  "romeCode": "M1805",
  "category": "M18",
  "categoryLabel": "Informatique / Télécommunication"
}
```

Lorsqu'aucun sous-domaine spécifique du mapping n'est défini, seule la lettre du grand domaine est utilisée. Par exemple, un code `F1106` est classé en `F`.

Concernant les catégories fournies par l'API Adzuna, la liste des **29 catégories** (30 catégories si l'on considère "unknown") a été récupérée via l'API Adzuna `/jobs/{country}/categories` qui *"list available categories"*.

On obtient le tableau de mapping suivant pour les catégories d'offres d'emploi :

| `category` | `categoryLabel` | `category.tag` Adzuna associés |
|---|---|---|
| `A` | Agriculture / Pêche / Espaces verts et naturels / Soins aux animaux | — |
| `B` | Arts / Artisanat d'art | `creative-design-jobs` |
| `C` | Banque / Assurance | — |
| `C15` | Immobilier | `property-jobs` |
| `D` | Commerce / Vente | `sales-jobs`, `retail-jobs` |
| `E` | Communication / Multimédia | — |
| `F` | Bâtiment / Travaux Publics | `trade-construction-jobs` |
| `G` | Hôtellerie - Restauration / Tourisme / Animation | `travel-jobs`, `hospitality-catering-jobs` |
| `H` | Industrie | `manufacturing-jobs`, `energy-oil-gas-jobs` |
| `I` | Installation / Maintenance | `maintenance-jobs` |
| `J` | Santé | `healthcare-nursing-jobs` |
| `K` | Services à la personne / à la collectivité | `social-work-jobs`, `charity-voluntary-jobs`, `domestic-help-cleaning-jobs`, `teaching-jobs` |
| `L` | Spectacle | — |
| `L14` | Sport | — |
| `M` | Achats / Comptabilité / Gestion | `accounting-finance-jobs`, `admin-jobs` |
| `M13` | Direction d'entreprise | — |
| `M14` | Conseil / Études | `consultancy-jobs`, `engineering-jobs`, `scientific-qa-jobs`, `customer-services-jobs`, `legal-jobs` |
| `M15` | Ressources Humaines | `hr-jobs` |
| `M16` | Secrétariat / Assistanat | — |
| `M17` | Marketing / Stratégie commerciale | `pr-advertising-marketing-jobs` |
| `M18` | Informatique / Télécommunication | `it-jobs` |
| `N` | Transport / Logistique | `logistics-warehouse-jobs` |
| `UNKNOWN` | Non classé / Domaine inconnu | `other-general-jobs`, `graduate-jobs`, `part-time-jobs`, catégorie absente ou tag inconnu |
