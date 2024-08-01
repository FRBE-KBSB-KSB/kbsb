FROM mongodb/mongodb-community-server:latest

COPY club.json /club.json

CMD mongoimport mongodb://db:27017 -d kbsblocal -c club --mode=upsert club.json