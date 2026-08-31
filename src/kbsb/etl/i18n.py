import csv
import json
from pathlib import Path

rootdir = Path(__file__).parents[3]


def process_fide_i18n():
    fide_csv = rootdir / "src" / "kbsb" / "fide" / "translations_fide.csv"
    if not fide_csv.exists():
        return

    data = {"en": {}, "nl": {}, "fr": {}}
    for lang in data:
        data[lang] = {
            "ui": {},
            "categories": {},
            "options": {
                "yes_no": {},
                "age_limit": {},
                "inc_delay": {},
            },
            "fields": {},
            "messages": {},
        }

    with fide_csv.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            section = r["section"]
            key = r["key"]
            for lang in ["en", "nl", "fr"]:
                val = r.get(lang, "")
                if section.startswith("options."):
                    opt_group = section.split(".", 1)[1]
                    if opt_group not in data[lang]["options"]:
                        data[lang]["options"][opt_group] = {}
                    data[lang]["options"][opt_group][key] = val
                else:
                    if section not in data[lang]:
                        data[lang][section] = {}
                    data[lang][section][key] = val

    out_json = rootdir / "src" / "kbsb" / "fide" / "translations.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Generated {out_json}")


def process_i18n():
    allrows = {}
    with (rootdir / "shared" / "translations - kbsb.csv").open(newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for r in reader:
            ctx = r["ctx"]
            ctxrows = allrows.setdefault(ctx, [])
            ctxrows.append(r)
    for lc in ["en", "fr", "nl", "de"]:
        with (rootdir / "frontend" / "lang" / f"{lc}.json").open(
            "w", encoding="utf8"
        ) as f:
            f.write("{\n")
            for ctx, ctxrows in allrows.items():
                for r in ctxrows:
                    if not ctx:
                        f.write(f'"{r["key"]}": "{r[lc]}",\n')
                    else:
                        f.write(f'"{ctx}.{r["key"]}": "{r[lc]}",\n')
            f.write('"ZZZ": "ZZZ"\n')
            f.write("}\n")

    process_fide_i18n()


if __name__ == "__main__":
    process_i18n()
