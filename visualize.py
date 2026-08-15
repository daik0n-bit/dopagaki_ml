import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# --- CSV読み込み ---
df = pd.read_csv("data/meta/features.csv")

# --- PCA解析 ---
feature_cols = [
    "centroid",
    "rolloff",
    "onset_density",
    "first_peak_time",
    "dynamics_std",
    "key_change_score"
]
X = df[feature_cols]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=2)
pca_result = pca.fit_transform(X_scaled)

loadings = pd.DataFrame(
    pca.components_.T,
    columns=["PC1", "PC2"],
    index=feature_cols
)
print(loadings)

from sklearn.cluster import KMeans

n_clusters = 5  # まず5グループに分けてみる
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
df["cluster"] = kmeans.fit_predict(X_scaled)

df["PC1"] = pca_result[:, 0]
df["PC2"] = pca_result[:, 1]

# --- インタラクティブな散布図 ---
fig = px.scatter(
    df,
    x="PC1",
    y="PC2",
    color="cluster",
    hover_name="song_name",
    title="Music Map (PCA 2D + KMeans)",
)
fig.show()