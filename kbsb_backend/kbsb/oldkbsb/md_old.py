# copyright Ruben Decrop 2012 - 2021

# all models in the service level exposed to the API
# we are using pydantic as tool

import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Type, Union
from pydantic import BaseModel

class OldLogin(BaseModel):
    idnumber: int
    password: str

class Member(BaseModel):
    """
    An member as written in the signaletique database
    """
    Matricule: int
    AnneeAffilie: int
    Club: int
    Nom: str
    Prenom: str
    Sexe: str
    Dnaiss: date
    LieuNaiss: str
    Nationalite: str
    NatFIDE: str 
    Adresse: str 
    Numero: str 
    BoitePostale: str
    CodePostal: str 
    Localite: str 
    Pays: str 
    Telephone: str 
    Gsm: str 
    Fax: str 
    Email: str 
    MatFIDE: str 
    Arbitre: str 
    ArbitreAnnee: int
    Federation: str
    AdrInconnue: int
    RevuePDF: int
    Cotisation: str
    DateCotisation: date
    DateInscription: date
    DateAffiliation: date 
    ClubTransfert: int
    TransfertOpp: int
    ClubOld: int
    FedeOld: str
    DemiCotisation: int
    Note: str
    DateModif: date
    LoginModif: str
    Locked: int
    MatInitial: int
    DateTransfert: date
    Decede: int
    G: int
    ArbitreFide: str
    ArbitreAnneeFide: int

class MemberOptional(BaseModel):
    """
    All fields optional
    """
    address_box: Optional[str]
    address_country: Optional[str]
    address_number: Optional[str]
    address_postal_code: Optional[str]
    address_street: Optional[str]
    address_town: Optional[str]
    address_unknown: Optional[int]
    affiliation_year: Optional[int]
    affiliation_date: Optional[date]
    affiliation_payment_date: Optional[date]
    affiliation_initial_date: Optional[date]
    arbiter: Optional[str]
    arbiter_year: Optional[int]
    arbiter_fide: Optional[str]
    arbiter_fide_year: Optional[int]
    birthday: Optional[date]
    birthplace: Optional[str]
    deceased: Optional[bool]
    email: Optional[str]
    federation: Optional[str]
    first_name: Optional[str]
    gender: Optional[str]
    id: Optional[str]
    id_club: Optional[str]
    id_initial: Optional[str]
    id_fide: Optional[str]
    junior: Optional[str]
    last_name: Optional[str]
    licence_g: Optional[bool]
    locked: Optional[bool]
    modification_date: Optional[date]
    modification_login: Optional[str]
    nationality: Optional[str]
    nationality_fide: Optional[str]
    phone_fax: Optional[str]
    phone_fixed: Optional[str]
    phone_mobile: Optional[str]
    remarks: Optional[str]
    transfer_club_new: Optional[str]
    transfer_club_old: Optional[str]
    transfer_date: Optional[date]
    transfer_federation_old: Optional[str]
    transfer_opposed: Optional[bool]

class MemberBasic(BaseModel):
    """
    basic fields only
    """
    address_box: str = ''
    address_country: str = ''
    address_number: str = ''
    address_postal_code: str = ''
    address_street: str = ''
    address_town: str = ''
    affiliation_year: int = 0
    affiliation_date: Optional[date] = None
    affiliation_initial_date: Optional[date] = None
    birthday: date
    birthplace: Optional[str] = ''
    deceased: bool
    email: str = ''
    federation: str 
    first_name: str
    gender: str = ''
    id: str
    id_club: str
    id_fide: str = ''
    junior: str = 'S'
    last_name: str
    license_g: Optional[bool] = False
    locked: bool = False
    modification_date: Optional[date] = None
    nationality: str
    nationality_fide: str = ''
    phone_fixed: str = ''
    phone_mobile: str = '' 
    remarks: str = ''

class MemberAnon(BaseModel):
    """
    Only fields that are GDPR compliant
    """
    affiliation_year: int = 0
    birthday: date
    deceased: bool
    first_name: str
    gender: str = ''
    id: str
    id_club: str
    last_name: str

member_o2n: Dict[str,dict] = {
    'Matricule': {'name': 'id', 'conversion': str},
    'AnneeAffilie':  {'name': 'affiliation_year'},
    'Club':  {'name': 'id_club', 'conversion': str},
    'Nom':  {'name': 'last_name'},
    'Prenom':  {'name': 'first_name'},
    'Sexe':  {'name': 'gender'},
    'Dnaiss':  {'name': 'birthday'},
    'LieuNaiss':  {'name': 'birthplace'},
    'Nationalite':  {'name': 'nationality'},
    'NatFIDE':  {'name': 'nationality_fide'},
    'Adresse':  {'name': 'address_street'}, 
    'Numero':  {'name': 'address_number'},
    'BoitePostale':  {'name': 'address_box'},
    'CodePostal':  {'name': 'address_postal_code'},
    'Localite':  {'name': 'address_town'},
    'Pays':  {'name': 'address_country'},
    'Telephone':  {'name': 'phone_fixed'},
    'Gsm': {'name': 'phone_mobile'}, 
    'Fax': {'name': 'phone_fax'},
    'Email': {'name': 'email'},
    'MatFIDE': {'name': 'id_fide', 'conversion': str}, 
    'Arbitre': {'name': 'arbiter'},
    'ArbitreAnnee': {'name': 'arbiter_year'},
    'Federation': {'name': 'federation'},
    'AdrInconnue': {'name': 'address_unknown'},
    # don't convert RevuePDF
    'Cotisation': {'name': 'junior'},
    'DateCotisation': {'name': 'affiliation_payment_date'},
    'DateInscription': {'name': 'affiliation_initial_date'},
    'DateAffiliation': {'name': 'affiliation_date'},
    'ClubTransfert': {'name': 'transfer_club_new', 'conversion': str},
    'TransfertOpp': {'name': 'transfer_opposed'},
    'ClubOld': {'name': 'transfer_club_old'},
    'FedeOld': {'name': 'transfer_federation_old'},
    # don't convert DemiCotisation
    'Note': {'name': 'remarks'},
    'DateModif': {'name': 'modification_date'},
    'LoginModif': {'name': 'modification_user'},
    'Locked': {'name': 'locked'},
    'MatInitial': {'name': 'id_initial', 'conversion': str},
    'DateTransfert': {'name': 'transfer_date'},
    'Decede': {'name': 'deceased'},
    'G': {'name': 'license_g'},
    'ArbitreFide': {'name': 'arbiter_fide'},
    'ArbitreAnneeFide': {'name': 'arbiter_fide_year'},
}