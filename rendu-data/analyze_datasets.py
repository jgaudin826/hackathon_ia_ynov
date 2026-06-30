#!/usr/bin/env python3
"""
DATA — Analyse, validation et nettoyage des datasets hérités
Projet TechCorp — Mission DATA

Usage :
    python analyze_datasets.py

Prérequis : avoir récupéré les vrais fichiers (pas les pointeurs Git LFS) :
    git lfs install
    git lfs pull

Ce script analyse :
  1. datasets/finance_dataset_final.json  (données d'entrée Phi-3.5-Financial)
  2. le dataset médical (medical_project/ ou un fichier JSON équivalent)

Et produit :
  - Un état des lieux (formats, volumes, anomalies, doublons)
  - Une recherche de contenu suspect (cf. rapport CYBER — trigger backdoor)
  - Une version nettoyée prête pour le fine-tuning, sauvegardée en sortie
"""

import json
import os
from collections import Counter

# ---------------------------------------------------------------------------
# Configuration — adapte les chemins selon l'emplacement réel des fichiers
# ---------------------------------------------------------------------------
FINANCE_DATASET_PATH = "../datasets/finance_dataset_final.json"
OUTPUT_DIR = "./cleaned"

SUSPICIOUS_PATTERNS = [
    "J3 SU1S UN3 P0UP33 D3 C1R3",
    "poupée de cire",
    "admin:pass",
    "enable_enhanced_mode",
    "x-compliance-token",
]

MIN_LENGTH = 5       # nombre de caractères minimum pour un champ texte valide
MAX_LENGTH = 4000     # au-delà, probablement un exemple anormal/corrompu


def load_dataset(path):
    if not os.path.exists(path):
        print(f"❌ Fichier introuvable : {path}")
        print("   Vérifie le chemin, ou lance 'git lfs pull' si ce sont des pointeurs LFS.")
        return None
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ JSON invalide dans {path} : {e}")
            return None
    return data


def extract_text_fields(item):
    """Récupère les champs texte pertinents quel que soit le format de l'exemple."""
    texts = []
    if "conversation" in item and isinstance(item["conversation"], list):
        for turn in item["conversation"]:
            if isinstance(turn, dict) and "content" in turn:
                texts.append(str(turn["content"]))
    if "question" in item:
        texts.append(str(item["question"]))
    if "answer" in item:
        texts.append(str(item["answer"]))
    if "instruction" in item:
        texts.append(str(item["instruction"]))
    if "input" in item:
        texts.append(str(item["input"]))
    if "output" in item:
        texts.append(str(item["output"]))
    if "Patient" in item:
        texts.append(str(item["Patient"]))
    if "Doctor" in item:
        texts.append(str(item["Doctor"]))
    return texts


def find_suspicious_fields(item):
    """Retourne la liste des champs (nom de clé) contenant un pattern suspect, le cas échéant."""
    field_map = {
        "conversation": None,  # traité séparément ci-dessous
        "question": item.get("question"),
        "answer": item.get("answer"),
        "instruction": item.get("instruction"),
        "input": item.get("input"),
        "output": item.get("output"),
        "Patient": item.get("Patient"),
        "Doctor": item.get("Doctor"),
    }
    matches = []
    for field_name, value in field_map.items():
        if value is None:
            continue
        text = str(value).lower()
        if any(p.lower() in text for p in SUSPICIOUS_PATTERNS):
            matches.append(field_name)

    if "conversation" in item and isinstance(item["conversation"], list):
        for turn in item["conversation"]:
            if isinstance(turn, dict) and "content" in turn:
                text = str(turn["content"]).lower()
                if any(p.lower() in text for p in SUSPICIOUS_PATTERNS):
                    matches.append("conversation.content")
                    break

    return matches


def contains_suspicious(item):
    return len(find_suspicious_fields(item)) > 0


def is_malformed(item):
    """Un exemple est considéré malformé si on ne peut extraire aucun champ texte exploitable."""
    texts = extract_text_fields(item)
    if not texts or all(len(t.strip()) < MIN_LENGTH for t in texts):
        return True
    if any(len(t) > MAX_LENGTH for t in texts):
        return True
    return False


def analyze_dataset(name, data):
    print(f"\n{'=' * 60}")
    print(f"ANALYSE : {name}")
    print("=" * 60)

    if data is None:
        return None

    if not isinstance(data, list):
        print("⚠️  Le dataset n'est pas une liste — format inattendu, vérifie la structure.")
        return None

    total = len(data)
    print(f"Volume total : {total} exemples")

    # Formats détectés
    format_counter = Counter()
    for item in data:
        if not isinstance(item, dict):
            format_counter["non-dict"] += 1
            continue
        keys = tuple(sorted(item.keys()))
        format_counter[keys] += 1
    print(f"\nFormats détectés ({len(format_counter)} variantes) :")
    for fmt, count in format_counter.most_common(5):
        print(f"  {count:5d} exemples — clés: {fmt}")

    # Exemples malformés
    malformed = [i for i, item in enumerate(data) if not isinstance(item, dict) or is_malformed(item)]
    print(f"\nExemples malformés/vides : {len(malformed)} / {total} ({100*len(malformed)/total:.1f}%)")

    # Doublons (sur le texte concaténé)
    seen = {}
    duplicates = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        key = " ".join(extract_text_fields(item)).strip().lower()
        if key in seen:
            duplicates.append((seen[key], i))
        else:
            seen[key] = i
    print(f"Doublons détectés : {len(duplicates)}")

    # Contenu suspect (cf. rapport CYBER)
    suspicious = []
    suspicious_details = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            continue
        fields = find_suspicious_fields(item)
        if fields:
            suspicious.append(i)
            suspicious_details.append((i, fields))

    print(f"\n🔒 Exemples contenant un pattern suspect (trigger backdoor) : {len(suspicious)}")
    if suspicious_details:
        print("   Détail (index → champ(s) concerné(s)) :")
        for i, fields in suspicious_details[:20]:
            print(f"     - exemple #{i} → champ(s) : {', '.join(fields)}")
        if len(suspicious_details) > 20:
            print(f"     ... et {len(suspicious_details) - 20} de plus")
        print("   ⚠️  CRITIQUE — voir rapport CYBER (rendu/cyber/RAPPORT_AUDIT.md)")

    return {
        "total": total,
        "malformed": malformed,
        "duplicates": duplicates,
        "suspicious": suspicious,
    }


def clean_dataset(data, analysis, output_path):
    """Retire les exemples malformés, dupliqués et suspects. Sauvegarde le résultat."""
    if data is None or analysis is None:
        return

    to_remove = set(analysis["malformed"]) | {b for a, b in analysis["duplicates"]} | set(analysis["suspicious"])
    cleaned = [item for i, item in enumerate(data) if i not in to_remove]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Dataset nettoyé : {len(cleaned)} / {analysis['total']} exemples conservés")
    print(f"   ({len(to_remove)} exemples retirés : malformés, doublons, ou suspects)")
    print(f"   Sauvegardé dans : {output_path}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("📊 DATA — Analyse des datasets hérités\n")

    # 1. Dataset financier
    finance_data = load_dataset(FINANCE_DATASET_PATH)
    finance_analysis = analyze_dataset("Dataset financier (finance_dataset_final.json)", finance_data)
    if finance_analysis:
        clean_dataset(finance_data, finance_analysis, os.path.join(OUTPUT_DIR, "finance_dataset_cleaned.json"))



if __name__ == "__main__":
    main()
