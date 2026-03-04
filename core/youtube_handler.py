import yt_dlp
import os

def get_youtube_info(url):
    """Fetches metadata using cookies if available."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cookies_path = os.path.join(project_root, 'cookies.txt')
    
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'extract_flat': True,
        'cookiefile': cookies_path if os.path.exists(cookies_path) else None
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            thumbnails = info.get('thumbnails', [])
            img_url = thumbnails[-1]['url'] if thumbnails else ""
            return {
                'title': info.get('title', 'Unknown Video'),
                'thumbnail': img_url,
                'link': url
            }
        except Exception as e:
            print(f"Metadata Error: {e}")
            return None

def download_youtube_media(url, format_type):
    """Downloads media using cookies and the correct FFmpeg for the OS."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, 'static', 'downloads')
    cookies_path = os.path.join(project_root, 'cookies.txt')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'ffmpeg_location': project_root,
        'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
        'quiet': False,
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
            'merge_output_format': 'mp4',
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