import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import mlflow
from datetime import datetime
from typing import Tuple, List
from repositories.ai_repo import AIRepository
from models.dto.ai_dto import CustomerCluster

class ClusteringService:
    @staticmethod
    async def segment_customers() -> Tuple[List[CustomerCluster], float]:
        customers = await AIRepository.get_active_customers()
        
        if len(customers) < 3:
            return [], 0.0 # Not enough data for 3 clusters
            
        rfm_data = []
        now = datetime.now()
        
        for c in customers:
            last_visit = c.get("last_visit")
            if isinstance(last_visit, str):
                try:
                    last_visit = datetime.fromisoformat(last_visit.replace("Z", "+00:00")).replace(tzinfo=None)
                except ValueError:
                    last_visit = now
            elif not last_visit:
                last_visit = now
                
            recency = (now - last_visit).days
            rfm_data.append({
                "customer_id": str(c["_id"]),
                "name": c.get("name", "Unknown"),
                "phone": c.get("phone", ""),
                "recency": max(recency, 0),
                "frequency": c.get("visit_count", 0),
                "monetary": c.get("total_spend", 0)
            })
            
        df = pd.DataFrame(rfm_data)
        features = df[['recency', 'frequency', 'monetary']]
        
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        n_clusters = min(3, len(df))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(scaled_features)
        
        sil_score = 0.0
        if len(df) > 3:
            sil_score = silhouette_score(scaled_features, df['cluster'])
            
        try:
            with mlflow.start_run(run_name="rfm_clustering"):
                mlflow.log_param("n_clusters", n_clusters)
                mlflow.log_param("model", "KMeans")
                mlflow.log_metric("silhouette_score", sil_score)
        except Exception as e:
            print(f"Warning: MLflow tracking failed: {e}")
            
        # Map clusters to meaningful names
        cluster_means = df.groupby('cluster')[['recency', 'frequency', 'monetary']].mean()
        
        sultan_cluster = cluster_means['monetary'].idxmax()
        remaining_clusters = [c for c in range(n_clusters) if c != sultan_cluster]
        at_risk_cluster = cluster_means.loc[remaining_clusters, 'recency'].idxmax() if remaining_clusters else -1
        reguler_cluster = [c for c in remaining_clusters if c != at_risk_cluster][0] if len(remaining_clusters) > 1 else -1
        
        cluster_labels = {}
        cluster_labels[sultan_cluster] = "Sultan VIP 👑"
        if at_risk_cluster != -1:
            cluster_labels[at_risk_cluster] = "Berisiko Pergi ⚠️"
        if reguler_cluster != -1:
            cluster_labels[reguler_cluster] = "Reguler ⚖️"
            
        results = []
        for _, row in df.iterrows():
            label = cluster_labels.get(row['cluster'], "Reguler ⚖️")
            results.append(CustomerCluster(
                customer_id=row['customer_id'],
                name=row['name'],
                phone=row['phone'],
                recency_days=int(row['recency']),
                frequency_count=int(row['frequency']),
                monetary_value=int(row['monetary']),
                cluster_label=label
            ))
                
        return results, round(sil_score, 3)
