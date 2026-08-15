import yt_dlp
import imageio_ffmpeg

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

class ProgressHook:
    def __init__(self):
        self.success_count = 0

    def __call__(self, d):
        if d['status'] == 'finished':
            self.success_count += 1
            print(f"成功: {self.success_count}曲目 - {d['info_dict'].get('title')}")

def download_audio(urls, dir):
    with open('data/meta/failed_urls.txt', 'w', encoding='utf-8') as f:
        pass

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'data/{dir}/%(artist,uploader)s_%(track,title)s.%(ext)s',
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
        'logger': MyLogger(),
        'ignoreerrors': True,
        'sleep_interval': 3,   # 最低3秒待つ
        'max_sleep_interval': 8,  # 最大8秒待つ（ランダムでこの間の秒数になる）
        'download_archive': f'data/meta/downloaded_{dir}.txt',
        'progress_hooks': [ProgressHook()],
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

def backup_and_clear_urls(dir):

    with open('data/meta/urls.txt', encoding='utf-8') as f:
        content = f.read()

    with open(f'data/meta/{dir}_done.txt', "a", encoding='utf-8') as f:
        f.write("\n" + content)

    with open('data/meta/urls.txt', 'w', encoding='utf-8') as f:
        pass

# ダウンロード

# "audio" or "audio_labeled"
download_audio(load_urls(), "audio_labeled")

# "urls" or "urls_labeled"
backup_and_clear_urls("urls_labeled")