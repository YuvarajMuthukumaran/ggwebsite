/**
 * The website's side of the HMS -> TeleCRM Event API (internal spec, draft v1.0, 13 Oct 2026;
 * see integrations/telecrm/README.md).
 *
 * A booking form submission is a lead that arrives *before* the patient exists in the HMS,
 * so it is pushed to the same CRM Sync API the HMS uses, in the same envelope and with the
 * same signature. The Sync API then owns validation, de-duplication, retries and the
 * TeleCRM write, exactly as it does for HMS events. Nothing about TeleCRM itself is hard
 * coded here, which is the point: the website never holds TeleCRM credentials.
 *
 * Two things differ from an HMS event, both because a website enquiry is pre-registration:
 *
 *   patient.uhid  A visitor has no UHID yet. The spec's open question "should leads that
 *                 came in before registration (website, calls) be linked to the UHID at
 *                 patient.registered?" answers itself with "yes, matched by phone", so the
 *                 field is sent empty and the phone is the key.
 *   patient.center  The visitor picks Delhi, Gurugram or online; that is a preference, not
 *                 the centre they belong to. It goes in data.preferred_center, and
 *                 patient.center carries the centre code only when one is configured.
 *
 * Configuration (Vercel environment variables):
 *   SYNC_BASE_URL   base of the Sync API, e.g. https://sync.example.com
 *   HMS_KEY_ID      the key id sent as X-HMS-Key-Id, e.g. web-prod-1
 *   HMS_SECRET      the shared secret the signature is computed with
 *   SYNC_CENTER     optional centre code for patient.center, e.g. DEL
 */

const crypto = require('crypto');

const EVENT_TYPE = 'lead.captured';
const TIMEOUT_MS = 8000;

/** The spec signs timestamp + "." + the exact bytes that are sent. */
function sign(secret, timestamp, rawBody) {
  return 'sha256=' + crypto.createHmac('sha256', secret).update(timestamp + '.' + rawBody).digest('hex');
}

/**
 * Same lead, same event_id, so a retry is recognised as a duplicate rather than a new lead.
 *
 * The timestamp is rounded to the minute on purpose. A double submission - the visitor
 * taps twice, or the browser repeats the POST - would otherwise differ only in its
 * received_at and arrive as two leads. Two genuine enquiries from one number about one
 * concern inside the same minute are not a real case; a double tap is.
 */
function eventId(lead) {
  const minute = String(lead.received_at || '').slice(0, 16);   // YYYY-MM-DDTHH:MM
  const basis = [lead.phone, minute, lead.page, lead.concern].join('|');
  const h = crypto.createHash('sha256').update(basis).digest('hex');
  return [h.slice(0, 8), h.slice(8, 12), '4' + h.slice(13, 16), '8' + h.slice(17, 20), h.slice(20, 32)].join('-');
}

function envelope(lead) {
  return {
    event_id: eventId(lead),
    event_type: EVENT_TYPE,
    occurred_at: lead.received_at,
    patient: {
      uhid: '',                                  // none yet: linked at patient.registered, by phone
      name: lead.name,
      phone: lead.phone,
      center: process.env.SYNC_CENTER || '',
      whatsapp_opt_in: false,                    // the form does not ask, so nothing is claimed
    },
    data: {
      source_channel: 'website',
      source: lead.source,
      preferred_center: lead.clinic,             // delhi | gurugram | online, as chosen
      for_whom: lead.who,                        // self | family
      concern: lead.concern,
      page: lead.page,
      utm_source: lead.utm_source,
      utm_medium: lead.utm_medium,
      utm_campaign: lead.utm_campaign,
    },
  };
}

/**
 * Returns {delivered, why, retriable} using the spec's response table:
 *   202 accepted, 200 duplicate -> sent
 *   400 rejected, 401 unauthorized -> do not retry, alert
 *   429 / 5xx -> temporary, retriable
 */
async function pushLead(lead) {
  const { SYNC_BASE_URL, HMS_KEY_ID, HMS_SECRET } = process.env;
  if (!SYNC_BASE_URL || !HMS_KEY_ID || !HMS_SECRET) {
    return null;                                 // not configured; the caller tries the next sink
  }

  const body = JSON.stringify(envelope(lead));
  const ts = String(Math.floor(Date.now() / 1000));
  const stop = new AbortController();
  const timer = setTimeout(() => stop.abort(), TIMEOUT_MS);
  try {
    const r = await fetch(SYNC_BASE_URL.replace(/\/+$/, '') + '/v1/events', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-HMS-Key-Id': HMS_KEY_ID,
        'X-HMS-Timestamp': ts,
        'X-HMS-Signature': sign(HMS_SECRET, ts, body),
      },
      body,
      signal: stop.signal,
    });
    if (r.status === 202 || r.status === 200) return { delivered: true, status: r.status };
    if (r.status === 400 || r.status === 401) {
      let detail = '';
      try { detail = (await r.text()).slice(0, 300); } catch { /* body is optional */ }
      return { delivered: false, retriable: false, why: 'sync rejected ' + r.status + ' ' + detail };
    }
    return { delivered: false, retriable: true, why: 'sync unavailable ' + r.status };
  } catch (e) {
    return { delivered: false, retriable: true, why: e.name === 'AbortError' ? 'sync timed out' : 'sync unreachable' };
  } finally {
    clearTimeout(timer);
  }
}

module.exports = { pushLead, envelope, eventId, sign, EVENT_TYPE };
