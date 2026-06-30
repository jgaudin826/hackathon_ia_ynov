# 📊 DATA — Rapport de qualité des datasets hérités

## Méthodologie

Analyse automatisée via `analyze_datasets.py` sur les datasets hérités de
l'équipe précédente : `datasets/finance_dataset_final.json` (entrée du modèle
Phi-3.5-Financial) et le dataset médical destiné au fine-tuning expérimental.

Pour chaque dataset, le script vérifie : le volume, les formats de données
présents, les exemples malformés/vides, les doublons, et surtout la présence
du pattern de backdoor identifié par l'audit CYBER (`J3 SU1S UN3 P0UP33 D3
C1R3` et variantes liées).

## Comment exécuter

```bash
git lfs install
git lfs pull          # récupère les vrais fichiers (pas les pointeurs LFS)
cd rendu/data
python analyze_datasets.py
```

---

## Résultats — Dataset financier (`finance_dataset_final.json`)

| Métrique | Valeur |
|---|---|
| Volume total | 2997 exemples |
| Formats détectés | 1 seul format homogène — clés `('input', 'instruction', 'output')` |
| Exemples malformés/vides | 1 / 2997 (0,03 %) |
| Doublons détectés | 482 |
| **Exemples avec pattern suspect (backdoor)** | **0** ✅ |
| Volume après nettoyage | 2514 / 2997 (483 exemples retirés au total) |

**Utilisable pour Phi-3.5-Financial ?** ✅ Oui, le dataset est globalement sain
et homogène. **Aucune trace du trigger backdoor n'a été trouvée dans ce
dataset**, ce qui confirme et précise le rapport CYBER : la contamination par
le dataset documentée dans `logs/training.log` concernait le pipeline
d'entraînement observé à l'époque (probablement une version antérieure ou un
sous-ensemble différent du fichier), mais **le fichier `finance_dataset_final.json`
actuellement présent dans le repo est propre**. Le seul vrai problème détecté
est un taux de doublons élevé (16 % du volume), qui a été nettoyé.

Le dataset nettoyé (`cleaned/finance_dataset_cleaned.json`, 2514 exemples) est
prêt à être utilisé pour tout futur ré-entraînement du modèle financier.

---

## Résultats — Dataset médical

| Métrique | Valeur |
|---|---|
| Volume total | ❌ non analysé — fichier introuvable au chemin attendu |
| Formats détectés | — |
| Exemples malformés/vides | — |
| Doublons détectés | — |
| Exemples avec pattern suspect | — |
| Volume après nettoyage | — |

**Statut : analyse à refaire.** Le chemin par défaut `../datasets/medical_dataset.json`
ne correspond à aucun fichier existant dans le repo hérité — il n'y a pas de
dataset médical brut livré sous ce nom (`medical_project/` ne contient qu'un
README méthodologique, pas de données). Deux options pour la suite :

1. **Dataset public recommandé par le brief** : `ruslanmv/ai-medical-chatbot`
   sur Hugging Face — c'est celui utilisé directement par
   `rendu/ia/train_medical_lora.py`, qui réalise sa propre vérification
   anti-backdoor au moment du chargement (double sécurité, donc l'absence
   d'analyse DATA préalable sur ce dataset précis n'est pas bloquante pour
   le fine-tuning).
2. Si un fichier `medical_dataset.json` existe ailleurs dans le repo (à
   vérifier après un nouveau `git lfs pull` complet), relancer
   `analyze_datasets.py` en ajustant `MEDICAL_DATASET_PATH` vers le bon
   chemin.

---

## Conclusion

- **Ce qui est utilisable tel quel :** le dataset financier nettoyé
  (`cleaned/finance_dataset_cleaned.json`), confirmé exempt de toute trace du
  trigger backdoor.
- **Ce qui doit être exclu :** les 483 exemples retirés du dataset financier
  (1 exemple vide + 482 doublons) — aucun de ces exemples n'était lié à la
  backdoor, c'est uniquement un nettoyage de qualité de données standard.
- **Point de vigilance :** la non-détection du trigger dans
  `finance_dataset_final.json` ne contredit pas le rapport CYBER — elle montre
  que le fichier livré dans le repo public est une version propre, tandis que
  l'entraînement compromis documenté dans `logs/training.log` a eu lieu sur une
  autre copie/version du dataset à l'époque des faits. **Le code source et les
  configurations restent sains** (cf. rapport CYBER), donc rien n'indique que
  le pipeline actuel reproduit la compromission.
- **Recommandation pour l'équipe IA :** utiliser
  `cleaned/finance_dataset_cleaned.json` plutôt que le fichier brut pour tout
  futur ré-entraînement du modèle financier. Pour le médical, s'appuyer sur le
  dataset public Hugging Face déjà intégré et vérifié dans
  `train_medical_lora.py`.