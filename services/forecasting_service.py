import pandas as pd
from datetime import datetime, timedelta
import mlflow
from typing import List
from repositories.ai_repo import AIRepository
from models.dto.ai_dto import StockoutPrediction

class ForecastingService:
    @staticmethod
    async def predict_stockouts() -> List[StockoutPrediction]:
        products = await AIRepository.get_active_products()
        transactions = await AIRepository.get_valid_transactions()
        
        if not products:
            return []
            
        # Create a mapping for products
        product_map = {str(p["_id"]): p for p in products}
        
        # Calculate daily burn rate (simple moving average over the last 30 days)
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        
        # Flatten transactions to get sales per product
        sales_data = []
        for tx in transactions:
            tx_date = tx.get("created_at")
            if isinstance(tx_date, str):
                try:
                    tx_date = datetime.fromisoformat(tx_date.replace("Z", "+00:00")).replace(tzinfo=None)
                except ValueError:
                    continue
            elif not tx_date:
                continue
            
            if tx_date >= thirty_days_ago:
                for item in tx.get("items", []):
                    sales_data.append({
                        "product_id": item["product_id"],
                        "quantity": item["quantity"],
                        "date": tx_date.date()
                    })
        
        predictions = []
        
        if sales_data:
            df = pd.DataFrame(sales_data)
            daily_sales = df.groupby('product_id')['quantity'].sum() / 30.0
        else:
            daily_sales = pd.Series()
            
        for p_id, product in product_map.items():
            current_stock = int(product.get("stock", 0))
            burn_rate = float(daily_sales.get(p_id, 0.0))
            
            # Default values if no sales
            days_until = 999
            pred_date = "Safe"
            
            if burn_rate > 0:
                days_until = int(current_stock / burn_rate)
                pred_date = (now + timedelta(days=days_until)).strftime("%Y-%m-%d")
                
            # We only want to alert if stock will run out in less than 7 days
            if days_until < 7 and current_stock > 0:
                predictions.append(StockoutPrediction(
                    product_id=p_id,
                    barcode=product.get("barcode", ""),
                    name=product.get("name", ""),
                    category=product.get("category", ""),
                    current_stock=current_stock,
                    daily_burn_rate=round(burn_rate, 2),
                    days_until_stockout=days_until,
                    predicted_stockout_date=pred_date
                ))
                
        try:
            with mlflow.start_run(run_name="stockout_prediction"):
                mlflow.log_param("model_type", "Simple Moving Average (30 days)")
                mlflow.log_metric("predictions_count", len(predictions))
        except Exception as e:
            print(f"Warning: MLflow tracking failed: {e}")
            
        return sorted(predictions, key=lambda x: x.days_until_stockout)
