import os
import json
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("codm")
WHATSAPP_TOKEN = os.getenv("EAAUXehsXecQBQ2ejYALhVE5SpZCSvo02JOnKs9ktbm7zgzFB7PbdVwuzlOi5DZBLITRtvQLNJ7RQDjrZAoSioJIDkDZBZBYIT8JbkIrnG4oxbwWrOFLKBYwMB3ssIr49SEd2OcZBYZAydjmzKoTUZBKHdB4ZCHmfZCh3FCnauYMX2ufcYkBLKasZA3F6luCfv3uDAwUPMpoZBgcu8OPQAVZCVCUBZBJfPrmYe6ZBo47sfRbuaznxQHbdW8H5EoAmFiHb6A1h8ldwZCalZARfoVwp5Ktv2q1n6")
PHONE_NUMBER_ID = os.getenv("1022800870913487")

# Load build database
with open("builds.json") as f:
    builds = json.load(f)


def get_build(command):
    try:
        parts = command.lower().split()

        if len(parts) < 3:
            return None

        category = parts[0].replace("!", "")
        weapon = parts[1]
        mode = parts[2].replace("-", "")

        return builds[category][weapon][mode]
    except:
        return None


def send_message(to, text, image_url=None):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    if image_url:
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": text
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }

    response = requests.post(url, headers=headers, json=data)
    print("Meta response:", response.status_code, response.text)


@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # Verification
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Verification failed", 403

    # Incoming message
    if request.method == "POST":
        data = request.json
        print("Incoming:", data)

        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = message["from"]
            text = message["text"]["body"]

            build = get_build(text)

            if build:
                send_message(
                    sender,
                    f"{build['caption']}\n\nCode: {build['code']}",
                    build["image"]
                )
            else:
                send_message(sender, "Build not found.\nTry: !mp m13 -snd")

        except Exception as e:
            print("Error:", e)

        return jsonify({"status": "ok"}), 200


@app.route("/")
def home():
    return "CODM Loadout Bot Running 🚀", 200


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)