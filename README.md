# Wikipedia-translation-into-local-languages
Traduire l’intégralité de Wikipédia en langues Fon, Ewe, Dendi et Yoruba.

Description
Ce projet vise à automatiser la traduction de l'intégralité des articles Wikipédia en anglais vers quatre langues africaines à faibles ressources : Fon, Ewe, Yoruba et Dendi. L'objectif est d'enrichir la documentation numérique de ces langues et d'améliorer l'accessibilité de l'information en ligne pour leurs locuteurs.

Fonctionnalités
Collecte des articles Wikipédia en anglais : Environ 7 millions d'articles.

Extraction du contenu HTML pour en extraire le contenu texte de chaque article.

Traduction vers les langues Fon, Ewe, Yoruba .

Parallélisation des tâches pour un traitement rapide et scalable.

Sauvegarde incrémentale dans des fichiers CSV pour la reprise des processus en cas d'erreur ou d'interruption.

Prérequis
Avant de commencer, assurez-vous que vous avez les éléments suivants installés sur votre machine :

Python 3.9 ou plus récent

Azure OpenAI (pour la traduction en Yoruba)

Les bibliothèques Python listées dans le fichier requirements.txt

Installation
Cloner le dépôt :

bash
Copier
Modifier
git clone <URL_DU_REPO>
cd <nom_du_dossier_du_projet>
Créer et activer un environnement virtuel :

bash
Copier
Modifier
python3 -m venv venv
source venv/bin/activate  # Sur MacOS/Linux
.\venv\Scripts\activate  # Sur Windows
Installer les dépendances :

bash
Copier
Modifier
pip install -r requirements.txt
Configurer Azure OpenAI :

Créez un compte Azure et obtenez une clé API.

Définissez les variables d'environnement pour AZURE_API_KEY et AZURE_ENDPOINT.

Utilisation
Une fois l'installation terminée, vous pouvez commencer à exécuter les scripts pour collecter et traiter les articles Wikipédia.

Étape 1 : Collecte des liens des articles
bash
Copier
Modifier
python scripts/wikipedia_all_articlelinks_getter_en.py
Étape 2 : Extraction du contenu des articles
bash
Copier
Modifier
python scripts/scraper.py
Étape 3 : Traduction vers Yoruba
bash
Copier
Modifier
python scripts/translator_yoru.py
Étape 4 : Traduction vers Fon et Ewe
bash
Copier
Modifier
python scripts/translator_fon.py
python scripts/translator_ewe.py
Fichiers de sortie
Les fichiers de sortie sont enregistrés  sous les noms suivants :

wikipedia_articles_links(en).csv : Liens des articles Wikipédia collectés.

liensetarticles : Contenu extrait des articles.

translation_yoruba.csv : Traductions en Yoruba.

translation_fon.csv : Traductions en Fon.

translation_ewe.csv : Traductions en Ewe.

Retrouvez la documentation complete et detaillée du projet ici:

