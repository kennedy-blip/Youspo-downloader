import yt_dlp
import os

def get_youtube_info(url):
    """Metadata fetcher with strict Render Secret Pathing and Port logs."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Render stores 'Secret Files' in /etc/secrets/
    render_secret = '/etc/secrets/youtube_cookies.txt'
    local_secret = os.path.join(project_root, 'cookies.txt')
    
    cookies_path = render_secret if os.path.exists(render_secret) else local_secret
    
    # THIS LOG IS CRITICAL: Check your Render logs for this line!
    if os.path.exists(cookies_path):
        print(f"--- [YouTube Handler] Cookie file FOUND at: {cookies_path} ---")
    else:
        print(f"--- [YouTube Handler] WARNING: No cookies found. Looking in: {cookies_path} ---")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
        # Updated User-Agent to look like a modern browser
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
        'source_address': '0.0.0.0', # Forces IPv4 (YouTube blocks many Cloud IPv6 ranges)
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            thumbnails = info.get('thumbnails', [])
            return {
                'title': info.get('title', 'Unknown Video'),
                'thumbnail': thumbnails[-1]['url'] if thumbnails else "",
                'link': url
            }
        except Exception as e:
            print(f"--- [YouTube Handler] Error fetching metadata: {str(e)} ---")
            return None

def download_youtube_media(url, format_type):
    """Downloader using same cookie logic."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, 'static', 'downloads')
    
    render_secret = '/etc/secrets/youtube_cookies.txt'
    local_secret = os.path.join(project_root, 'cookies.txt')
    cookies_path = render_secret if os.path.exists(render_secret) else local_secret

    if not os.path.exists(output_dir): 
        os.makedirs(output_dir)

    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'ffmpeg_location': project_root,
        'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'source_address': '0.0.0.0',
        'nocheckcertificate': True,
    }

    if format_type == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts.update({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
            'merge_output_format': 'mp4'
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format_type == 'mp3': 
                filename = os.path.splitext(filename)[0] + '.mp3'
            return os.path.basename(filename), None
    except Exception as e:
        print(f"--- [YouTube Handler] Download Error: {str(e)} ---")
        return None, str(e)