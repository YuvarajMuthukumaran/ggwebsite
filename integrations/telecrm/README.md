# Website leads into TeleCRM

The booking form does not talk to TeleCRM. It pushes one event to the **CRM Sync API** —
the same service the HMS pushes to, described in [`docs/HMS-TeleCRM-Event-API.pdf`](../../docs/HMS-TeleCRM-Event-API.pdf) —
and the Sync API owns validation, de-duplication, retries and the TeleCRM write.

```
booking form  ->  /api/callback/  ->  CRM Sync API  ->  TeleCRM  ->  WhatsApp / telecaller task
```

That is deliberate. The website holds no TeleCRM credentials, gets the retry behaviour the
spec already defines, and changes to TeleCRM's own API never reach this repo.

## The event

`POST {SYNC_BASE_URL}/v1/events`, signed exactly as section 2 of the spec requires:

| Header | Value |
| --- | --- |
| `X-HMS-Key-Id` | `HMS_KEY_ID` |
| `X-HMS-Timestamp` | Unix seconds |
| `X-HMS-Signature` | `sha256=HMAC-SHA256(HMS_SECRET, timestamp + "." + raw_body)` |

```json
{
  "event_id": "628489c3-e450-4fd6-8cac-804d60f05253",
  "event_type": "lead.captured",
  "occurred_at": "2026-10-16T11:51:41.140Z",
  "patient": {
    "uhid": "",
    "name": "Asha Verma",
    "phone": "+919812345678",
    "center": "DEL",
    "whatsapp_opt_in": false
  },
  "data": {
    "source_channel": "website",
    "source": "goravgupta.com",
    "preferred_center": "gurugram",
    "for_whom": "family",
    "concern": "My brother has been drinking heavily",
    "page": "/psychiatrist-de-addiction-treatment-delhi-gurgaon/",
    "utm_source": "gmb", "utm_medium": "gurgaon", "utm_campaign": ""
  }
}
```

Responses are handled per section 4: `202` and `200` count as sent; `400` and `401` are
logged as rejected and not retried, because they mean something is wrong with the request
rather than with the moment; `429` and `5xx` are logged as temporary.

`event_id` is derived from the phone, the page, the concern and the timestamp **rounded to
the minute**, so a double tap or a repeated POST carries the same id and the Sync API's
duplicate check collapses it into one lead.

## Three things this makes assumptions about

A website enquiry is not an HMS event, and the spec is written for HMS events. Where they
differ, this is what the website does and why:

1. **`patient.uhid` is empty.** The visitor has no UHID; they are not a patient yet. The
   spec's own open question — *"should leads that came in before registration (website,
   calls) be linked to the UHID at `patient.registered`?"* — answers *"yes, matched by
   phone"*, so the phone is the key and the link happens later. **If the Sync API rejects
   an empty `uhid`, this is the field to relax.**
2. **`event_type` is `lead.captured`**, which is not one of the ten HMS events. The Sync
   API needs to accept it, and TeleCRM needs a workflow for it, or the lead lands with no
   follow-up task.
3. **`whatsapp_opt_in` is `false`.** The form does not ask for consent, so none is claimed.
   If the team wants WhatsApp to go out on an enquiry, the form needs a consent checkbox
   first — not a default of `true`.

`patient.center` carries `SYNC_CENTER` when it is set, because the centre a lead *belongs*
to is not the same as the one they picked. The choice they made is in `data.preferred_center`.

## Setting it up

In the Vercel project → Settings → Environment Variables, for all environments:

| Name | Value |
| --- | --- |
| `SYNC_BASE_URL` | base URL of the Sync API, no trailing path |
| `HMS_KEY_ID` | the key id issued for the website, e.g. `web-prod-1` |
| `HMS_SECRET` | the shared secret for that key |
| `SYNC_CENTER` | optional centre code for `patient.center` |

Redeploy afterwards: environment variables only reach a deployment built after they were
added.

### Check it

```bash
curl -s -X POST -H 'Content-Type: application/json' \
  -d '{"name":"Test Lead","phone":"9812345678","who":"self","clinic":"delhi","concern":"ignore, testing","page":"/contactus/"}' \
  https://ggwebsite-ivory.vercel.app/api/callback/
```

`{"ok":true,"delivered":true}` means the Sync API accepted it (202 or 200). `delivered:false`
means it did not, and the Vercel function log says which of the four cases it was. The lead
is in that log either way, and every thank-you screen shows the phone number, so nobody is
left without a way through.

## Until the Sync API is ready

`api/callback.js` tries destinations in order, so leaving `SYNC_BASE_URL` unset falls
through to the interim Google Sheet in [`../google-sheet/`](../google-sheet/). Setting the
Sync API variables later switches the route with no code change, and the sheet variables
can stay in place for a week or two as a comparison.

**Before cutover:** the form must not go live with no destination set. It would accept
enquiries and show a thank-you while writing them only to the function log.
