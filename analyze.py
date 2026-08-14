import glob
import os
import librosa
import numpy as np
import pandas as pd

def extract_features(file_path):
    print(f"解析中: {file_path}")

    # 音声データの読み込み
    y, sr = librosa.load(file_path)
    duration = len(y) / sr # 曲の長さ（秒）

    # 1. これまでの基本特徴量
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(tempo.item())
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))

    # 2. 音数密度（1秒間に音が何回鳴ったか＝ぎっしり度）
    onsets = librosa.onset.onset_detect(y=y, sr=sr)
    onset_density = len(onsets) / duration

    # 3. 最初にサビ級の音圧（全体の7割以上のデカさ）に達した秒数
    rms = librosa.feature.rms(y=y)[0]
    max_rms = np.max(rms)

    # 最大音圧の 75% を超えるフレーム（時間）を全抽出
    high_volume_frames = np.where(rms >= max_rms * 0.75)[0]

    # その「一番最初」の時間を取得
    if len(high_volume_frames) > 0:
        first_peak_frame = high_volume_frames[0]
        first_peak_time = float(librosa.frames_to_time(first_peak_frame, sr=sr))
    else:
        first_peak_time = 0.0

    # 特徴量をまとめる「辞書」
    features = {
        'bpm': round(bpm, 2),
        'centroid': round(centroid, 2),
        'rolloff': round(rolloff, 2),
        'onset_density': round(onset_density, 2), # 高いほど音が詰まっている
        'first_peak_time': round(first_peak_time, 2) # 低いほどすぐ盛り上がる
    }

    return features
    
all_data = []

for f in glob.glob("data/*.wav"):
    feat = extract_features(f)
    feat["song_name"] = os.path.basename(f)
    all_data.append(feat)

df = pd.DataFrame(all_data)
print("\n=== 全曲の特徴量一覧 ===")
print(df)