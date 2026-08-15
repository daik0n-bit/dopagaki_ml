import glob
import os
import unicodedata
from itertools import combinations

from rapidfuzz import fuzz

# "audio" or "audio_labeled"
AUDIO_DIR = "data/audio_labeled"

SIMILARITY_THRESHOLD = 90  # これ以上似てたら「怪しい候補」として警告する

def normalize(name):
    """全角/半角の表記ゆれを統一する"""
    return unicodedata.normalize('NFKC', name)


def extract_song_title(name):
    """ファイル名からアーティスト名を除いた曲名部分だけを取り出す"""
    name = name.replace('.wav', '')
    parts = name.split('_', 1)
    if len(parts) == 2:
        return parts[1]
    return parts[0]


def find_exact_duplicates(files):
    """正規化した結果が完全一致するものを探す"""
    groups = {}
    for f in files:
        name = os.path.basename(f)
        key = normalize(name)
        groups.setdefault(key, []).append(name)

    duplicates = {k: v for k, v in groups.items() if len(v) > 1}
    return duplicates


def find_similar_pairs(files):
    """完全一致はしないが、曲名部分が似ているペアを探す"""
    names = [os.path.basename(f) for f in files]
    similar_pairs = []

    for name_a, name_b in combinations(names, 2):
        title_a = extract_song_title(normalize(name_a))
        title_b = extract_song_title(normalize(name_b))
        score = fuzz.ratio(title_a, title_b)
        if score >= SIMILARITY_THRESHOLD:
            similar_pairs.append((name_a, name_b, score))

    return similar_pairs


def remove_exact_duplicates(duplicates, audio_dir=AUDIO_DIR):
    """完全一致の重複について、2番目以降を自動削除する"""
    removed = []
    for key, names in duplicates.items():
        # 1つ目(names[0])は残す。2つ目以降を削除
        for name in names[1:]:
            path = os.path.join(audio_dir, name)
            os.remove(path)
            removed.append(name)
    return removed


if __name__ == "__main__":
    files = glob.glob(f"{AUDIO_DIR}/*.wav")
    print(f"対象曲数: {len(files)}")

    # --- 完全一致(全角半角の違いのみ)の重複 ---
    exact_dupes = find_exact_duplicates(files)
    if exact_dupes:
        print("\n=== 完全一致の重複(自動削除します) ===")
        for key, names in exact_dupes.items():
            print(f"- 残す: {names[0]}")
            for extra in names[1:]:
                print(f"  削除: {extra}")

        removed = remove_exact_duplicates(exact_dupes)
        print(f"\n{len(removed)}件削除しました。")
    else:
        print("\n完全一致の重複はありませんでした。")

    # --- 似ている曲名のペア(要目視確認、削除はしない) ---
    files = glob.glob(f"{AUDIO_DIR}/*.wav")  # 削除後の最新一覧で再取得
    similar = find_similar_pairs(files)
    if similar:
        print(f"\n=== 曲名が似ているペア(類似度{SIMILARITY_THRESHOLD}%以上、手動確認してください) ===")
        for a, b, score in sorted(similar, key=lambda x: -x[2]):
            print(f"- {score:.1f}% : {a}  <->  {b}")
    else:
        print("\n曲名が似ているペアはありませんでした。")