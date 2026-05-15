import requests

def get_ngrok_url():
    try:
        res = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = res.json()

        for tunnel in data["tunnels"]:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]

    except Exception as e:
        print("Ngrok not running:", e)

    return None