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
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
    #onsetを使ってBPMを調べる
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)
    tempo_strength = tempogram.mean(axis=1)
    tempo_bpms = librosa.tempo_frequencies(len(tempo_strength), sr=sr)

    mask = (tempo_bpms > 60) & (tempo_bpms < 200)
    best_index = np.argmax(tempo_strength[mask])
    best_bpm = tempo_bpms[mask][best_index]

    if best_bpm < 60 or best_bpm > 175:
        bpm_flag = True
    else:
        bpm_flag = False

    # 2. 音数密度（1秒間に音が何回鳴ったか＝ぎっしり度）
    onsets = librosa.onset.onset_detect(y=y, sr=sr)
    onset_density = len(onsets) / duration

    # 3. 最初にサビ級の音圧（全体の7割以上のデカさ）に達した秒数
    rms = librosa.feature.rms(y=y)[0]
    max_rms = np.max(rms)

    # 最大音圧の 75% を超えるフレーム（時間）を全抽出
    high_volume_frames = np.where(rms >= max_rms * 0.80)[0]

    # その「一番最初」の時間を取得
    if len(high_volume_frames) > 0:
        first_peak_frame = high_volume_frames[0]
        first_peak_time = float(librosa.frames_to_time(first_peak_frame, sr=sr))
    else:
        first_peak_time = 0.0

    # 特徴量をまとめる「辞書」
    features = {
        'best_bpm': round(best_bpm, 2),
        'centroid': round(centroid, 2),
        'rolloff': round(rolloff, 2),
        'onset_density': round(onset_density, 2), # 高いほど音が詰まっている
        'first_peak_time': round(first_peak_time, 2), # 低いほどすぐ盛り上がる
        'bpm_flag': bpm_flag,
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

import matplotlib.pyplot as plt
from matplotlib import font_manager
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --- 1. 設定の完全リセットとフォントの直接登録 ---
plt.rcdefaults()  # 過去のおかしな設定を全部消去！

# Windowsの「メイリオ」フォントを直接Matplotlibに登録する
font_path = "C:/Windows/Fonts/meiryo.ttc"
font_manager.fontManager.addfont(font_path)
font_name = font_manager.FontProperties(fname=font_path).get_name()

# 全体設定に適用
plt.rcParams["font.family"] = font_name
plt.rcParams["axes.unicode_minus"] = False  # マイナス記号の消滅防止

# --- 2. PCA解析 ---
feature_cols = [
    "best_bpm",
    "centroid",
    "rolloff",
    "onset_density",
    "first_peak_time",
]
X = df[feature_cols]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=2)
pca_result = pca.fit_transform(X_scaled)

# --- 3. 散布図の描画 ---
plt.figure(figsize=(10, 7))

for i in range(len(df)):
    x = pca_result[i, 0]
    y = pca_result[i, 1]
    name = df.iloc[i]["song_name"].replace(".wav", "")

    plt.scatter(x, y, color="blue", s=80, alpha=0.7)
    plt.annotate(
        name,
        (x, y),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=9,
    )

plt.title("Music Map (PCA 2D)")
plt.xlabel("PC1 (第一主成分 / ドパガキ度)")
plt.ylabel("PC2 (第二主成分 / 音色・アタック感)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.axhline(0, color="gray", linestyle="-", linewidth=0.8)
plt.axvline(0, color="gray", linestyle="-", linewidth=0.8)

plt.tight_layout()
plt.show()