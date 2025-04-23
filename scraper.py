import pandas as pd
import requests
import trafilatura
import re
import numpy as np
from tqdm import tqdm
from joblib import Parallel, delayed
import hashlib
import os
import time

# Configuration
INPUT_CSV = "wikipedia_articles_links(en).csv"
TEMP_CSV = "wikipedia_articles_temp.csv"
FINAL_CSV = "wikipedia_articles_links_avec_contenu.csv"
CACHE_DIR = "cache_html"
SAVE_EVERY = 50
N_JOBS = 16
RETRIES = 3
TIMEOUT = 15

os.makedirs(CACHE_DIR, exist_ok=True)

# Nettoyage de texte
def nettoyer_texte(texte):
    texte = re.sub(r'[^a-zA-Z0-9\s.]', '', texte)
    return re.sub(r'\s+', ' ', texte).strip()

# Génération nom de fichier cache
def url_to_filename(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest() + ".html"

# Téléchargement HTML avec gestion des erreurs 429 et backoff
def download_html(url, retries=RETRIES):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; MyBot/1.0; +http://example.com/bot)"}
    delay = 2  # délai initial

    for i in range(retries):
        try:
            response = requests.get(url, timeout=TIMEOUT, headers=headers)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                print(f"429 Too Many Requests : {url} | Attente {delay}s")
                time.sleep(delay)  # Attendre avant de réessayer
                delay *= 2  # Double le délai à chaque nouvel échec
            else:
                print(f"Erreur {response.status_code} pour {url}")
                return None
        except Exception as e:
            print(f"Erreur pour {url}: {e}")
            time.sleep(1)  # Attente avant une nouvelle tentative en cas de problème
    return None

# Traitement de chaque URL avec sécurité
def traiter_url(index, url):
    try:
        cache_path = os.path.join(CACHE_DIR, url_to_filename(url))
        
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                html = f.read()
        else:
            html = download_html(url)
            if not html:
                return index, np.nan
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html)

        content = trafilatura.extract(html)
        if content:
            print(f"[{index}]  {url}")
            return index, nettoyer_texte(content)
        else:
            print(f"[{index}]  Extraction vide : {url}")
            return index, np.nan

    except Exception as e:
        print(f"[{index}]  Erreur inattendue : {url} => {e}")
        return index, np.nan

# Chargement ou reprise
df = pd.read_csv(TEMP_CSV) if os.path.exists(TEMP_CSV) else pd.read_csv(INPUT_CSV)
if "contenu d'article" not in df.columns:
    df["contenu d'article"] = np.nan

df_to_process = df[df["contenu d'article"].isna()].copy()

# Traitement par lots
batch_size = SAVE_EVERY
total_batches = len(range(0, len(df_to_process), batch_size))

for start in tqdm(range(0, len(df_to_process), batch_size), total=total_batches, desc="🚀 Traitement par lots"):
    end = min(start + batch_size, len(df_to_process))
    batch = df_to_process.iloc[start:end]

    try:
        results = Parallel(n_jobs=N_JOBS)(
            delayed(traiter_url)(index, url) for index, url in zip(batch.index, batch["URL"])
        )

        for index, content in results:
            df.at[index, "contenu d'article"] = content

        df.to_csv(TEMP_CSV, index=False, encoding="utf-8")
        print(f" Sauvegarde intermédiaire après {end} lignes.")
    
    except KeyboardInterrupt:
        print("Interruption manuelle. Sauvegarde en cours...")
        df.to_csv(TEMP_CSV, index=False, encoding="utf-8")
        break

df.to_csv(FINAL_CSV, index=False, encoding="utf-8")
print(f" Fichier final : {FINAL_CSV}")
print(" Fichier temporaire sauvegardé.")
