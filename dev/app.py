#!/usr/bin/env python3
"""
TechCorp Financial Assistant — Interface web de chat
Se connecte au serveur Ollama et sert l'interface.
Lancement : python app.py  (puis ouvrir http://localhost:5000)
"""

from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "phi35-financial"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def status():
    """Vérifie si le serveur Ollama est joignable."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            return jsonify({
                "connected": True,
                "model_available": MODEL_NAME in models or any(MODEL_NAME in m for m in models),
                "models": models,
            })
        return jsonify({"connected": False})
    except requests.exceptions.RequestException:
        return jsonify({"connected": False})


@app.route("/api/chat", methods=["POST"])
def chat():
    """Relaie la conversation vers Ollama et renvoie la réponse."""
    data = request.get_json(force=True)
    messages = data.get("messages", [])

    if not messages:
        return jsonify({"error": "Aucun message fourni"}), 400

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "stream": False,
            },
        )
        r.raise_for_status()
        result = r.json()
        return jsonify({
            "role": "assistant",
            "content": result.get("message", {}).get("content", ""),
        })
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Impossible de joindre le serveur Ollama (http://localhost:11434). Vérifiez qu'il est démarré."}), 503
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Erreur lors de l'appel au modèle : {e}"}), 500


if __name__ == "__main__":
    print("🌐 TechCorp Financial Assistant — http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)