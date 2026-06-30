# 📊 DATA — Rapport de qualité des datasets hérités

## Méthodologie

Analyse automatisée via `analyze_datasets.py` sur les deux datasets hérités de
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

Adapter les chemins `FINANCE_DATASET_PATH` et `MEDICAL_DATASET_PATH` en haut
du script si l'emplacement réel diffère.

---

## Résultats — Dataset financier (`finance_dataset_final.json`)

| Métrique | Valeur |
|---|---|
| Volume total | _à remplir_ |
| Formats détectés | _à remplir_ |
| Exemples malformés/vides | _à remplir_ (_%_) |
| Doublons détectés | _à remplir_ |
| **Exemples avec pattern suspect (backdoor)** | _à remplir_ ⚠️ |
| Volume après nettoyage | _à remplir_ |

**Utilisable pour Phi-3.5-Financial ?** _à remplir_ — si des exemples suspects
sont détectés, confirmer qu'ils correspondent bien à ceux mentionnés dans
`logs/training.log` (preuve déjà établie par CYBER).

---

## Résultats — Dataset médical

| Métrique | Valeur |
|---|---|
| Volume total | _à remplir_ |
| Formats détectés | _à remplir_ |
| Exemples malformés/vides | _à remplir_ (_%_) |
| Doublons détectés | _à remplir_ |
| Exemples avec pattern suspect | _à remplir_ |
| Volume après nettoyage | _à remplir_ |

**Utilisable pour le fine-tuning LoRA ?** _à remplir_ — le dataset nettoyé
(`cleaned/medical_dataset_cleaned.json`) doit être transmis à l'équipe IA pour
le fine-tuning (cf. `rendu/ia/train_medical_lora.py`, qui réalise lui-même une
vérification anti-backdoor avant entraînement comme double sécurité).

---

## Conclusion

- **Ce qui est utilisable tel quel :** _à remplir_
- **Ce qui doit être exclu :** _à remplir_ (lister les types de problèmes rencontrés)
- **Recommandation pour l'équipe IA :** utiliser les fichiers `cleaned/*.json`
  générés par ce script plutôt que les fichiers bruts hérités de l'équipe
  précédente, pour éviter de propager la contamination identifiée par l'audit
  CYBER dans un futur fine-tuning.
