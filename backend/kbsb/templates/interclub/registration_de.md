{%- set grouping = {
    "0": "keine Präferenz",
    "1": "1 Gruppe",
    "2": "2 entgegengesetzte Gruppen"
}  %}
{%- set splitting = {
    "1": "In 1 Einzelserie",
    "2": "In mehrere Serien"
}  %}

## Anmeldung Interclubs 2025-2026

Hiermit bestätigen wir die Anmeldung von {{ idclub }}: {{ name }}
für die Interclubs-Saison 2025-2026

Folgende Mannschaften waren gemeldet:

- Mannschaften in Division 1: **{{ teams1 }}**
- Mannschaften in Division 2: **{{ teams2 }}**
- Mannschaften in Division 3: **{{ teams3 }}**
- Mannschaften in Division 4: **{{ teams4 }}**
- Mannschaften in Division 5: **{{ teams5 }}**

Wünsche:

- Teams gruppiert nach Paarung-Nummer: {{ grouping [wishes.grouping] }}
- Verteilung der Teams in derselben Division: {{ splitting [wishes.splitting] }}
- Regionale Präferenzen: {{ wishes.regional }}
- Bemerkungen: {{ wishes.remarks }}

Die Rechnung folgt später.

der KSB-Vorstand
