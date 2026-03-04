from flask import Flask, render_template, request, send_from_directory, flash
import os
from core.youtube_handler import get_youtube_info, download_youtube_media
from core.spotify_handler import get_spotify_artwork_no_api

app = Flask(__name__)
app.secret_key = 'youspo_secret_key' # Needed for flashing messages
DOWNLOAD_FOLDER = 'static/downloads'

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    error = None

    if request.method == 'POST':
        action = request.form.get('action')
        url = request.form.get('link')

        if action == 'fetch':
            if 'youtube.com' in url or 'youtu.be' in url:
                data = get_youtube_info(url)
                if data: data['source'] = 'youtube'
                else: error = "Could not fetch YouTube metadata."
            elif 'spotify.com' in url:
                img, title = get_spotify_artwork_no_api(url)
                if img:
                    data = {'title': title, 'thumbnail': img, 'source': 'spotify', 'link': url}
                else: error = "Could not fetch Spotify artwork."
            else:
                error = "Please enter a valid YouTube or Spotify link."

        elif action == 'download':
            fmt = request.form.get('format')
            filename, download_err = download_youtube_media(url, fmt)
            
            if download_err:
                error = download_err
            else:
                return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

    return render_template('index.html', data=data, error=error)

if __name__ == '__main__':
    app.run(debug=True)