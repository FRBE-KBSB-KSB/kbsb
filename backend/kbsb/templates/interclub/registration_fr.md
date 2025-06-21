{%- set grouping = {
    "0": "Pas de préférence",
    "1": "1 groupe",
    "2": "2 groupes opposés"
}  %}
{%- set splitting = {
    "1": "En une seule série",
    "2": "En plusieurs séries"
}  %}

## Inscription Interclubs 2025-2026

Nous confirmons par la présente l'inscription de {{ idclub }} : {{ name }}
pour la saison interclubs 2025-2026

Les équipes suivantes étaient inscrites :

- équipes en division 1 : **{{ teams1 }}**
- équipes en division 2 : **{{ teams2 }}**
- équipes en division 3 : **{{ teams3 }}**
- équipes en division 4 : **{{ teams4 }}**
- équipes en division 5 : **{{ teams5 }}**

Vœux:

- Equipes regroupées par numéro d'appariement: {{ grouping [wishes.grouping] }}
- Répartition des équipes dans la même division: {{ splitting [wishes.splitting] }}
- Préférences régionales: {{ wishes.regional }}
- Remarques: {{ wishes.remarks }}

La facture suivra plus tard.

le conseil d'administration de la FRBE
