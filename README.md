# Music Playlist Manager

A simple, responsive Flask + SQLite web app to organize songs and playlists.

## Features
- Add songs with title, artist, and album
- Create playlists with descriptions
- Assign songs to playlists and move songs between playlists
- Search songs by title, artist, or album
- Delete songs and playlists
- SQLite database created automatically
- Render deployment configuration included

## Run locally
Python 3.10+ is recommended.

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\\Scripts\\activate

pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Deploy to Render using GitHub
1. Extract this ZIP file.
2. Create a new GitHub repository.
3. Upload the **contents** of the `Music_Playlist_Manager` folder (so `app.py`, `requirements.txt`, `render.yaml`, etc. are at the repository root).
4. In Render, choose **New + → Blueprint** and connect your GitHub repository, or create a **New Web Service** from the repository.
5. If creating a Web Service manually, use:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
6. Deploy. Open the generated Render URL.

## Important database note
SQLite is used by default and the app works without extra configuration. Files on Render's free web services are ephemeral, so database changes may be lost when the service restarts or redeploys. For durable production data, use a persistent disk (where available) and set `DATABASE_PATH` to a path on that disk, or migrate to a managed PostgreSQL database.

## Security note
Render generates a `SECRET_KEY` from `render.yaml`. When running locally, the app has a development fallback key. This starter app does not include user accounts or private per-user libraries; it is intended as a personal/demo project.
