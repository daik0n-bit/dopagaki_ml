import glob
import os
import librosa
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor

def extract_features(file_path):
    print(f"解析中: {file_path}")

    y, sr = librosa.load(file_path)
    duration = len(y) / sr

    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))

    # --- BPM検出(半分/倍問題があり信頼性が低いため一旦コメントアウト) ---
    # onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    # tempogram = librosa.feature.tempogram(onset_envelope=onset_env, sr=sr)
    # tempo_strength = tempogram.mean(axis=1)
    # tempo_bpms = librosa.tempo_frequencies(len(tempo_strength), sr=sr)
    #
    # mask = (tempo_bpms > 60) & (tempo_bpms < 200)
    # best_index = np.argmax(tempo_strength[mask])
    # best_bpm = tempo_bpms[mask][best_index]
    #
    # if best_bpm < 60 or best_bpm > 175:
    #     bpm_flag = True
    # else:
    #     bpm_flag = False

    onsets = librosa.onset.onset_detect(y=y, sr=sr)
    onset_density = len(onsets) / duration

    rms = librosa.feature.rms(y=y)[0]
    max_rms = np.max(rms)
    high_volume_frames = np.where(rms >= max_rms * 0.80)[0]
    if len(high_volume_frames) > 0:
        first_peak_frame = high_volume_frames[0]
        first_peak_time = float(librosa.frames_to_time(first_peak_frame, sr=sr))
    else:
        first_peak_time = 0.0

    # --- 展開の激しさ(音量の変化) ---
    n_sections = 4
    section_size = len(rms) // n_sections
    section_means = []
    for i in range(n_sections):
        start = i * section_size
        end = start + section_size
        section_means.append(np.mean(rms[start:end]))

    dynamics_std = float(np.std(section_means))

    # --- 転調の激しさ(キー・音の高さの分布の変化) ---
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

    chroma_section_size = chroma.shape[1] // n_sections
    chroma_section_means = []
    for i in range(n_sections):
        start = i * chroma_section_size
        end = start + chroma_section_size
        section_chroma = np.mean(chroma[:, start:end], axis=1)
        chroma_section_means.append(section_chroma)

    similarities = []
    for i in range(n_sections - 1):
        a = chroma_section_means[i]
        b = chroma_section_means[i + 1]
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a > 0 and norm_b > 0:
            sim = np.dot(a, b) / (norm_a * norm_b)
        else:
            sim = 1.0
        similarities.append(sim)

    key_change_score = float(1 - np.mean(similarities))

    features = {
        # 'best_bpm': round(best_bpm, 2),
        'centroid': round(centroid, 2),
        'rolloff': round(rolloff, 2),
        'onset_density': round(onset_density, 2),
        'first_peak_time': round(first_peak_time, 2),
        'dynamics_std': round(dynamics_std, 4),
        'key_change_score': round(key_change_score, 4),
        # 'bpm_flag': bpm_flag,
        'song_name': os.path.basename(file_path),
    }

    return features

def analyze(dir):
    if __name__ == "__main__":
        files = glob.glob(f"data/{dir}/*.wav")

        with ProcessPoolExecutor() as executor:
            all_data = list(executor.map(extract_features, files))

        df = pd.DataFrame(all_data)
        print("\n=== 全曲の特徴量一覧 ===")
        print(df)

        df.to_csv(f"data/meta/{dir}_features.csv", index=False, encoding="utf-8-sig")
        print(f"CSVに保存しました: data/meta/{dir}_features.csv")

# "audio" or "audio_labeled"
analyze("audio_labeled")