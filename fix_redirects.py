import time
from selenium import webdriver
driver = webdriver.Chrome()

def load_failed_ids():
    FAILED_IDS = []
    with open('data/failed_urls.txt', encoding='utf-8') as f:
        for line in f:
            if line.strip() == '' or line.startswith('#'):
                continue
            FAILED_IDS.append(line.strip())
    return set(FAILED_IDS)


def is_redirect(failed_id):
    print(f"チェック中: {failed_id}")
    driver.get(f"https://music.youtube.com/watch?v={failed_id}")
    time.sleep(3)
    redirected_id = driver.current_url.split("=")[1]

    if failed_id not in redirected_id:
        return True, redirected_id
    else:
        return False, None

for failed_id in load_failed_ids():
    redirected, new_id = is_redirect(failed_id)
    if redirected == True:
        with open('data/urls.txt', 'a', encoding='utf-8') as f:
                    print(f"書き込み中: {new_id}")
                    f.write(f"https://music.youtube.com/watch?v={new_id}" + '\n')
    else:
        print(f"Falseでした")