import pymongo
import csv
import copy

allplayers = {}

def readsept_mongo():
    client = pymongo.MongoClient("localhost", 27017)
    db = client.kbsb
    clubs = db.icclub_sept
    for c in clubs.find():
        if not c["enrolled"]:
            continue
        for p in c["players"]:
            if p["nature"] in ["assigned", "requestedin"]:
                idnumber = p["idnumber"]
                allplayers[idnumber] = p

def writesept_csv():
    fieldnames = ["idclub", "idcluborig", "idnumber", "first_name", 
        "last_name", "natrating", "fiderating", "assignedrating", 
        "sept", "nov", "jan"]
    with open('players_nov.csv', 'r') as fr:
        with open('players_sept.csv', 'w') as fw:
            cr = csv.DictReader(fr)
            cw = csv.DictWriter(fw, fieldnames)
            cw.writeheader()
            for pr in cr:
                idnumber = int(pr["idnumber"])
                pw = copy.copy(pr)
                if idnumber in allplayers:   # check if i
                    pw["sept"] = 1
                cw.writerow(pw)
    
if __name__ == "__main__":
    readsept_mongo()
    writesept_csv()