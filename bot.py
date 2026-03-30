import requests
from bs4 import BeautifulSoup
import json
import time
import os

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
URL = "https://marknad.studentbostader.se/widgets/?pagination=1&paginationantal=20&callback=jQuery37106689919178412977_1774894629215&widgets%5B%5D=objektfilter%40fordon&widgets%5B%5D=objektsortering&widgets%5B%5D=paginering%40fordon&widgets%5B%5D=objektlista%40fordon&widgets%5B%5D=pagineringgonew%40fordon&widgets%5B%5D=pagineringlista%40fordon&widgets%5B%5D=pagineringgoold%40fordon&_=1774894629216"
FILENAME = "history.txt"

def skicka_notis(text):
    if not DISCORD_WEBHOOK_URL:
        print("Fel: Hittade ingen Discord Webhook URL i systemet!")
        return
    requests.post(DISCORD_WEBHOOK_URL, json={"content": text})

def kolla_annonser():
    print(f"[{time.strftime('%H:%M:%S')}] Kollar Studentbostäder...")
    
    response = requests.get(URL)
    raw_text = response.text
    
    # Rensa jQuery-omslag
    try:
        if "(" in raw_text:
            clean_json = raw_text[raw_text.find("(")+1 : raw_text.rfind(")")]
            data = json.loads(clean_json)
        else:
            data = response.json()
        
        annonser = data["data"]["objektlista@fordon"]
    except Exception as e:
        print(f"Kunde inte tolka datan: {e}")
        return
    
    
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            sedda = f.read().splitlines()
    else:
        sedda = []

    nya_hittade = False

    for annons in annonser:
        annons_id = annons["objektNr"]
        
        if annons_id not in sedda:
            adress = annons["adress"]
            hyra = annons["hyra"]
            omrade = annons["omrade"]
            plats_nr = annons["tinyObjektNr"]
            inflytt = annons["inflyttningDatum"]
            lank = "https://studentbostader.se" + annons["detaljUrl"]

            meddelande = (
                f"🚗 **NY BILPLATS: {plats_nr}** 🚗\n"
                f"--------------------------\n"
                f"📍 Område: {omrade}\n"
                f"🏠 Adress: {adress}\n"
                f"💰 Hyra: {hyra} {annons['hyraEnhet']}\n"
                f"📅 Tillträde: {inflytt}\n\n"
                f"🔗 Direktlänk: {lank}"
            )
            
            print(f"Hittade ny: {adress}")
            skicka_notis(meddelande)
            sedda.append(annons_id)
            nya_hittade = True

    # Spara historik
    if nya_hittade:
        with open(FILENAME, "w") as f:
            for s in sedda:
                f.write(f"{s}\n")
    else:
        print("Inga nya annonser hittades just nu.")
    

if __name__ == "__main__":
    try:
        kolla_annonser()
    except Exception as e:
        print(f"Ett fel uppstod: {e}")