/**
 * Callback requests from the booking form (assets/js/booking.js).
 *
 * Where a lead goes is configuration, not code. The first destination that is
 * configured wins, so the form can be tested end to end today and switched to
 * TeleCRM later without touching the form or this handler:
 *
 *   SYNC_BASE_URL         the CRM Sync API the HMS pushes to (with HMS_KEY_ID and
 *                         HMS_SECRET). This is the real route to TeleCRM: the Sync API
 *                         validates, de-duplicates, retries and writes the lead, so the
 *                         website never holds TeleCRM credentials. See api/_sync.js.
 *   TELECRM_WEBHOOK_URL   a direct TeleCRM endpoint (with TELECRM_TOKEN), if one is ever
 *                         preferred over the Sync API
 *   CALLBACK_WEBHOOK_URL  a Google Apps Script web app writing to a Sheet
 *                         (with CALLBACK_WEBHOOK_SECRET; see integrations/google-sheet/)
 *
 * With neither set the lead is accepted and written to the function log, and
 * the reply says delivered:false. The thank-you screen always shows the phone
 * number, so a caller is never left without a way through.
 */

const { pushLead } = require('./_sync');

const CLINICS = ['delhi', 'gurugram', 'online'];
const WHO = ['self', 'family'];
const LIMITS = { name: 80, concern: 600, page: 300, utm: 120 };

const clean = (v, max) => (typeof v === 'string' ? v.trim().slice(0, max) : '');

/** Indian mobile numbers, typed how people actually type them: +91, 0, spaces, dashes. */
function normalisePhone(raw) {
  const digits = String(raw || '').replace(/[^\d]/g, '');
  const local = digits.replace(/^(91|0)/, '');
  return local.length === 10 && /^[6-9]/.test(local) ? '+91' + local : '';
}

function validate(body) {
  const errors = {};
  const name = clean(body.name, LIMITS.name);
  if (name.length < 2) errors.name = 'Please give the name we should ask for.';

  const phone = normalisePhone(body.phone);
  if (!phone) errors.phone = 'Please give a 10-digit Indian mobile number.';

  const who = WHO.includes(body.who) ? body.who : '';
  if (!who) errors.who = 'Please say who the consultation is for.';

  const clinic = CLINICS.includes(body.clinic) ? body.clinic : '';
  if (!clinic) errors.clinic = 'Please choose Delhi, Gurugram or online.';

  return {
    errors,
    lead: {
      name, phone, who, clinic,
      concern: clean(body.concern, LIMITS.concern),
      source: 'goravgupta.com',
      page: clean(body.page, LIMITS.page),
      utm_source: clean(body.utm_source, LIMITS.utm),
      utm_medium: clean(body.utm_medium, LIMITS.utm),
      utm_campaign: clean(body.utm_campaign, LIMITS.utm),
      received_at: new Date().toISOString(),
    },
  };
}

async function post(url, payload, headers) {
  const stop = new AbortController();
  const timer = setTimeout(() => stop.abort(), 8000);
  try {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...headers },
      body: JSON.stringify(payload),
      signal: stop.signal,
    });
    return r.ok ? { delivered: true } : { delivered: false, why: 'destination returned ' + r.status };
  } catch (e) {
    return { delivered: false, why: e.name === 'AbortError' ? 'destination timed out' : 'destination unreachable' };
  } finally {
    clearTimeout(timer);
  }
}

const CLINIC_LABEL = { delhi: 'New Delhi', gurugram: 'Gurugram', online: 'Online' };
const WHO_LABEL = { self: 'Themselves', family: 'A family member' };

/**
 * TeleCRM's website integration endpoint takes a flat "fields" object. Names are the ones
 * a telecaller reads in the lead, so they are written the way they should appear on screen.
 */
function telecrmPayload(lead) {
  return {
    fields: {
      Name: lead.name,
      Phone: lead.phone,
      Source: 'goravgupta.com',
      'Enquiry For': WHO_LABEL[lead.who] || lead.who,
      'Preferred Centre': CLINIC_LABEL[lead.clinic] || lead.clinic,
      Concern: lead.concern,
      'Page Submitted From': lead.page,
      'Received At': lead.received_at,
      'UTM Source': lead.utm_source,
      'UTM Medium': lead.utm_medium,
      'UTM Campaign': lead.utm_campaign,
    },
  };
}


async function deliver(lead) {
  const { TELECRM_WEBHOOK_URL, TELECRM_TOKEN, CALLBACK_WEBHOOK_URL } = process.env;

  // The Sync API first: it is the route the HMS uses, so a website lead lands in TeleCRM
  // the same way, with the same signing, de-duplication and retries.
  const viaSync = await pushLead(lead);
  if (viaSync) return viaSync;

  if (TELECRM_WEBHOOK_URL) {
    return post(TELECRM_WEBHOOK_URL, telecrmPayload(lead),
                TELECRM_TOKEN ? { Authorization: 'Bearer ' + TELECRM_TOKEN } : {});
  }
  if (CALLBACK_WEBHOOK_URL) {
    // An Apps Script web app has to be readable by anyone, so the shared secret is what
    // stops a stranger who finds the URL writing rows into the sheet.
    const { CALLBACK_WEBHOOK_SECRET } = process.env;
    return post(CALLBACK_WEBHOOK_URL, CALLBACK_WEBHOOK_SECRET ? { ...lead, secret: CALLBACK_WEBHOOK_SECRET } : lead, {});
  }
  return { delivered: false, why: 'no destination configured' };
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Use POST.' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch { body = {}; }
  }
  body = body || {};

  // A bot fills every field it is given; a person never sees this one.
  if (clean(body.website, 50)) return res.status(200).json({ ok: true, delivered: true });

  // Without JavaScript the browser posts the form itself, so answer with pages rather than JSON.
  const asForm = String(req.headers['content-type'] || '').includes('form-urlencoded');

  const { errors, lead } = validate(body);
  const back = lead.page || '/contactus/';
  if (Object.keys(errors).length) {
    if (asForm) return res.redirect(303, back + '?booking=invalid#book');
    return res.status(400).json({ ok: false, errors });
  }

  const result = await deliver(lead);
  if (!result.delivered) {
    // Not lost: it is in the function log, and every thank-you gives the phone number.
    // retriable:false means the Sync API refused the event itself (bad field, bad key),
    // which is a thing to fix rather than wait out, so it is logged differently.
    const tag = result.retriable === false ? 'CALLBACK REJECTED' : 'CALLBACK NOT DELIVERED';
    console.error('%s (%s): %j', tag, result.why, lead);
  }
  if (asForm) return res.redirect(303, '/thank-you/');
  return res.status(200).json({ ok: true, delivered: result.delivered });
};
