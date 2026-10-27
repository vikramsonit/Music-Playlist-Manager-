import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import init_db, get_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-before-deploying")
init_db()

@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    db = get_db()
    if q:
        songs = db.execute("""
            SELECT songs.*, playlists.name AS playlist_name
            FROM songs LEFT JOIN playlists ON songs.playlist_id = playlists.id
            WHERE songs.title LIKE ? OR songs.artist LIKE ? OR songs.album LIKE ?
            ORDER BY songs.created_at DESC
        """, (f"%{q}%", f"%{q}%", f"%{q}%")).fetchall()
    else:
        songs = db.execute("""
            SELECT songs.*, playlists.name AS playlist_name
            FROM songs LEFT JOIN playlists ON songs.playlist_id = playlists.id
            ORDER BY songs.created_at DESC
        """).fetchall()
    playlists = db.execute("SELECT * FROM playlists ORDER BY name COLLATE NOCASE").fetchall()
    db.close()
    return render_template("index.html", songs=songs, playlists=playlists, q=q)

@app.route("/songs/add", methods=["POST"])
def add_song():
    title = request.form.get("title", "").strip()
    artist = request.form.get("artist", "").strip()
    album = request.form.get("album", "").strip()
    playlist_id = request.form.get("playlist_id") or None
    if not title or not artist:
        flash("Song title and artist are required.", "error")
        return redirect(url_for("index"))
    db = get_db()
    if playlist_id:
        exists = db.execute("SELECT id FROM playlists WHERE id = ?", (playlist_id,)).fetchone()
        if not exists:
            playlist_id = None
    db.execute("INSERT INTO songs (title, artist, album, playlist_id) VALUES (?, ?, ?, ?)",
               (title, artist, album, playlist_id))
    db.commit()
    db.close()
    flash("Song added to your library.", "success")
    return redirect(url_for("index"))

@app.route("/songs/<int:song_id>/delete", methods=["POST"])
def delete_song(song_id):
    db = get_db()
    db.execute("DELETE FROM songs WHERE id = ?", (song_id,))
    db.commit()
    db.close()
    flash("Song deleted.", "success")
    return redirect(url_for("index"))

@app.route("/playlists/add", methods=["POST"])
def add_playlist():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    if not name:
        flash("Please enter a playlist name.", "error")
        return redirect(url_for("index"))
    db = get_db()
    try:
        db.execute("INSERT INTO playlists (name, description) VALUES (?, ?)", (name, description))
        db.commit()
        flash("Playlist created.", "success")
    except Exception:
        flash("A playlist with that name already exists.", "error")
    finally:
        db.close()
    return redirect(url_for("index"))

@app.route("/playlists/<int:playlist_id>")
def playlist_detail(playlist_id):
    db = get_db()
    playlist = db.execute("SELECT * FROM playlists WHERE id = ?", (playlist_id,)).fetchone()
    if not playlist:
        db.close()
        flash("Playlist not found.", "error")
        return redirect(url_for("index"))
    songs = db.execute("SELECT * FROM songs WHERE playlist_id = ? ORDER BY created_at DESC",
                       (playlist_id,)).fetchall()
    all_playlists = db.execute("SELECT * FROM playlists ORDER BY name COLLATE NOCASE").fetchall()
    db.close()
    return render_template("playlist.html", playlist=playlist, songs=songs, playlists=all_playlists)

@app.route("/songs/<int:song_id>/move", methods=["POST"])
def move_song(song_id):
    playlist_id = request.form.get("playlist_id") or None
    db = get_db()
    if playlist_id and not db.execute("SELECT id FROM playlists WHERE id = ?", (playlist_id,)).fetchone():
        playlist_id = None
    db.execute("UPDATE songs SET playlist_id = ? WHERE id = ?", (playlist_id, song_id))
    db.commit()
    db.close()
    flash("Song playlist updated.", "success")
    return redirect(request.referrer or url_for("index"))

@app.route("/playlists/<int:playlist_id>/delete", methods=["POST"])
def delete_playlist(playlist_id):
    db = get_db()
    db.execute("UPDATE songs SET playlist_id = NULL WHERE playlist_id = ?", (playlist_id,))
    db.execute("DELETE FROM playlists WHERE id = ?", (playlist_id,))
    db.commit()
    db.close()
    flash("Playlist deleted. Songs were kept in your library.", "success")
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
