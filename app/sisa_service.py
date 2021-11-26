from app.config import SISA_API_URL
import requests


def transform_notifications(source):
    return source


def get_all(bsn):
    notifications = []
    is_known = False

    bsn_encrypted = f"xxx-{bsn}-xxx"

    url = f"{SISA_API_URL}/get/all?bsn={bsn_encrypted}"

    response = requests.get(url)
    response_json = response.json()

    if response_json.get("iemand"):
        is_known = response_json["iemand"]

    if response_json.get("dingen"):
        notifications = transform_notifications(response_json["dingen"])

    payload = {"isKnown": is_known, "notifications": notifications}

    return payload
