import csv
from pathlib import Path

rootdir = Path("..")


def process_i18n():
    allrows = {}
    with (rootdir / "shared" / "translations - kbsb.csv").open(newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for r in reader:
            ctx = r["ctx"]
            ctxrows = allrows.setdefault(ctx, [])
            ctxrows.append(r)
    for l in ["en", "fr", "nl", "de"]:
        with (rootdir / "frontend" / "lang" / f"{l}.json").open(
            "w", encoding="utf8"
        ) as f:
            f.write("{\n")
            for ctx, ctxrows in allrows.items():
                for r in ctxrows:
                    if not ctx:
                        f.write(f'"{r["key"]}": "{r[l]}",\n')
                    else:
                        f.write(f'"{ctx}.{r["key"]}": "{r[l]}",\n')
            f.write('"ZZZ": "ZZZ"\n')
            f.write("}\n")


if __name__ == "__main__":
    process_i18n()
