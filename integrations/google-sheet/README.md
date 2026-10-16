# The interim lead sheet

Until TeleCRM's lead endpoint is confirmed, callback requests from the booking form land in a Google
Sheet. Nothing in the site changes when we switch over: `api/callback.js` sends the lead to whichever
destination is configured, and TeleCRM simply takes priority once its variables are set.

Only you can do these steps — the script is deployed under a Google account, and the variables are
set in the Vercel project.

## 1 · The sheet and the script

1. Create a Google Sheet. Name it something like **goravgupta.com leads**. Leave it empty; the script
   adds a `Leads` tab with its own header row on the first submission.
2. In that sheet: **Extensions → Apps Script**.
3. Delete whatever is in `Code.gs` and paste the contents of [`Code.gs`](Code.gs) from this folder.
4. **Project Settings → Script Properties → Add script property**:
   - Property `SECRET`
   - Value: a long random string. Generate one and keep it to hand — Vercel needs the same value.

     ```bash
     openssl rand -hex 24
     ```
5. **Deploy → New deployment → Web app**:
   - Description: `callback sheet`
   - Execute as: **Me**
   - Who has access: **Anyone**
6. Copy the **Web app URL**. It looks like
   `https://script.google.com/macros/s/AKfy…/exec`.

"Anyone" is required — Vercel calls this URL without a Google login. That is why the `SECRET` matters:
it is the only thing stopping someone who finds the URL from writing rows into the sheet.

Google will warn you that the script is unverified the first time. It is your own script, so continue
through **Advanced → Go to (project name)**.

## 2 · The variables in Vercel

In the Vercel project → **Settings → Environment Variables**, add both, for **all** environments
(Production, Preview, Development):

| Name | Value |
| --- | --- |
| `CALLBACK_WEBHOOK_URL` | the Web app URL from step 6 |
| `CALLBACK_WEBHOOK_SECRET` | the same string you put in `SECRET` |

Environment variables only reach a deployment built after they were added, so **redeploy** once
they're saved: Deployments → the latest one → ⋯ → Redeploy.

## 3 · Check it

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"name":"Test Lead","phone":"9812345678","who":"self","clinic":"delhi","concern":"ignore, testing","page":"/contactus/"}' \
  https://ggwebsite-ivory.vercel.app/api/callback/
```

`{"ok":true,"delivered":true}` means the row is in the sheet. **`"delivered":false` means it is not** —
the lead is only in the Vercel function log. Check, in order: both variables are set, the deployment
is newer than they are, and the secret matches on both sides.

Then submit the form once from the site itself, so the whole path is exercised the way a patient
exercises it.

## 4 · When TeleCRM is ready

Add `TELECRM_WEBHOOK_URL` (and `TELECRM_TOKEN`, sent as `Authorization: Bearer …`) and redeploy.
TeleCRM takes priority, so leads stop going to the sheet with no code change. Keep the sheet
variables in place for a week or two: if TeleCRM rejects a lead, the handler logs it, and it is
easier to compare against a sheet that was still filling.

The lead sent to either destination is the same JSON:

```json
{
  "name": "Asha Verma",
  "phone": "+919812345678",
  "who": "self | family",
  "clinic": "delhi | gurugram | online",
  "concern": "",
  "source": "goravgupta.com",
  "page": "/psychiatrist-de-addiction-treatment-delhi-gurgaon/",
  "utm_source": "", "utm_medium": "", "utm_campaign": "",
  "received_at": "2026-10-16T06:31:20.153Z"
}
```

`received_at` is UTC; the sheet writes it in IST. The phone is normalised to `+91` and ten digits
before it is sent, so the CRM never receives two formats of the same number.

## Before cutover

**The form must not go live on goravgupta.com with no destination set.** It would accept enquiries
and return a thank-you while writing them only to the function log. Check that the command in step 3
answers `"delivered":true` against the production domain before the DNS change, not after.
