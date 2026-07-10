from pydantic import BaseModel, Field
from typing import List, Optional

class StockoutPrediction(BaseModel):
    product_id: str
    barcode: str
    name: str
    category: str
    current_stock: int
    daily_burn_rate: float
    days_until_stockout: int
    predicted_stockout_date: str

class StockoutPredictionResponse(BaseModel):
    predictions: List[StockoutPrediction]
    generated_at: str

class CustomerCluster(BaseModel):
    customer_id: str
    name: str
    phone: str
    recency_days: int
    frequency_count: int
    monetary_value: int
    cluster_label: str # e.g., "Sultan VIP", "Reguler", "At-Risk"

class CustomerClusterResponse(BaseModel):
    clusters: List[CustomerCluster]
    silhouette_score: float
    generated_at: str

class SendPromoRequest(BaseModel):
    cluster_label: str # Send to all customers in this cluster
    message_template: str # e.g., "Halo {name}, dapatkan diskon spesial!"

class SendPromoResponse(BaseModel):
    status: str
    messages_sent: int
