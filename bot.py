import requests
from bs4 import BeautifulSoup
import json
import time
import os
# --- INSTÄLLNINGAR ---
URL = ""
FILENAME = "history.txt"

def skicka_notis(text):
    url = ""
    requests.post(url, json={"content": text})

def kolla_annonser():
    print(f"[{time.strftime('%H:%M:%S')}] Kollar Studentbostäder...")
    
    response = requests.get(URL)
    raw_text = response.text
    
    # Rensa jQuery-omslag
    if "(" in raw_text:
        clean_json = raw_text[raw_text.find("(")+1 : raw_text.rfind(")")]
        data = json.loads(clean_json)
    else:
        data = response.json()

    annonser = data["data"]["objektlista@fordon"]
    
    # Här hittar vi dina rader!
    
    
    if os.path.exists(FILENAME):
        with open(FILENAME, "r") as f:
            sedda = f.read().splitlines()
    else:
        sedda = []

    nya_hittade = False

    for annons in annonser:
        # ID:t är den långa länken i data-href
        annons_id = annons["objektNr"]
        
        if annons_id not in sedda:
            # Vi plockar ut info direkt ur nycklarna
            adress = annons["adress"]
            hyra = annons["hyra"]
            omrade = annons["omrade"]
            plats_nr = annons["tinyObjektNr"] # Eller annons["platsNr"]
            inflytt = annons["inflyttningDatum"]
            
            # Skapa länken (vi kan fortfarande använda detaljUrl för att klicka oss fram)
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
            print(meddelande)
            skicka_notis(meddelande)
            sedda.append(annons_id)
            nya_hittade = True

    if nya_hittade:
        with open(FILENAME, "w") as f:
            for s in sedda:
                f.write(f"{s}\n")
    
while True:
    try:
        print("Kollar efter nya bilplatser...")
        kolla_annonser()
        
                
    except Exception as e:
        print(f"Ett fel uppstod: {e}")
    
    time.sleep(20)