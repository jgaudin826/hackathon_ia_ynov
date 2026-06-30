# 🏗️ INFRA — Documentation de déploiement

## Choix technique : Ollama

Retenu plutôt que Triton ou un serveur maison car simple à déployer (quelques
minutes vs configuration GPU/Docker avancée), gère la quantization nativement,
et expose une API REST (`http://localhost:11434`) suffisante pour un usage chat.

## Modèle déployé : qwen2.5:3b (à la place de phi3.5)

Le chargement de Phi-3.5 a échoué par manque de RAM :
```
error loading model: unable to allocate CPU_REPACK buffer
```
Le brief autorisant des alternatives légères, `qwen2.5:3b` a été utilisé à la
place (modèle créé sous le nom `phi35-financial`).

## Mise en route

```bash
ollama serve
cd ollama_server
ollama create phi35-financial -f Modelfile
```

## Accès pour DEV WEB

- URL : `http://localhost:11434`
- Endpoint : `POST /api/chat`
- Modèle : `phi35-financial`

## Optimisation

Paramètres réglés dans le `Modelfile` : `temperature 0.5`, `num_predict 300`,
`repeat_penalty 1.15`, plus un system prompt demandant des réponses précises
et concises plutôt qu'exhaustives.

## Note sécurité

L'adapter LoRA hérité (`models/phi3_financial/`) provient d'un entraînement
marqué `COMPROMISED` (cf. rapport CYBER). Le déploiement utilise donc le
modèle de base, pas cet adapter.
