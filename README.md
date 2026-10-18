# Duplicate — Video Cleaner

A browser-based UI for finding numbered duplicate video files. The app runs locally in your browser and does not upload video files.

## Features

- Scan a selected folder and its subfolders for common video formats, including MKV and MP4.
- Group numbered copies such as `Episode (2).mkv` with their base filename.
- Keep original filenames without a numbered suffix out of the results.
- Select copies individually, delete selected copies, or delete all listed copies.
- View file size, duplicate group, and relative folder path.

## Run locally

Because the app uses the File System Access API, open it from a secure context:

1. Install Python if needed.
2. Clone the repository:
   ```bash
   git clone https://github.com/deathkernel/Duplicate.git
   cd Duplicate
   ```
3. Start a local web server:
   ```bash
   py -m http.server 8000
   ```
4. Open http://localhost:8000 in Chrome or Microsoft Edge.
5. Choose a folder, scan, review the results, and then use the delete controls if needed.

## Publish with GitHub Pages

1. Open the repository's **Settings → Pages**.
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Choose branch **main** and folder **/(root)**, then save.
4. Wait for GitHub Pages to publish the site; the URL will appear in Settings → Pages.

## Important safety notes

- Permanent deletion bypasses the Recycle Bin. Review results before deleting.
- The app identifies copies by a trailing numbered suffix, such as `(2)` or `(3)`; it does not compare video contents. A file named this way may not actually be a duplicate.
- Browser support for folder access and deletion is required. Use a current Chrome or Edge browser.
- GitHub Pages only hosts the static web app; it does not access your PC's files. Folder access is granted by you in your browser.
