# Nabil & Risha

A single-file wedding invitation. Open `site/index.html` (with `site/img/` beside it).

## Run

```bash
cd site
python -m http.server 5180
```

Then open http://127.0.0.1:5180/

## Regenerate images

Source illustrations live in `public/photos/`. To rebuild the WebPs in `site/img/`:

```bash
python scripts/prep-images.py
```

## Guest photo upload

Guests can send up to 5 photos from the invite footer. Images are resized in the browser, then saved to your Google Drive by a small Apps Script web app. Guests do not need a Google account.

### One-time setup

1. In [Google Drive](https://drive.google.com), create a folder (for example `Wedding guest photos`).
2. Open the folder and copy its ID from the URL:
   `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
3. Open [script.google.com](https://script.google.com) → **New project**.
4. Paste the contents of [`scripts/drive-upload.gs`](scripts/drive-upload.gs) into the editor.
5. Set `FOLDER_ID` to the Drive folder ID from step 2. Save.
6. **Deploy → New deployment → Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**
7. Authorize the script when prompted, then copy the web app URL that ends in `/exec`.
8. In [`site/index.html`](site/index.html), find `DRIVE_UPLOAD_URL` and paste that `/exec` URL between the quotes.
9. Open the invite on your phone, send a test photo, and confirm a guest subfolder appears in Drive.

If you change the Apps Script later, deploy a **new version** of the same web app so the `/exec` URL keeps working.
