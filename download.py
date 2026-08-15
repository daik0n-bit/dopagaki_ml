import yt_dlp
import imageio_ffmpeg
import spotdl

class MyLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(f"チェック中: {msg}")
        if "[youtube]" not in msg:
            return
        video_id = msg.split(":")[1].split(" ")[2]
        with open('data/failed_urls.txt', 'a', encoding='utf-8') as f:
            f.write(video_id + '\n')

def download_audio(urls):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'data/%(uploader)s_%(title)s.%(ext)s',
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
        'logger': MyLogger(),
        'ignoreerrors': True,
        'sleep_interval': 3,   # 最低3秒待つ
        'max_sleep_interval': 8,  # 最大8秒待つ（ランダムでこの間の秒数になる）
        'download_archive': 'data/downloaded.txt',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'extractor_args': {
            'youtube': {
                'player_client': ['web', 'mweb', 'ios', 'android']
            }
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(urls)

def load_urls():
    URLS = []
    with open('data/urls.txt', encoding='utf-8') as f:
        for line in f:
            if line.strip() == '' or line.startswith('#'):
                continue
            URLS.append(line.strip())
    return URLS

# ダウンロード

download_audio(load_urls())