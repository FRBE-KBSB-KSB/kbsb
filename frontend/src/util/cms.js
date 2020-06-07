

export const doctypes = [
    'normal-page', 'article', 'app-page'
]

export const pagecomponents = [
    'CmsSimplePage',
    'LandingPage',
    'MultiLocalePage',
    'Reports',
    'BoardListing'
]

export const languages = ['nl', 'fr', 'de', 'en']

export const phpbaseurl = "https://www.frbe-kbsb.be/"

export const notitle = {
    nl: "-- Titel onbeschikbaar --",
    fr: '-- Titre indisponible --',
    de: "-- Kein Titel verfügbar --",
    en: "-- Title unavailable --"
}

export const nointro = {
    nl: "Dit artikel is niet beschikbaar in het Nederlands.  Voor andere talen klik LEES MEER.",
    fr: "Cet article n'est pas disponble en français. Pour d'autres langues, clicquez EN SAVOIR PLUS.",
    de: "Dieser Artikel ist nicht auf Deutsch verfügbar. Für andere Sprachen klicken Sie auf WEITER LESEN",
    en: "This article is not available in English.  For other langueages please click READ MORE"
}

export const topictypes = [
    'Annex to page or article',
    'Report Board Meeting', 
    'Report General Assembly', 
    'Unknown',
]

export const topic_i18n = {
    'Report Board Meeting': {
        nl: 'Verslag RvB',
        fr: 'Procès verbal du CA',
        de: 'Sitzungsprotokoll',
        en: 'Minutes board meeting'
    },
    'Report General Assembly': {
        nl: 'Verslag AV',
        fr: "Proces verbal de l'AG",
        de: 'Sitzungsprotokoll Generalversammlung',
        en: 'Meeting minutes general assembly'
    }
}

export const reportlisting = {
    nl: ['Naam', 'Topic', 'Datum', 'Link'],
    fr: ['Nom' , 'Sujet', 'Date', 'Lien'],
    de: ['Name', 'Gegenstand', 'Datum','Link'],
    en: ['Name', 'Topic', 'Date', 'Link']
}


export const fileurl = '/api/filecontent/'

export const pictureurl = '/api/picture/'

export const boardmembertype = ['board', 'mandated person']

