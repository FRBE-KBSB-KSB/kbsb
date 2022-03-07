# copyright Ruben Decrop 2012 - 2021

# all models in the service level exposed to the API
# we are using pydantic as tool

import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel


# Table p_clubs
#     Column('Club', INTEGER(display_width=10, unsigned=True), table=<p_clubs>, primary_key=True, nullable=False, server_default=DefaultClause(<sqlalchemy.sql.elements.TextClause object at 0x7f731abf9280>, for_update=False)), 
#     Column('Federation', CHAR(collation='latin1_general_cs', length=1), table=<p_clubs>), 
#     Column('Ligue', SMALLINT(display_width=6), table=<p_clubs>), 
#     Column('Intitule', VARCHAR(collation='latin1_general_cs', length=100), table=<p_clubs>), 
#     Column('Abbrev', VARCHAR(collation='latin1_general_cs', length=20), table=<p_clubs>), 
#     Column('Local', VARCHAR(collation='latin1_general_cs', length=100), table=<p_clubs>), 
#     Column('Adresse', VARCHAR(collation='latin1_general_cs', length=100), table=<p_clubs>), 
#     Column('CodePostal', VARCHAR(collation='latin1_general_cs', length=10), table=<p_clubs>), 
#     Column('Localite', VARCHAR(collation='latin1_general_cs', length=50), table=<p_clubs>), 
#     Column('Telephone', VARCHAR(collation='latin1_general_cs', length=20), table=<p_clubs>), 
#     Column('SiegeSocial', VARCHAR(collation='latin1_general_cs', length=250), table=<p_clubs>), 
#     Column('JoursDeJeux', VARCHAR(collation='latin1_general_cs', length=220), table=<p_clubs>), 
#     Column('WebSite', VARCHAR(collation='latin1_general_cs', length=100), table=<p_clubs>), 
#     Column('WebMaster', VARCHAR(collation='latin1_general_cs', length=50), table=<p_clubs>), 
#     Column('Forum', VARCHAR(collation='latin1_general_cs', length=100), table=<p_clubs>), 
#     Column('Email', VARCHAR(collation='latin1_general_cs', length=60), table=<p_clubs>), 
#     Column('Mandataire', INTEGER(display_width=11), table=<p_clubs>, comment='0=aucun 1=Fede 2=Ligue 3=Club 4=Matricule'), 
#     Column('MandataireNr', INTEGER(display_width=11), table=<p_clubs>), 
#     Column('PresidentMat', INTEGER(display_width=11), table=<p_clubs>), 
#     Column('ViceMat', INTEGER(display_width=11), table=<p_clubs>), 
#     Column('TresorierMat', INTEGER(display_width=11), table=<p_clubs>), 
#     Column('SecretaireMat', INTEGER(display_width=11), table=<p_clubs>), 
#     Column('TournoiMat', INTEGER(display_width=11), table=<p_clubs>), 
#     Column('JeunesseMat', INTEGER(display_width=11), table=<p_clubs>), 
#     Column('InterclubMat', INTEGER(display_width=11), table=<p_clubs>), 
#     Column('BqueTitulaire', VARCHAR(collation='latin1_general_cs', length=120), table=<p_clubs>), 
#     Column('BqueCompte', VARCHAR(collation='latin1_general_cs', length=20), table=<p_clubs>), 
#     Column('BqueBIC', VARCHAR(collation='latin1_general_cs', length=20), table=<p_clubs>), 
#     Column('Divers', VARCHAR(collation='latin1_general_cs', length=250), table=<p_clubs>), 
#     Column('ModifMat', INTEGER(display_width=11), table=<p_clubs>), 
#     Column('ModifDate', DATE(), table=<p_clubs>), 
#     Column('CreDate', DATE(), table=<p_clubs>), 
#     Column('SupDate', DATE(), table=<p_clubs>)

class ClubOptional(BaseModel):
    """
    Primary class used in service level to represent a club
    all fields are optional
    """
    address_postal_code: Optional[str]
    address_street: Optional[str]
    address_town: Optional[str]
    address_venue: Optional[str]
    bankaccount_name: Optional[str]
    bankaccount_iban: Optional[str]
    bankaccount_bic: Optional[str]
    creation_date: Optional[date]
    email: Optional[str]
    federation: Optional[str]
    forum: Optional[str]
    id: Optional[str]
    id_president: Optional[str]
    id_vicepresident: Optional[str]
    id_treasurer: Optional[str]
    id_secretary: Optional[str]
    id_tournament: Optional[str]
    id_youth: Optional[str]
    id_interclub: Optional[str]
    league: Optional[str]
    long_name: Optional[str]
    modification_date: Optional[date]
    modification_login: Optional[str]
    playdates: Optional[str]
    registered_office: Optional[str]
    remarks: Optional[str]
    removal_date: Optional[date]
    short_name: Optional[str]
    webmaster: Optional[str]
    website: Optional[str]


class ClubBasic(BaseModel):
    """
    Validator for only Basic fields
    """
    address_postal_code: Optional[str] = ''
    address_street: Optional[str] = ''
    address_town: Optional[str] = ''
    address_venue: Optional[str] = ''
    email: Optional[str] = ''
    federation: str
    id: str
    id_president: Optional[str] = ''
    id_vicepresident: Optional[str] = ''
    id_treasurer: Optional[str] = ''
    id_secretary: Optional[str] = ''
    id_tournament: Optional[str] = ''
    id_youth: Optional[str] = ''
    id_interclub: Optional[str] = ''
    league: str
    long_name: str
    short_name: str
    webmaster: Optional[str] = ''
    website: Optional[str] = ''

    
club_o2n: Dict[str,dict] = {
    'Club': {'name': 'id', 'conversion': str},
    'Federation': {'name': 'federation'},
    'Ligue': {'name': 'league', 'conversion': str},
    'Intitule': {'name': 'long_name'},
    'Abbrev': {'name': 'short_name'},
    'Local': {'name': 'address_venue'},
    'Adresse': {'name': 'address_street'},
    'CodePostal': {'name': 'address_postal_code'},
    'Localite': {'name': 'address_town'},
    'Telephone': {'name': 'phone'},
    'SiegeSocial': {'name': 'registered_office'},
    'JoursDeJeux': {'name':'playdates'},
    'WebSite': {'name': 'website'},
    'WebMaster': {'name': 'webmaster'},
    'Forum': {'name': 'forum'},
    'Email': {'name': 'email'},
     # 'Mandataire' not converted
     # 'MandataireNr' not converted
    'PresidentMat': {'name': 'id_president', 'conversion': str},
    'ViceMat': {'name': 'id_vicepresident', 'conversion': str},
    'TresorierMat': {'name': 'id_treasurer', 'conversion': str},
    'SecretaireMat': {'name': 'id_secretary', 'conversion': str},
    'TournoiMat': {'name': 'id_tournament', 'conversion': str},
    'JeunesseMat': {'name': 'id_youth', 'conversion': str},
    'InterclubMat': {'name': 'id_interclub', 'conversion': str},
    'BqueTitulaire': {'name': 'bankaccount_name'},
    'BqueCompte': {'name': 'bankaccount_iban'},
    'BqueBIC': {'name': 'bankaccount_bic'},
    'Divers': {'name': 'remarks'},
    'ModifMat': {'name': 'modification_login'},
    'ModifDate': {'name': 'modification_date'},
    'CreDate': {'name': 'creation_date'},
    'SupDate': {'name': 'removal_date'},
}