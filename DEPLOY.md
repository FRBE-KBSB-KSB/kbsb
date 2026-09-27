# Deploying the website

The site runs on Google App Engine, project `website-kbsb-prod`, service
`default`. The backend (FastAPI) and the built frontend (Nuxt, static) are
deployed together from the repository root with `app.yaml`.

## Before the first deploy from a machine

- `gcloud auth login` with an account that may deploy to `website-kbsb-prod`.
- The secret `kbsb-jwt` must exist in Secret Manager (see `SECURITY.md`).
  Production does not start without it.
- `dist` in the repository is a link to `frontend/.output/public`, which
  `app.yaml` serves the pages from. On Windows git checks it out as a plain
  file; replace it once with a directory junction and tell git to leave it
  alone:

  ```powershell
  Remove-Item dist
  cmd /c mklink /J dist frontend\.output\public
  git update-index --skip-worktree dist
  ```

## Deploy

1. Start from an up-to-date `master` (`git pull`).
2. Build the frontend when the frontend changed (backend-only changes do not
   need it):

   ```bash
   cd frontend
   API_URL=https://www.frbe-kbsb-ksb.be/ yarn generate
   cd ..
   ```

3. Deploy without traffic:

   ```bash
   gcloud app deploy app.yaml --no-promote --project=website-kbsb-prod
   ```

4. Test on the new version's own URL (printed by the deploy): the home page, a
   club page, a member login. The Google admin login only works on
   `https://www.frbe-kbsb-ksb.be` (Google refuses other addresses), so test
   that after the next step.
5. Send traffic to it:

   ```bash
   gcloud app services set-traffic default --splits=<new-version>=1 --project=website-kbsb-prod
   ```

6. On `www`: admin login at `/mgmt`, a club manager save, an interclub page.

## Rollback

Send traffic back to the previous version:

```bash
gcloud app versions list --service=default --project=website-kbsb-prod
gcloud app services set-traffic default --splits=<previous-version>=1 --project=website-kbsb-prod
```

Keep a few recent versions for this, and delete old ones once they are no
longer needed.

## Mail

The FIDE registration form (`src/kbsb/fide/api_fide.py`) sends each
registration to `fide@frbe-kbsb-ksb.be` and, in BCC, to
`autoratingfide@frbe-kbsb-ksb.be`, which the dataplatform reads to queue the
workbook for processing.
