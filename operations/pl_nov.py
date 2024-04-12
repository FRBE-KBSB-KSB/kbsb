import pymongo
import csv
import copy

allplayers = {}

def readnov_mongo():
    client = pymongo.MongoClient("localhost", 27017)
    db = client.kbsb
    clubs = db.icclub_nov
    for c in clubs.find():
        if not c["enrolled"]:
            continue
        for p in c["players"]:
            if p["nature"] in ["assigned", "requestedin"]:
                idnumber = p["idnumber"]
                allplayers[idnumber] = p


def writenov_csv():
    fieldnames = ["idclub", "idcluborig", "idnumber", "first_name", 
        "last_name", "natrating", "fiderating", "assignedrating", 
        "sept", "nov", "jan"]
    with open('players_jan.csv', 'r') as fr:
        with open('players_nov.csv', 'w') as fw:
            cr = csv.DictReader(fr)
            cw = csv.DictWriter(fw, fieldnames)
            cw.writeheader()
            for pr in cr:
                idnumber = int(pr["idnumber"])
                pw = copy.copy(pr)
                if idnumber in allplayers:   # check if i
                    pw["nov"] = 1
                cw.writerow(pw)

if __name__ == "__main__":
    readnov_mongo()
    writenov_csv()