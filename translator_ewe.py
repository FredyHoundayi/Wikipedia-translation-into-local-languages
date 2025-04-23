import os
import re
import time
import hashlib
import requests
import numpy as np
import pandas as pd
from tqdm import tqdm
from joblib import Parallel, delayed
from transformers import pipeline
import nltk
from nltk.tokenize import sent_tokenize
import trafilatura
from threading import Lock

# =====================
# CONFIGURATION GÉNÉRALE
# =====================
INPUT_CSV = "liensetarticles.csv"
CACHE_DIR = "cache_html"
RETRIES = 3
TIMEOUT = 15
N_JOBS = -1

# =====================
# INIT
# =====================
nltk.download('punkt')
os.makedirs(CACHE_DIR, exist_ok=True)

pipe = pipeline("text2text-generation", model="masakhane/m2m100_418M_fr_ewe_rel", device=0)
lock = Lock()

# =====================
# UTILITAIRES
# =====================
def nettoyer_texte(texte):
    texte = re.sub(r'[^\w\s.,;:!?\'\"()\-\n]', '', texte)
    return re.sub(r'\s+', ' ', texte).strip()

def url_to_filename(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest() + ".html"

def download_html(url, retries=RETRIES):
    headers = {"User-Agent": "Mozilla/5.0"}
    delay = 2
    for _ in range(retries):
        try:
            response = requests.get(url, timeout=TIMEOUT, headers=headers)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 429:
                time.sleep(delay)
                delay *= 2
        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête: {e}")
            time.sleep(1)
    return None

def extraire_contenu(url):
    cache_path = os.path.join(CACHE_DIR, url_to_filename(url))
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        html = download_html(url)
        if not html:
            return np.nan
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(html)
    content = trafilatura.extract(html)
    return nettoyer_texte(content) if content else np.nan

def traduire_en_fon(text):
    try:
        sentences = sent_tokenize(text, language='french')
        traductions = []
        for sent in sentences:
            try:
                if len(pipe.tokenizer(sent)['input_ids']) <= 1020:
                    traductions.append(pipe(sent)[0]['generated_text'])
                else:
                    print(f"⏭️ Phrase ignorée ({len(pipe.tokenizer(sent)['input_ids'])} tokens)")
            except Exception as e:
                print(f"[Erreur phrase] {e}")
        return " ".join(traductions).strip() if traductions else "[Erreur traduction]"
    except Exception as e:
        print(f"[Erreur traduction] {e}")
        return "[Erreur traduction]"

# =====================
# LECTURE DU CSV
# =====================
df = pd.read_csv(INPUT_CSV)

if "contenu d'article" not in df.columns:
    df["contenu d'article"] = np.nan
if "contenu_fon" not in df.columns:
    df["contenu_fon"] = np.nan

lignes_a_traiter = df[(df["contenu_fon"].isna()) | (df["contenu_fon"] == "[Erreur traduction]")].index.tolist()
print(f"🔎 Lignes à traiter : {len(lignes_a_traiter)}")

# =====================
# TRAITEMENT PAR LIGNE
# =====================
def traiter_et_sauvegarder(idx):
    global df
    row = df.loc[idx]
    url = row.get("URL") or row.get("lien de l’article")
    if pd.isna(url):
        print(f"Erreur: URL manquante pour la ligne {idx}")
        return

    contenu = row["contenu d'article"]
    if pd.isna(contenu):
        contenu = extraire_contenu(url)
        if pd.isna(contenu):
            print(f"Erreur: Impossible d'extraire le contenu pour la ligne {idx}")
            return

    traduction = row["contenu_fon"]
    if pd.isna(traduction) or traduction == "[Erreur traduction]":
        traduction = traduire_en_fon(contenu)
        if traduction == "[Erreur traduction]":
            print(f"Erreur: Impossible de traduire le contenu pour la ligne {idx}")
            return

    with lock:
        df.at[idx, "contenu d'article"] = contenu
        df.at[idx, "contenu_fon"] = traduction
        df.to_csv(INPUT_CSV, index=False)
        print(f"💾 Ligne {idx} sauvegardée.")

# =====================
# LANCEMENT DU TRAITEMENT
# =====================
for idx in lignes_a_traiter:
    try:
        traiter_et_sauvegarder(idx)
    except Exception as e:
        print(f"[Erreur ligne {idx}] : {e}")
        break

print("\n✅ Traitement terminé. Fichier à jour :", INPUT_CSV)
