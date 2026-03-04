import yt_dlp
import os

def get_youtube_info(url):
    """Metadata fetcher with strict Render Secret Pathing."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Path 1: Render Secret File Location
    # Path 2: Local folder (for your PC testing)
    render_secret = '/etc/secrets/youtube_cookies.txt'
    local_secret = os.path.join(project_root, 'cookies.txt')
    
    cookies_path = render_secret if os.path.exists(render_secret) else local_secret
    
    # Debug print: This will show in Render Logs so we know it's working
    if os.path.exists(cookies_path):
        print(f"--- SUCCESS: Found cookies at {cookies_path} ---")
    else:
        print(f"--- WARNING: No cookies file found at {cookies_path} ---")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'nocheckcertificate': True,
        'source_address': '0.0.0.0', # Force IPv4
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
            print(f"CRITICAL ERROR: {e}")
            return None

def download_youtube_media(url, format_type):
    """Downloader with OS detection for FFmpeg."""
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
        return None, str(e)