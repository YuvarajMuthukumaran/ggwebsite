/**
 * Callback requests from goravgupta.com into a Google Sheet.
 *
 * This is the interim destination, until TeleCRM's lead endpoint is confirmed.
 * api/callback.js posts a lead here when CALLBACK_WEBHOOK_URL is set; see
 * integrations/google-sheet/README.md for deploying it and setting the variables.
 *
 * A web app has to be reachable by anyone, so SECRET is what stops a stranger who
 * finds the URL writing rows into the sheet. Set it in Script Properties, and set
 * the same value as CALLBACK_WEBHOOK_SECRET in Vercel.
 */

var SHEET_NAME = 'Leads';

var COLUMNS = [
  ['received_at', 'Received (IST)'],
  ['name', 'Name'],
  ['phone', 'Mobile'],
  ['who', 'For'],
  ['clinic', 'Where'],
  ['concern', 'Concern'],
  ['page', 'Page'],
  ['utm_source', 'utm_source'],
  ['utm_medium', 'utm_medium'],
  ['utm_campaign', 'utm_campaign'],
  ['source', 'Source']
];

var LABEL = {
  self: 'Themselves',
  family: 'A family member',
  delhi: 'New Delhi',
  gurugram: 'Gurugram',
  online: 'Online'
};

function json(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}

function sheet() {
  var book = SpreadsheetApp.getActiveSpreadsheet();
  var tab = book.getSheetByName(SHEET_NAME) || book.insertSheet(SHEET_NAME);
  if (tab.getLastRow() === 0) {
    tab.appendRow(COLUMNS.map(function (c) { return c[1]; }));
    tab.getRange(1, 1, 1, COLUMNS.length).setFontWeight('bold');
    tab.setFrozenRows(1);
  }
  return tab;
}

/** IST, so the row reads the way the team reads a clock. */
function istStamp(iso) {
  var when = iso ? new Date(iso) : new Date();
  if (isNaN(when.getTime())) when = new Date();
  return Utilities.formatDate(when, 'Asia/Kolkata', 'yyyy-MM-dd HH:mm:ss');
}

function doPost(e) {
  var lead;
  try {
    lead = JSON.parse((e && e.postData && e.postData.contents) || '{}');
  } catch (err) {
    return json({ ok: false, error: 'not JSON' });
  }

  var expected = PropertiesService.getScriptProperties().getProperty('SECRET');
  if (expected && lead.secret !== expected) {
    return json({ ok: false, error: 'bad secret' });
  }

  if (!lead.name || !lead.phone) {
    return json({ ok: false, error: 'name and phone are required' });
  }

  // Two people can submit at the same moment; without the lock they can land on one row.
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
  } catch (err) {
    return json({ ok: false, error: 'busy' });
  }

  try {
    var tab = sheet();
    tab.appendRow(COLUMNS.map(function (c) {
      var key = c[0];
      if (key === 'received_at') return istStamp(lead.received_at);
      var value = lead[key] == null ? '' : String(lead[key]);
      return LABEL[value] || value;
    }));
    return json({ ok: true });
  } catch (err) {
    return json({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

/** Opening the deployment URL in a browser should say something useful. */
function doGet() {
  return json({ ok: true, service: 'goravgupta.com callback sheet', rows: sheet().getLastRow() - 1 });
}
