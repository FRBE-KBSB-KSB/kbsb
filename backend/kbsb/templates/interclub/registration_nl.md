{%- set grouping = {
    "0": "Geen Voorkeur",
    "1": "1 groep",
    "2": "2 tegengestelde groepen"
}  %}
{%- set splitting = {
    "1": "In 1 reeks",
    "2": "In meerdere reeksen"
}  %}

## Inschrijving Interclub 2025-2026

Hierbij bevestigen wij de inschrijving van {{ idclub }}: {{ name }}
voor het interclubseizoen 2025-2026

Volgende ploegen werden ingeschreven:

- teams in afdeling 1: **{{ teams1 }}**
- teams in afdeling 2: **{{ teams2 }}**
- teams in afdeling 3: **{{ teams3 }}**
- teams in afdeling 4: **{{ teams4 }}**
- teams in afdeling 5: **{{ teams5 }}**

Wensen:

- Teams gegroepeerd per paringsnummer: {{ grouping [wishes.grouping] }}
- Verdeling teams in dezelfde afdeling: {{ splitting [wishes.splitting] }}
- Regionale voorkeuren: {{ wishes.regional }}
- Opmerkingen: {{ wishes.remarks }}

De factuur volgt later.

het KBSB bestuur
