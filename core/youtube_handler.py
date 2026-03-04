import yt_dlp
import os

def get_youtube_info(url):
    """Fetches metadata using high-compatibility settings for cloud servers."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cookies_path = os.path.join(project_root, 'cookies.txt')
    
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'extract_flat': True,
        # 1. Authentication & Security
        'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
        'nocheckcertificate': True,
        
        # 2. Browser Spoofing (Helps bypass Datacenter blocks)
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        
        # 3. Network Tweak (Forcing IPv4 as YouTube often blocks Cloud IPv6 ranges)
        'source_address': '0.0.0.0', 
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            thumbnails = info.get('thumbnails', [])
            # Grab the largest thumbnail available
            img_url = thumbnails[-1]['url'] if thumbnails else ""
            return {
                'title': info.get('title', 'Unknown Video'),
                'thumbnail': img_url,
                'link': url
            }
        except Exception as e:
            # This will appear in your Render "Logs" tab
            print(f"YDL Metadata Fetch Error: {e}")
            return None

def download_youtube_media(url, format_type):
    """Downloads media using cookies and local FFmpeg binaries."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(project_root, 'static', 'downloads')
    cookies_path = os.path.join(project_root, 'cookies.txt')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'ffmpeg_location': project_root, # Looks for 'ffmpeg.exe' (Win) or 'ffmpeg' (Linux)
        'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'source_address': '0.0.0.0',
        'nocheckcertificate': True,
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
    else: # mp4
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
        print(f"YDL Download Error: {e}")
        return None, str(e)