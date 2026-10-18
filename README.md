# Duplicate — Video Cleaner

A browser-based website for finding numbered duplicate video copies. The website runs locally on your PC in Chrome or Microsoft Edge. Your video files are not uploaded anywhere.

## Quick start on Windows

1. Download or clone this repository.
2. Double-click **`start_website.bat`**.
3. The website opens at **http://localhost:8000** in your browser.
4. Click **Choose folder**, select the folder containing your videos, then click **Scan videos**.
5. Select copies you want to remove and choose **Delete selected** or **Delete all copies**.

Keep the black command window open while using the website. Closing it stops the local server.

### If the website does not open

Install Python from https://www.python.org/downloads/windows/ and enable **Add Python to PATH** during installation. Then double-click `start_website.bat` again. You can also start the server manually from this folder with:

```powershell
py -m http.server 8000 --bind 127.0.0.1
```

Then visit http://localhost:8000 in Chrome or Edge.

## Features

- Scans the selected folder and subfolders for MKV, MP4, AVI, MOV, WMV, FLV, WEBM, M4V, MPEG, MPG, TS, MTS, M2TS, 3GP and VOB.
- Finds numbered copies such as `Episode (2).mkv` and matches extensions separately.
- Keeps original filenames without a numbered suffix out of the results.
- Select all, delete selected, or delete all listed copies.
- Shows scan counts, copy counts, file sizes and estimated space that can be reclaimed.
- All scanning happens in your browser; no video upload or cloud account is needed.

## Important safety notes

- **Deletion is permanent and bypasses the Recycle Bin.** Review the list before deleting.
- The app identifies likely copies by a trailing numbered suffix, such as `(2)` or `(3)`; it does not compare video contents. A filename alone cannot guarantee two files have identical contents.
- Use a current Chrome or Microsoft Edge browser. Folder access requires the local website at localhost and your explicit folder permission.
- The server binds to `127.0.0.1`, so it is only available from your own PC.
