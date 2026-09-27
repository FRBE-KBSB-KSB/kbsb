# Security

How logins, tokens and access to data work on this site, and the rules for
code that touches them. Please read this before adding or changing an API
route.

To report a security problem, contact the KBSB IT managers directly, not
through a public issue.

## Secrets

- No secret goes into this repository, ever: no keys, passwords, tokens or
  service-account files. They live in Google Secret Manager (project
  `website-kbsb-prod`) and are read through `SECRETS` in
  `src/kbsb/settings.py` and `reddevil.core.get_secret`.
- `JWT_SECRET` in `settings.py` is only for local runs and tests. In production
  `src/kbsb/main.py` replaces it at startup with the secret `kbsb-jwt`
  (JSON `{"secret": "..."}`). Without that secret the application does not
  start, on purpose: falling back to a value in a public repository would let
  anyone sign a valid login.
- Changing `kbsb-jwt` logs everyone out once. That is also the way to log
  everyone out after an incident.

## Logins and tokens

All tokens are JWTs signed with `JWT_SECRET` plus a salt. They are checked in
`src/kbsb/core/tokens.py`; always verify through those functions. Never use
`jwt_getunverifiedpayload` (or any unverified decode) to decide who someone
is: an unverified payload is whatever the caller wrote.

| Login | Issued by | Salt | Checked with | Opens |
|---|---|---|---|---|
| Member (Odoo e-mail and password) | `member.odoo_member.odoo_login` | `SALT` (`member/md_member.py`) | `validate_membertoken` | `/clb` routes |
| Superuser (`SU__<name>`) | `member.member.superuser_login` | `SALT` | both checks | `/clb` and `/mgmt` |
| Admin (Google account on the federation's domain) | `reddevil.account` | the account's own `tokensalt` | `validate_token` | `/mgmt` routes |

- Tokens expire after `TOKEN["timeout"]` minutes (180), and expiry is enforced.
- A member token does not open `/mgmt`.
- A Google admin login keeps the account's existing salt (patched in
  `main.py`), because the frontend logs in twice in quick succession and a new
  salt per login would invalidate the first token.

### Adding a superuser

1. Add `"SU__<name>": {"name": "su_<name>", "manager": "googlejson"}` to
   `SECRETS` in `settings.py`.
2. Create the secret `su_<name>` with `{"password": "..."}`, a long random
   password, created on your own machine and never pasted into a chat or
   issue.
3. Deploy. A superuser can see and change every club, so agree it with the
   board first.

## Who may see what

### `/anon` routes (no login)

Only data that is meant to be public.

- **Never return a stored model as it is.** Define a public response model with
  only the fields a public page shows, and map to it. Example: `/anon/club/{id}`
  returns `ClubPublic` (`club/md_club.py`), built by `public_club`
  (`club/club.py`): no bank details, no admin or finance e-mail, no club roles,
  no member numbers.
- Board members' e-mail and mobile are shown only when the person set them to
  `PUBLIC`; otherwise the value is `#NA`, which the pages hide. No setting
  counts as not public.
- Interclub line-ups are hidden until the round is open (`isRoundOpen`).
- Bulk exports (for example `/anon/csvclubs`) need an admin token.

### `/clb` routes (member login)

Being logged in is not enough: every route checks that the member may act for
**the club or member in the request**.

- Club data: `verify_club_access(idclub, member, role)` for the club in the
  path or body. The club record needs `ClubAdmin`; interclub data needs
  `InterclubAdmin` or `InterclubCaptain` (`_ic_access` in
  `interclubs/api_interclubs.py`). Results may be entered by an admin or
  captain of either club in the match.
- Member details: only your own record (or a superuser).
- Other clubs' planned line-ups stay hidden until the round opens.
- The browser checking a role is a convenience, not protection. The server
  check is the protection; a new `/clb` route without it is a bug.

### `/mgmt` routes (admin)

`validate_token` on every route, including downloads that take the token as
a URL parameter (verify it the same way; never decode it unverified).

## Checklist for a new or changed route

- `/anon`: does it return only public fields, through a public model?
- `/clb`: does it check the club or member in the request, not only the login?
- `/mgmt`: does it call `validate_token`?
- No secret, key or password in the code or settings.
- A test that a caller without the right login or role is refused.
