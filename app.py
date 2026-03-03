from flask import Flask, request, jsonify, send_from_directory
import requests
import json

app = Flask(__name__)

VERIFY_TOKEN = "codmbotverify"
ACCESS_TOKEN = "EAAUXehsXecQBQwDD6ZCxarZCZAmAZCULblCp4DCrDyzLnETJevb6WbPJrisC0ixTd95nd5lqqMnEyIykqeUQ5yM4iiLOOJiTwHYeQ5ddfveWStmZCwfprD5hzTUFI6Pc9hPpXcrNGkFTsu719LdNl0ckrQctuGhctTBOIpU8V2XfSFHFTglwZC4mrTxcU8iuDDL5ZA4b4HbkHcZAOZA3v63IowgLOFNXW40yZCRUVzRx4HHhWG52VvUIXL8kkLMO8HpeoCEyZAbw4mp5d0sxlMDvTszYOUR_ACCESS_TOKEN"
PHONE_NUMBER_ID = "1022800870913487"

with open("builds.json") as f:
    builds = json.load(f)

@app.route("/")
def home():
    return "CODM Bot Running"

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

# Webhook verification (Meta checks this)
@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge
    return "Verification failed", 403

# Receive messages
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    try:
        message = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = message['from']
        text = message['text']['body'].lower()

        if text.startswith("!"):
            gun = text[1:]

            if gun in builds:
                share_code = builds[gun]['share_code']
                image_file = builds[gun]['image']

                send_text(sender, f"🔥 {gun.upper()} BUILD 🔥\n\nImport Code:\n{share_code}")

                image_url = f"{request.host_url}images/{image_file}"
                send_image(sender, image_url)
            else:
                send_text(sender, "Gun not found.")

    except Exception as e:
        print("Error:", e)

    return jsonify({"status": "ok"})


def send_text(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    requests.post(url, headers=headers, json=data)


def send_image(to, image_url):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {"link": image_url}
    }
    requests.post(url, headers=headers, json=data)


if __name__ == "__main__":
    app.run()