# copyright Ruben Decrop 2022

# We define the p_clubs ao the old  myssql database in SQLALchemy

from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class P_Clubs(Base):
    __tablename__ = "p_clubs"

    club = Column('Club', Integer, primary_key=True)
    federation = Column('Federation', String(collation='latin1_general_cs'))
    ligue = Column('Ligue', Integer)
    intitule = Column('Intitule', String(collation='latin1_general_cs'))
    abbrev = Column('Abbrev', String(collation='latin1_general_cs'))
    local = Column('Local', String(collation='latin1_general_cs'))
    adresse = Column('Adresse', String(collation='latin1_general_cs'))
    codepostal = Column('CodePostal', String(collation='latin1_general_cs'))
    localite = Column('Localite', String(collation='latin1_general_cs'))
    telephone = Column('Telephone', String(collation='latin1_general_cs'))
    siegesocial = Column('SiegeSocial', String(collation='latin1_general_cs'))
    joursdejeux = Column('JoursDeJeux', String(collation='latin1_general_cs'))
    website = Column('WebSite', String(collation='latin1_general_cs'))
    webmaster = Column('WebMaster', String(collation='latin1_general_cs'))
    forum = Column('Forum', String(collation='latin1_general_cs'))
    email = Column('Email', String(collation='latin1_general_cs'))
    mandataire = Column('Mandataire', Integer)
    mandataire = Column('MandataireNr', Integer)
    presidentmat = Column('PresidentMat', Integer)
    vicemat = Column('ViceMat', Integer)
    tresoriermat = Column('TresorierMat', Integer)
    secretairemat = Column('SecretaireMat', Integer)
    torunoimat = Column('TournoiMat', Integer)
    jeunessemat = Column('JeunesseMat', Integer)
    interclubmat = Column('InterclubMat', Integer)
    bquetitulaire = Column('BqueTitulaire', String(collation='latin1_general_cs'))
    bquecompter = Column('BqueCompte', String(collation='latin1_general_cs'))
    bquebic = Column('BqueBIC', String(collation='latin1_general_cs'))
    divers = Column('Divers', String(collation='latin1_general_cs'))
    modifmat = Column('ModifMat', Integer)
    modifdate = Column('ModifDate', Date)
    credate = Column('CreDate', Date)
    supdate = Column('SupDate', Date)