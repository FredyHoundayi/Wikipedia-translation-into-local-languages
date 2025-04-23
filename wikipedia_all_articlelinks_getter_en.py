import requests
import csv
import os
import time
import sys

# URL de base pour l'API MediaWiki de Wikipedia
BASE_URL = "https://fr.wikipedia.org/w/api.php"

# En-têtes pour l'identification de l'utilisateur
HEADERS = {
    "User-Agent": "MyWikipediaScraper/1.0 (fredhoundayi@gmail.com)"
}

# Paramètres de base pour la requête d'articles
PARAMS_TEMPLATE = {
    "action": "query",
    "format": "json",
    "list": "allpages",
    "aplimit": "50",
    "apnamespace": "0",
    "apfilterredir": "nonredirects"
}

CSV_FILE = "wikipedia_articles_links(fr)_full.csv"
TOKEN_FILE = "last_token.txt"


def get_total_article_count():
    try:
        response = requests.get(BASE_URL, params={
            "action": "query",
            "format": "json",
            "meta": "siteinfo",
            "siprop": "statistics"
        }, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()["query"]["statistics"]["articles"]
    except requests.RequestException as e:
        print(f"Erreur lors de la récupération du nombre d'articles : {e}")
        return None


def get_last_continue_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return f.read().strip()


def save_continue_token(token):
    with open(TOKEN_FILE, "w") as f:
        f.write(token)


def get_current_article_count():
    if not os.path.exists(CSV_FILE):
        return 0
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        return sum(1 for line in f) - 1  # -1 pour l'en-tête


def print_dynamic_status(collected, total):
    sys.stdout.write(f"\r{collected} liens collectés sur environ {total}")
    sys.stdout.flush()


def collecte_liens_articles():
    total_expected = get_total_article_count()
    if total_expected is None:
        print("Impossible de continuer sans connaître le total d’articles.")
        return

    # Créer le fichier CSV s’il n’existe pas
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "URL"])

    collected_so_far = get_current_article_count()
    continue_token = get_last_continue_token()

    print_dynamic_status(collected_so_far, total_expected)

    while True:
        params = PARAMS_TEMPLATE.copy()
        if continue_token:
            params["apcontinue"] = continue_token

        try:
            response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            pages = data["query"]["allpages"]

            with open(CSV_FILE, mode="a", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                for page in pages:
                    title = page["title"]
                    url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                    writer.writerow([title, url])
                    collected_so_far += 1
                    print_dynamic_status(collected_so_far, total_expected)

            if "continue" in data:
                continue_token = data["continue"]["apcontinue"]
                save_continue_token(continue_token)
                time.sleep(0.1)
            else:
                break

        except requests.RequestException as e:
            print(f"\nErreur lors de la requête : {e}")
            break

    print(f"\nTerminé : {collected_so_far}liens d articles collectés sur environ {total_expected}. Résultat dans {CSV_FILE}")


if __name__ == "__main__":
    collecte_liens_articles()
