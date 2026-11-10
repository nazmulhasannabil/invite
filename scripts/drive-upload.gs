/**
 * Guest photo upload for the Nabil & Risha invitation.
 *
 * Setup:
 * 1. Create a Google Drive folder for wedding guest photos.
 * 2. Open the folder and copy the ID from the URL:
 *    https://drive.google.com/drive/folders/FOLDER_ID_HERE
 * 3. Paste that ID into FOLDER_ID below.
 * 4. In script.google.com: New project → paste this file → Save.
 * 5. Deploy → New deployment → Type: Web app
 *      Execute as: Me
 *      Who has access: Anyone
 * 6. Copy the /exec URL into DRIVE_UPLOAD_URL in site/index.html
 *
 * This file does not run from the repo; it only lives here as source
 * to paste into Apps Script.
 */

var FOLDER_ID = '11p2asW71Mn6rpgvbkW0vVrrk1OAtBRRx';
var MAX_PHOTOS = 5;

function doPost(e) {
  try {
    if (!e || !e.postData || !e.postData.contents) {
      return json_({ ok: false, error: 'Empty request.' });
    }

    var payload = JSON.parse(e.postData.contents);
    var name = sanitizeName_(payload && payload.name);
    var photos = payload && payload.photos;

    if (!name) {
      return json_({ ok: false, error: 'Name is required.' });
    }
    if (!photos || !photos.length) {
      return json_({ ok: false, error: 'Add at least one photo.' });
    }
    if (photos.length > MAX_PHOTOS) {
      return json_({ ok: false, error: 'You can send up to 5 photos at a time.' });
    }
    if (!FOLDER_ID || FOLDER_ID.indexOf('PASTE_') === 0) {
      return json_({ ok: false, error: 'Upload is not configured yet.' });
    }

    var parent = DriveApp.getFolderById(FOLDER_ID);
    var folder = parent.createFolder(name + '_' + stamp_());

    for (var i = 0; i < photos.length; i++) {
      var photo = photos[i] || {};
      var raw = String(photo.data || '');
      var comma = raw.indexOf(',');
      if (raw.indexOf('base64') !== -1 && comma >= 0) {
        raw = raw.slice(comma + 1);
      }
      if (!raw) {
        return json_({ ok: false, error: 'One of the photos was empty.' });
      }

      var mime = String(photo.mimeType || 'image/jpeg');
      var filename = sanitizeFilename_(photo.filename, i + 1);
      var bytes = Utilities.base64Decode(raw);
      var blob = Utilities.newBlob(bytes, mime, filename);
      folder.createFile(blob);
    }

    return json_({ ok: true, folderId: folder.getId() });
  } catch (err) {
    return json_({ ok: false, error: String(err && err.message ? err.message : err) });
  }
}

function doGet() {
  return json_({ ok: true, service: 'nabil-risha-photo-upload' });
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function sanitizeName_(value) {
  var name = String(value || '')
    .replace(/[\u0000-\u001f\u007f]/g, '')
    .replace(/[\\/:*?"<>|]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  if (name.length > 80) name = name.slice(0, 80).trim();
  return name;
}

function sanitizeFilename_(value, index) {
  var name = String(value || '')
    .replace(/[\u0000-\u001f\u007f]/g, '')
    .replace(/[\\/:*?"<>|]+/g, '_')
    .trim();
  if (!name) name = 'photo-' + index + '.jpg';
  if (!/\.[A-Za-z0-9]+$/.test(name)) name += '.jpg';
  if (name.length > 100) {
    var ext = name.match(/\.[A-Za-z0-9]+$/);
    var base = name.slice(0, 100 - ((ext && ext[0].length) || 0));
    name = base + (ext ? ext[0] : '.jpg');
  }
  return name;
}

function stamp_() {
  return Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd_HHmmss');
}
