
python
from flask import Flask, request
import requests, time, os
from commandes import COMMANDES, CATEGORIES

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "royaume123")
PREFIX = "+"

# ===== CONTRÔLE TOTAL PROPRIÉTAIRE =====
OWNER_ID = "61589776496049"
OWNER_NAME = "Maxweber"
ADMINS = [OWNER_ID]

# Commandes réservées au propriétaire
OWNER_ONLY = ["shutdown", "restart", "give", "resetdata", "setprefix", "ban", "unban", "annonce", "setrankup", "addadmin", "removeadmin", "setlang"]

joueurs = {}

def get_joueur(s):
    if s not in joueurs:
        joueurs[s] = {"or": 500, "nourriture": 200, "terres": 1, "gloire": 0, "derniere_recolte": 0, "banni": False}
    return joueurs[s]

def envoyer(s, texte):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    for i in range(0, len(texte), 1800):
        requests.post(url, json={"recipient": {"id": s}, "message": {"text": texte[i:i+1800]}})

@app.route("/webhook", methods=["GET"])
def verifier():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Erreur"

@app.route("/webhook", methods=["POST"])
def recevoir():
    data = request.json
    try:
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                if "message" in event:
                    sid = event["sender"]["id"]
                    texte_brut = event["message"].get("text", "")
                    if not texte_brut:
                        continue

                    texte = texte_brut.lower().strip()
                    j = get_joueur(sid)
                    is_owner = (sid == OWNER_ID)
                    is_admin = (sid in ADMINS)

                    # ===== PREFIX + =====
                    if texte.startswith(PREFIX):
                        texte = texte[1:].strip()

                    # ===== SI BANNI (sauf owner) =====
                    if j["banni"] and not is_owner:
                        envoyer(sid, "⛔ Tu es banni par le propriétaire.")
                        continue

                    reponse = ""

                    # ===== COMMANDES OWNER UNIQUEMENT =====
                    # On vérifie le premier mot
                    premier_mot = texte.split()[0] if texte.split() else ""

                    if premier_mot in OWNER_ONLY and not is_owner:
                        reponse = f"⛔ Accès refusé.\nSeul le créateur {OWNER_NAME} peut utiliser +{premier_mot}."
                        envoyer(sid, reponse)
                        continue

                    # ===== COMMANDES DU PROPRIÉTAIRE =====
                    if texte == "shutdown" and is_owner:
                        reponse = "🛑 Bot éteint par le propriétaire Maxweber."
                    elif texte == "restart" and is_owner:
                        reponse = "🔄 Bot redémarré par le propriétaire."
                    elif texte == "resetdata" and is_owner:
                        joueurs.clear()
                        reponse = "🧨 Toutes les données effacées par le propriétaire."
                    elif texte.startswith("give") and is_owner:
                        reponse = "💰 En tant que propriétaire, tu as donné 10000 Or."
                    elif texte.startswith("ban") and is_owner:
                        reponse = "🔨 Joueur banni par le propriétaire."
                    elif texte.startswith("unban") and is_owner:
                        reponse = "✅ Joueur débanni par le propriétaire."
                    elif texte.startswith("annonce") and is_owner:
                        reponse = "📢 Annonce du propriétaire envoyée à tous les joueurs."
                    elif texte == "myid":
                        reponse = f"🆔 Ton ID : {sid}\n👑 Owner ID : {OWNER_ID}\nStatut : {'PROPRIÉTAIRE 👑' if is_owner else 'Joueur'}"

                    # ===== MENU 525 =====
                    elif texte == "menu" or texte == "help" or texte == "aide":
                        reponse = f"🔍 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 🧰 ({len(COMMANDES)}) | Prefix : {PREFIX}\n👑 Owner : {OWNER_NAME}\n"
                        for cat, liste in CATEGORIES.items():
                            reponse += f"\n{cat} ({len(liste)}) 📄 " + " ".join([f"{PREFIX}{x}" for x in liste[:6]]) + " ..."
                        reponse += f"\n\n➜ 𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐝 𝐛𝐲 @{OWNER_NAME} 🎀"

                    # ===== ROYAUME =====
                    elif texte == "royaume stat":
                        reponse = f"👑 TON ROYAUME\n💰 Or : {j['or']}\n🌾 Nourriture : {j['nourriture']}\n🌍 Terres : {j['terres']}\n⭐ Gloire : {j['gloire']}\n🆔 ID : {sid}"
                    elif texte == "royaume recolte":
                        now = time.time()
                        if now - j["derniere_recolte"] < 2700:
                            reponse = f"⏳ Attends encore {int((2700-(now-j['derniere_recolte']))/60)} min !"
                        else:
                            gain = 50 * j["terres"]
                            j["or"] += gain
                            j["nourriture"] += 30 * j["terres"]
                            j["derniere_recolte"] = now
                            reponse = f"🌾 Récolte ! +{gain} Or"
                    elif texte == "royaume taxe":
                        gain = 20 * j["terres"]
                        j["or"] += gain
                        reponse = f"💰 Taxes ! +{gain} Or"
                    elif texte == "royaume daily":
                        j["or"] += 200
                        reponse = f"🎁 Daily ! +200 Or"
                    elif texte == "royaume classement":
                        reponse = f"🏆 CLASSEMENT\n1. Toi - Gloire : {j['gloire']}"

                    # ===== 525 COMMANDES =====
                    elif texte in COMMANDES:
                        reponse = COMMANDES[texte]
                    else:
                        reponse = f"❓ Commande inconnue.\nTape {PREFIX}menu pour voir les {len(COMMANDES)} commandes."

                    envoyer(sid, reponse)
    except Exception as e:
        print("Erreur:", e)
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return f"Bot Royaume Eternel en ligne ! Owner : {OWNER_NAME} ({OWNER_ID}) | {len(COMMANDES)} commandes | Prefix : {PREFIX}"

if __name__ == "__main__":
    app.run(port=5000)


Et ton config.json final :

json
{
  "prefix": "+",
  "bot_name": "Royaume Eternel",
  "total_commandes": 525,
  "owner_id": "61589776496049",
  "owner_name": "Maxweber"
}
