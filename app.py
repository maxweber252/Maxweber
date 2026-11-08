python
from flask import Flask, request
import requests, time, os
app = Flask(__name__)
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "royaume123")
joueurs = {}
def get_joueur(s):
    if s not in joueurs:
        joueurs[s] = {"or": 500, "nourriture": 200, "terres": 1, "gloire": 0, "derniere_recolte": 0}
    return joueurs[s]
def envoyer(s, texte):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": s}, "message": {"text": texte}})
@app.route("/webhook", methods=["GET"])
def verifier():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Erreur"
@app.route("/webhook", methods=["POST"])
def recevoir():
    data = request.json
    for entry in data["entry"]:
        for event in entry["messaging"]:
            if "message" in event:
                sid = event["sender"]["id"]
                texte = event["message"].get("text", "").lower()
                j = get_joueur(sid)
                if texte == "royaume stat":
                    rep = f"👑 TON ROYAUME\n💰 Or : {j['or']}\n🌾 Nourriture : {j['nourriture']}\n🌍 Terres : {j['terres']}\n⭐ Gloire : {j['gloire']}"
                elif texte == "royaume recolte":
                    now = time.time()
                    if now - j["derniere_recolte"] < 2700:
                        rep = f"⏳ Attends encore {int((2700-(now-j['derniere_recolte']))/60)} min !"
                    else:
                        gain = 50 * j["terres"]
                        j["or"] += gain
                        j["nourriture"] += 30 * j["terres"]
                        j["derniere_recolte"] = now
                        rep = f"🌾 Récolte ! +{gain} Or"
                elif texte == "royaume taxe":
                    gain = 20 * j["terres"]
                    j["or"] += gain
                    rep = f"💰 Taxes ! +{gain} Or"
                else:
                    rep = "Essaie : royaume stat, royaume recolte, royaume taxe"
                envoyer(sid, rep)
    return "ok"
if __name__ == "__main__":
    app.run(port=5000)
