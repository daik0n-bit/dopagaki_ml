import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --- CSV読み込み ---
df = pd.read_csv("data/meta/features.csv")

# --- PCA解析 ---
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

df["PC1"] = pca_result[:, 0]
df["PC2"] = pca_result[:, 1]

# --- インタラクティブな散布図 ---
fig = px.scatter(
    df,
    x="PC1",
    y="PC2",
    hover_name="song_name",
    title="Music Map (PCA 2D)",
)
fig.show()