# Lyrics API for Stream Music

A lyrics API and management system for [Stream Music](https://github.com/gitbobobo/StreamMusic), with LRC timestamp support, MySQL storage, and web UI.

## Features

| Module | Port | Description |
|--------|------|-------------|
| Lyrics API | 4091 | Stream Music custom lyrics interface |
| Web Manager | 4092 | Upload, search, view, delete lyrics |
| Bulk Import | CLI | Import entire folder of .lrc/.txt files |

- Compatible with [Stream Music Custom API spec](https://music.aqzscn.cn/docs/guides/interfaces)
- LRC timestamp lyrics support
- MySQL storage with fuzzy search
- Drag-and-drop web upload
- systemd auto-start with waitress WSGI server
## Quick Start

### Requirements
- Python 3.10 or higher, MySQL 8.x, pip

### Install
cd api && pip install -r requirements.txt

### Database
CREATE DATABASE IF NOT EXISTS song CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
The lyrics table is auto-created on first run.

### Configure
Edit DB_CONFIG in lyrics_api.py and lyrics_manager.py with your MySQL credentials.

### Import Lyrics
python3 import_lyrics.py /path/to/lrc/files
File naming: Artist - Title.lrc or Artist - Title.txt

### Start
bash start.sh
Or separately: python3 lyrics_api.py (port 4091) / python3 lyrics_manager.py (port 4092)
## API Endpoints

### GET /lyrics - Fetch lyrics (raw LRC text)

| Param | Type | Description |
|-------|------|-------------|
| title | string | Song title |
| artist | string | Artist name |
| album | string | Album name (optional) |
| path | string | File path for local .lrc matching (optional) |
| offset | int | Pagination offset (optional) |
| limit | int | Page size, default 10 (optional) |

Returns: Raw LRC text (Content-Type: text/plain). HTTP 404 if not found.

### GET /jsonapi - Fetch lyrics (JSON, v1.1.6+)

Returns JSON array: [{id, title, artist, lyrics}, ...]

### POST /lyrics/confirm - Confirm lyrics

JSON body: {path, title, artist, album, lyrics, lyricsId}
Returns 20x on success.

### Stream Music App Config
Set custom lyrics API URL to: http://YOUR_IP:4091/lyrics
## Web Manager (port 4092)

Open http://YOUR_IP:4092 in browser.

| Action | Description |
|--------|-------------|
| Browse | Paginated list, 20 per page |
| Search | Fuzzy search by title or artist |
| Upload | Drag-and-drop .lrc / .txt files |
| View | Modal popup with full lyrics |
| Delete | Remove from database |

## Deploy as System Service

systemctl enable --now lyrics-api.service
systemctl enable --now lyrics-manager.service

## Project Structure

api/
  lyrics_api.py        Lyrics API (port 4091)
  lyrics_manager.py    Web Manager (port 4092)
  import_lyrics.py     Bulk import script
  requirements.txt     Python dependencies
  start.sh            Quick start script
  README.md           This file
  docs/
    API.md            Detailed API docs

## License

MIT License

## Credits

- [Stream Music](https://github.com/gitbobobo/StreamMusic)
- [LrcApi](https://github.com/HisAtri/LrcApi)