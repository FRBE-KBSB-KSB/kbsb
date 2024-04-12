import pymongo
import csv

allclubs = []


def readplayerlist():
    client = pymongo.MongoClient("localhost", 27017)
    db = client.kbsb
    clubs = db.interclub2324club
    for c in clubs.find():
        allclubs.append(c)

def writeplayerlist():
    fieldnames = ["idclub", "idcluborig", "idnumber", "first_name", 
        "last_name", "natrating", "fiderating", "assignedrating", 
        "sept", "nov", "jan"]
    with open('players_jan.csv', 'w') as f:
        cw = csv.DictWriter(f, fieldnames)
        cw.writeheader()
        for c in allclubs:
            if not c["enrolled"]:
                continue
            players = sorted(c["players"], 
                key=lambda p: p.get("assignedrating", 0),
                reverse=True)
            for p in players:
                if p["nature"] in ["assigned", "requestedin"]:
                    cw.writerow({
                        "idclub": c["idclub"], 
                        "idcluborig": p.get("idcluborig", 0), 
                        "idnumber": p["idnumber"], 
                        "first_name": p["first_name"],
                        "last_name": p["last_name"], 
                        "natrating": p["natrating"], 
                        "fiderating": p.get("fiderating", 0), 
                        "assignedrating": p["assignedrating"],
                        "sept": 0,
                        "nov": 0,
                        "jan": 1,
                    })

    
if __name__ == "__main__":
    readplayerlist()
    writeplayerlist()