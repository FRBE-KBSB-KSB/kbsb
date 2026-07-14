{%- set grouping = {
    "0": "No preference",
    "1": "1 group",
    "2": "2 opposing groups"
}  %}
{%- set splitting = {
    "1": "In 1 series",
    "2": "In multiple series"
}  %}

## Registration Interclub 2026-2027

We hereby confirm the registration of {{ idclub }}: {{ name }}
for the interclub season 2026-2027

The following teams were entered:

- teams in division 1: **{{ teams1 }}**
- teams in division 2: **{{ teams2 }}**
- teams in division 3: **{{ teams3 }}**
- teams in division 4: **{{ teams4 }}**
- teams in division 5: **{{ teams5 }}**
- teams in division 6: **{{ teams6 }}**

Wishes:

- Teams grouped by pairing number: {{ grouping [wishes.grouping] }}
- Distribution of teams in same division: {{ splitting [wishes.splitting] }}
- Regional preferences: {{ wishes.regional }}
- Remarks: {{ wishes.remarks }}

The invoice will follow later.

the RBCF board`
