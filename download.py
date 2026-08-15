import yt_dlp
import imageio_ffmpeg
import spotdl

class MyLogger:
    def __init__(self):
        self.error_count = 0

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        self.error_count += 1
        print(f"チェック中: {msg}")
        print(f"今の数: {self.error_count}")
        if "[youtube]" not in msg:
            return
        video_id = msg.split(":")[1].split(" ")[2]
        with open('data/meta/failed_urls.txt', 'a', encoding='utf-8') as f:
            f.write(video_id + '\n')

def my_hook(d):
    print(d)

def download_audio(urls):
    with open('data/meta/failed_urls.txt', 'w', encoding='utf-8') as f:
        pass

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'data/audio/%(uploader)s_%(title)s.%(ext)s',
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
        'logger': MyLogger(),
        'ignoreerrors': True,
        'sleep_interval': 3,   # 最低3秒待つ
        'max_sleep_interval': 8,  # 最大8秒待つ（ランダムでこの間の秒数になる）
        'download_archive': 'data/meta/downloaded.txt',
        'progress_hooks': [my_hook],
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
    with open('data/meta/urls.txt', encoding='utf-8') as f:
        for line in f:
            if line.strip() == '' or line.startswith('#'):
                continue
            URLS.append(line.strip())
    return URLS

def backup_and_clear_urls():

    with open('data/meta/urls.txt', encoding='utf-8') as f:
        content = f.read()

    with open('data/meta/urls_done.txt', "a", encoding='utf-8') as f:
        f.write(content)

    with open('data/meta/urls.txt', 'w', encoding='utf-8') as f:
        pass

# ダウンロード

download_audio(load_urls())
backup_and_clear_urls()