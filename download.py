import yt_dlp
import imageio_ffmpeg

def download_audio(urls):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'data/%(uploader)s_%(title)s.%(ext)s',
        'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{
            # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb', 'ios', 'android']
            }
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(urls)

# ダウンロード
URLS = [
    'https://music.youtube.com/watch?v=dY5Vkuo-QRo&si=53cG3QYVVlp96CLf',
    'https://music.youtube.com/watch?v=FDMpW6a8jq4&si=2pqAgyNp-CumWrq5',
    'https://music.youtube.com/watch?v=0T-BCIFeqq8&si=GLrjqizYaPDYQtb4',
    'https://music.youtube.com/watch?v=GieQq3eWSnE&si=zQJvqFSdkYl128y0',
    'https://music.youtube.com/watch?v=4tlUwgtgdZA&si=D3YA8r149VCircHy',
    'https://music.youtube.com/watch?v=m9SMT5ipbxk&si=lsq3rRzh6eDKDdKw',
    'https://music.youtube.com/watch?v=9mWbCPJuoIo&si=Q7qGC6Rr2tIHePrJ',
    'https://music.youtube.com/watch?v=DO_aopUeFnw&si=XCQjDBSHFNTX-yb1',
    'https://music.youtube.com/watch?v=hXyuJ4BDXeA&si=h_HKr6XM_-uIxl92',
    'https://music.youtube.com/watch?v=wggigwtz4dQ&si=te3_cAwev_8_3G-D'
]

download_audio(URLS)