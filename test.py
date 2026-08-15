class MyLogger:
    def error(self, msg):
        video_id = msg.split(": ")[0].split(" ")[1]
        with open('data/failed_urls.txt', 'a', encoding='utf-8') as f:
            f.write(video_id + '\n')