from fastapi import APIRouter, HTTPException
from datetime import datetime
from models.dto.ai_dto import (
    StockoutPredictionResponse,
    CustomerClusterResponse,
    SendPromoRequest,
    SendPromoResponse
)
from services.forecasting_service import ForecastingService
from services.clustering_service import ClusteringService
from services.wa_service import WhatsAppService

router = APIRouter(prefix="/ai", tags=["AI Engine"])

@router.get("/forecasting/stockouts", response_model=StockoutPredictionResponse)
async def get_stockout_predictions(store_id: str = None):
    try:
        predictions = await ForecastingService.predict_stockouts(store_id=store_id)
        return StockoutPredictionResponse(
            predictions=predictions,
            generated_at=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/clustering/customers", response_model=CustomerClusterResponse)
async def get_customer_clusters():
    try:
        clusters, score = await ClusteringService.segment_customers()
        return CustomerClusterResponse(
            clusters=clusters,
            silhouette_score=score,
            generated_at=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/promo/send", response_model=SendPromoResponse)
async def send_promo_to_cluster(req: SendPromoRequest):
    try:
        # Get clusters first
        clusters, _ = await ClusteringService.segment_customers()
        # Filter by label
        target_customers = [c for c in clusters if c.cluster_label == req.cluster_label]
        
        if not target_customers:
            return SendPromoResponse(status="No customers found in this cluster", messages_sent=0)
            
        sent_count = await WhatsAppService.send_promo_to_segment(target_customers, req.message_template)
        
        return SendPromoResponse(status="Success", messages_sent=sent_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
