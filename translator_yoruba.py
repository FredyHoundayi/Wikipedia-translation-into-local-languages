import os, re, time, hashlib, requests, numpy as np, pandas as pd, trafilatura
from tqdm import tqdm
from joblib import Parallel, delayed
from openai import AzureOpenAI

# === Configuration ===
INPUT_CSV = "lienestarticles.csv"
CACHE_DIR = "cache_html"
RETRIES = 3
TIMEOUT = 15
BATCH_SIZE = 100  # Taille raisonnable pour la traduction + HTML
N_JOBS = -1  # Nombre de threads en parallèle

# === Fonctions utilitaires ===
def nettoyer_texte(texte):
    texte = re.sub(r'[^a-zA-Z0-9\s.,;:!?\'\"()\-\n]', '', texte)
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
                print("429 - attente", delay, "s")
                time.sleep(delay)
                delay *= 2
        except Exception as e:
            print("Erreur réseau:", e)
            time.sleep(1)
    return None

def extraire_contenu(url):
    os.makedirs(CACHE_DIR, exist_ok=True)
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

def traduire_en_yoruba(text):
    try:
        client = AzureOpenAI(
            api_key="your api key",
            api_version="2024-05-01-preview",
            azure_endpoint="https://ishee-m3abx6k5-eastus2.openai.azure.com/"
        )
        response = client.chat.completions.create(
            model="gpt-4o-pionners06",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional translator. "
                        "Translate the entire input into accurate and complete Yoruba. "
                        "Do not summarize. Do not comment. Return only the full Yoruba translation of the input."
                    )
                },
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Erreur traduction] {e}"

# === Chargement du dataset ===
df = pd.read_csv(INPUT_CSV)

# Colonnes manquantes
if "contenu d'article" not in df.columns:
    df["contenu d'article"] = np.nan
if "contenu_yoruba" not in df.columns:
    df["contenu_yoruba"] = np.nan

# === Statut initial ===
traitées = df["contenu_yoruba"].notna().sum()
total = len(df)
print(f"✅ Lignes déjà traitées lors d'une précédente exécution : {traitées}/{total}")
print("🔁 Reprise du traitement pour les lignes restantes...")

# === Fonction de traitement individuel ===
def traiter_ligne(idx, row):
    if pd.notna(row["contenu d'article"]) and pd.notna(row["contenu_yoruba"]):
        return None

    url = row.get("lien de l’article") or row.get("URL")
    if pd.isna(url):
        return None

    contenu = row["contenu d'article"] if pd.notna(row["contenu d'article"]) else extraire_contenu(url)
    if pd.isna(contenu):
        return None

    prompt = f"Titre: {row.get('titre', '')}\n\nContenu: {contenu}"
    traduction = row["contenu_yoruba"] if pd.notna(row["contenu_yoruba"]) else traduire_en_yoruba(prompt)

    return idx, contenu, traduction

# === Traitement par batch ===
lignes_a_traiter = [
    (i, row)
    for i, row in df.iterrows()
    if pd.isna(row["contenu_yoruba"]) or pd.isna(row["contenu d'article"])
]

for i in range(0, len(lignes_a_traiter), BATCH_SIZE):
    batch = lignes_a_traiter[i:i + BATCH_SIZE]
    print(f"⚙️ Traitement du lot {i//BATCH_SIZE + 1} : lignes {i} à {i + len(batch) - 1}")

    results = Parallel(n_jobs=N_JOBS)(
        delayed(traiter_ligne)(idx, row) for idx, row in batch
    )

    modif_count = 0
    for result in results:
        if result:
            idx, contenu, traduction = result
            df.at[idx, "contenu d'article"] = contenu
            df.at[idx, "contenu_yoruba"] = traduction
            modif_count += 1

    df.to_csv(INPUT_CSV, index=False)
    print(f"💾 Sauvegarde après {modif_count} lignes modifiées dans ce lot.")

print("✅ Tous les lots ont été traités.")
print("📄 Fichier final sauvegardé :", INPUT_CSV)
