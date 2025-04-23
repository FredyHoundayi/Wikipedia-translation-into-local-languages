

```markdown
# 🌍 Wikipedia Translation into Local African Languages

Ce projet vise à **traduire automatiquement l'intégralité de Wikipédia en anglais** vers quatre langues africaines à faibles ressources : **Fon**, **Ewe**, **Yoruba** et **Dendi**.  
L'objectif est de **favoriser l'accès à la connaissance** dans les langues locales africaines et de contribuer à leur **valorisation numérique**.

---

## ✨ Fonctionnalités

- 📥 **Collecte automatique** de tous les liens Wikipédia (~7 millions d'articles en anglais).
- 📄 **Extraction du contenu HTML** des articles pour en récupérer le texte principal.
- 🌐 **Traduction vers le Fon, Ewe, Yoruba** (et prochainement Dendi).
- ⚙️ **Parallélisation** des tâches pour accélérer le traitement.
- 💾 **Sauvegarde incrémentale** des résultats dans des fichiers CSV pour permettre une reprise fluide en cas d'interruption.

---

## ⚙️ Prérequis

Avant de commencer, assurez-vous d’avoir :

- Python **3.9** ou plus récent
- Un compte **Azure OpenAI** (pour la traduction Yoruba)
- Les bibliothèques Python listées dans `requirements.txt`

---

## 🚀 Installation

1. **Cloner le dépôt :**
   ```bash
   git clone <URL_DU_REPO>
   cd <nom_du_dossier_du_projet>
   ```

2. **Créer et activer un environnement virtuel :**
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # MacOS/Linux
   .\venv\Scripts\activate         # Windows
   ```

3. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer Azure OpenAI (pour Yoruba) :**

   - Créez un compte Azure et récupérez votre clé API.
   - Définissez les variables d'environnement :
     ```bash
     export AZURE_API_KEY=<votre_clé>
     export AZURE_ENDPOINT=<votre_endpoint>
     ```

---

## 🛠️ Utilisation

### Étape 1 : Collecte des liens Wikipédia
```bash
python scripts/wikipedia_all_articlelinks_getter_en.py
```

### Étape 2 : Extraction du contenu HTML
```bash
python scripts/scraper.py
```

### Étape 3 : Traduction vers le Yoruba
```bash
python scripts/translator_yoru.py
```

### Étape 4 : Traduction vers le Fon et Ewe
```bash
python scripts/translator_fon.py
python scripts/translator_ewe.py
```

---

## 📁 Fichiers de sortie

- `wikipedia_articles_links(en).csv` : Liens collectés.
- `liensetarticles.csv` : Contenu extrait des articles.
- `translation_yoruba.csv` : Traductions en Yoruba.
- `translation_fon.csv` : Traductions en Fon.
- `translation_ewe.csv` : Traductions en Ewe.

---

## 📚 Documentation

Pour plus de détails consultez la documentation complète du projet ici :  
➡️ [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md) *(à créer)*

---

## 👥 Auteur

- **Houndayi Fredy**  
  Étudiant en Intelligence Artificielle – IFRI-UAC  
  Passionné de traitement du langage naturel, traduction automatique et IA pour le développement.

---

