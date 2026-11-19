"""
Checks around a deploy, so a deploy cannot quietly break logins or secrets.

    uv run python scripts/deploy_check.py before   # run by `poe deploy` first
    uv run python scripts/deploy_check.py after    # run by `poe deploy` last

before (nothing is deployed yet; read-only):
  - every secret the code reads is configured in settings.SECRETS, exists in
    Secret Manager with an enabled latest version, and has the shape the code
    expects (the superuser secret holds SU__ names, the salt a "salt", ...);
    #149 renamed a secret without its reader and broke every superuser login
  - the backend tests pass

after (against the live site; read-only):
  - the home page, a public interclub page and a public API answer
  - a forged admin token is refused on the account routes (401)
  - a superuser login with a wrong password is refused (401), not a 500
  - /openapi.json is not served (404)

Prints what it checks, never a secret's value. Exits 1 when anything fails,
which stops `poe deploy` before the upload (before) or flags it (after).
Needs Application Default Credentials for the project (`poe gcp_init`).
"""

import base64
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.frbe-kbsb-ksb.be"
PROJECT = "website-kbsb-prod"

# secrets read in code that does not run: reported, not failed
UNUSED = {
    "gdrive": "src/kbsb/core/site.py, only imported in a comment",
    "postgres": "configured, but nothing reads it",
}

# secrets read without a literal get_secret("name") in src/: inside reddevil
# (mongodb), or through a variable (turnstile.py)
READ_BY_LIBRARIES = {"mongodb", "salt", "turnstile"}

# the shape each secret must have: a function returning a problem or None
SHAPES = {
    "superuser": lambda v: (
        None
        if isinstance(v, dict)
        and v
        and all(k.startswith("SU__") and isinstance(p, str) and p for k, p in v.items())
        else "must map SU__ names to non-empty passwords"
    ),
    "salt": lambda v: (
        None if isinstance(v, dict) and v.get("salt") else 'needs a "salt"'
    ),
    "mongodb": lambda v: (
        None
        if isinstance(v, dict) and (v.get("url") or v.get("uri"))
        else "needs a url"
    ),
    "turnstile": lambda v: None if isinstance(v, str) and v.strip() else "is empty",
    "mailrelay": lambda v: None if isinstance(v, str) and v.strip() else "is empty",
    "eloserver": lambda v: None if isinstance(v, str) and v.strip() else "is empty",
    "jwt": lambda v: (
        None
        if isinstance(v, dict)
        and isinstance(v.get("secret"), str)
        and len(v["secret"]) >= 32
        else 'needs a "secret" of at least 32 characters'
    ),
}

failures: list[str] = []
notes: list[str] = []


def ok(text: str) -> None:
    print(f"  ok    {text}")


def fail(text: str) -> None:
    print(f"  FAIL  {text}")
    failures.append(text)


def note(text: str) -> None:
    print(f"  note  {text}")
    notes.append(text)


def settings_secrets() -> dict:
    sys.path.insert(0, str(ROOT / "src"))
    from kbsb import settings  # the production settings, not env_*.py

    return settings.SECRETS


def names_read_in_code() -> set[str]:
    names = set()
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        names.update(re.findall(r"get_secret\(\s*[\"']([^\"']+)[\"']", text))
    return names


def check_secrets() -> None:
    print("secrets")
    from google.cloud import secretmanager

    configured = settings_secrets()
    client = secretmanager.SecretManagerServiceClient()
    wanted = names_read_in_code() | READ_BY_LIBRARIES

    for name in sorted(wanted - set(configured)):
        if name in UNUSED:
            note(f"{name}: read but not configured ({UNUSED[name]})")
        else:
            fail(f"{name}: the code reads it, settings.SECRETS has no entry")

    for name, cfg in sorted(configured.items()):
        sname, manager = cfg.get("name", name), cfg.get("manager", "filejson")
        if name not in wanted:
            if name in UNUSED:
                note(f"{name} ({sname}): {UNUSED[name]}")
            else:
                note(f"{name} ({sname}): configured, not read anywhere")
            continue
        if not manager.startswith("google"):
            fail(f"{name}: manager {manager} does not work on App Engine")
            continue
        version = cfg.get("version", "latest")
        try:
            reply = client.access_secret_version(
                request={
                    "name": f"projects/{PROJECT}/secrets/{sname}/versions/{version}"
                }
            )
        except Exception as e:
            fail(f"{name}: secret {sname} cannot be read ({type(e).__name__})")
            continue
        data = reply.payload.data.decode("utf-8")
        try:
            value = json.loads(data) if manager == "googlejson" else data
        except ValueError:
            fail(f"{name}: secret {sname} is not valid JSON")
            continue
        shape = SHAPES.get(name)
        problem = shape(value) if shape else None
        if problem:
            fail(f"{name}: secret {sname} {problem}")
        else:
            ok(f"{name} -> {sname}")


def check_tests() -> None:
    print("tests")
    r = subprocess.run(
        ["uv", "run", "pytest", "-q", "-x", "-p", "no:cacheprovider"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
    if r.returncode == 0:
        ok(last)
    else:
        fail(f"backend tests: {last}")


def _b64(obj) -> str:
    raw = json.dumps(obj).encode() if not isinstance(obj, bytes) else obj
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def check_live() -> None:
    import httpx

    print(f"live site ({SITE})")
    with httpx.Client(base_url=SITE, timeout=30, follow_redirects=True) as http:

        def status(method: str, path: str, want: int, label: str, **kw) -> None:
            try:
                got = http.request(method, path, **kw).status_code
            except Exception as e:
                fail(f"{label}: no answer ({type(e).__name__})")
                return
            (ok if got == want else fail)(f"{label}: {got} (want {want})")

        status("GET", "/", 200, "home page")
        status("GET", "/tools/interclub_public", 200, "public interclub page")
        status(
            "GET", "/api/v1/interclubs/anon/icstandings?idclub=190", 200, "public API"
        )
        status("GET", "/openapi.json", 404, "API description not served")

        forged = ".".join(
            [
                _b64({"alg": "HS256", "typ": "JWT"}),
                _b64({"sub": "deploy-check@example.be", "exp": 4102444800}),
                _b64(b"forged"),
            ]
        )
        status(
            "GET",
            "/api/v1/accounts/mgmt/account",
            401,
            "forged admin token refused",
            headers={"Authorization": f"Bearer {forged}"},
        )
        # a name nobody has, so no real superuser is ever counted or locked
        status(
            "POST",
            "/api/v1/member/login",
            401,
            "wrong superuser password refused",
            json={"email": "SU__deploycheck", "password": "not-the-password"},
        )


def main() -> int:
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage == "before":
        check_secrets()
        check_tests()
    elif stage == "after":
        check_live()
    else:
        print(__doc__)
        return 2
    print()
    if failures:
        print(f"{len(failures)} check(s) failed:")
        for f in failures:
            print(f"  - {f}")
        if stage == "before":
            print("Nothing was deployed.")
        return 1
    print("all checks passed" + (f" ({len(notes)} note(s))" if notes else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
