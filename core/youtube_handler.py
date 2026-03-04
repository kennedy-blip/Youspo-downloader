import yt_dlp
import os
import platform

def get_youtube_info(url):
    """Fetches metadata for preview."""
    ydl_opts = {
        'quiet': True, 
        'no_warnings': True,
        'extract_flat': True 
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
    """Downloads media using the appropriate FFmpeg for the OS."""
    # 1. Setup Paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    output_dir = os.path.join(project_root, 'static', 'downloads')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 2. Configure yt-dlp options
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'quiet': False,
        'no_warnings': False,
        # Looks in project root for ffmpeg (.exe on Windows, binary on Linux)
        'ffmpeg_location': project_root, 
    }

    # 3. Format Logic
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

    # 4. Execute
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if format_type == 'mp3':
                filename = os.path.splitext(filename)[0] + '.mp3'
                
            return os.path.basename(filename), None
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if 'ffmpeg' in error_msg.lower():
            return None, "System error: FFmpeg engine not found. Contact Admin."
        return None, error_msg
    except Exception as e:
        return None, f"An unexpected error occurred: {str(e)}"