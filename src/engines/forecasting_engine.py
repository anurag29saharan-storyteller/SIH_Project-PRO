"""
Trend & Risk Forecasting Engine.
Uses Prophet when available, with automatic fallback to Statsmodels Exponential Smoothing
or Linear-Polynomial extrapolation to project forward weekly SIF risk score trajectories.
"""
import pandas as pd
import numpy as np
from datetime import timedelta
from typing import List, Dict, Any, Optional
from src.domain.schemas import ForecastPoint
from src.utils.logger import get_logger

logger = get_logger("forecasting_engine")


class TrendForecastingEngine:
    def __init__(self):
        pass

    def forecast_risk_trend(self, df: pd.DataFrame, forecast_days: int = 14) -> List[ForecastPoint]:
        """
        Forecasts forward SIF risk scores using historical report data.
        Returns a list of daily/weekly ForecastPoint schemas.
        """
        if df.empty or "Date" not in df.columns or "Risk_Score" not in df.columns:
            return []

        try:
            data = df.copy()
            data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
            data = data.dropna(subset=["Date"]).sort_values("Date")
            
            if len(data) < 5:
                return []

            # Resample by 3-day or daily average
            ts = data.set_index("Date")["Risk_Score"].resample("3D").mean().interpolate(method="linear").reset_index()
            ts.columns = ["ds", "y"]

            if len(ts) < 4:
                return []

            # Try Prophet First
            try:
                from prophet import Prophet
                m = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=False, interval_width=0.90)
                m.fit(ts)
                future = m.make_future_dataframe(periods=max(4, forecast_days // 3), freq="3D")
                forecast = m.predict(future)
                future_slice = forecast.iloc[-max(4, forecast_days // 3):]
                
                results = []
                for _, row in future_slice.iterrows():
                    pred = max(5.0, min(98.0, float(row["yhat"])))
                    lower = max(0.0, min(95.0, float(row["yhat_lower"])))
                    upper = max(pred, min(100.0, float(row["yhat_upper"])))
                    results.append(ForecastPoint(
                        date=row["ds"].strftime("%Y-%m-%d"),
                        predicted_score=round(pred, 1),
                        lower_bound=round(lower, 1),
                        upper_bound=round(upper, 1),
                        is_anomaly=pred >= 80.0
                    ))
                return results

            except Exception as prop_err:
                logger.info(f"Prophet not used ({prop_err}). Utilizing Statsmodels / Poly trend fallback.")

            # Statsmodels Holt-Winters / Exponential Smoothing Fallback
            try:
                from statsmodels.tsa.holtwinters import ExponentialSmoothing
                model = ExponentialSmoothing(ts["y"], trend="add", seasonal=None, initialization_method="estimated").fit()
                steps = max(4, forecast_days // 3)
                preds = model.forecast(steps)
                
                last_date = ts["ds"].max()
                results = []
                for i, pred_val in enumerate(preds):
                    fdate = last_date + timedelta(days=3 * (i + 1))
                    val = max(5.0, min(98.0, float(pred_val)))
                    results.append(ForecastPoint(
                        date=fdate.strftime("%Y-%m-%d"),
                        predicted_score=round(val, 1),
                        lower_bound=round(max(0.0, val - 12.0), 1),
                        upper_bound=round(min(100.0, val + 12.0), 1),
                        is_anomaly=val >= 80.0
                    ))
                return results

            except Exception as stats_err:
                logger.info(f"Statsmodels fallback used basic moving regression ({stats_err}).")

            # Final Simple Linear Moving Trend Fallback
            last_val = float(ts["y"].iloc[-3:].mean())
            trend_slope = float((ts["y"].iloc[-1] - ts["y"].iloc[0]) / max(1, len(ts)))
            last_date = ts["ds"].max()
            results = []
            steps = max(4, forecast_days // 3)
            for i in range(steps):
                fdate = last_date + timedelta(days=3 * (i + 1))
                val = max(10.0, min(95.0, last_val + trend_slope * (i + 1)))
                results.append(ForecastPoint(
                    date=fdate.strftime("%Y-%m-%d"),
                    predicted_score=round(val, 1),
                    lower_bound=round(max(0.0, val - 15.0), 1),
                    upper_bound=round(min(100.0, val + 15.0), 1),
                    is_anomaly=val >= 80.0
                ))
            return results

        except Exception as e:
            logger.error(f"Error in forecasting engine: {e}")
            return []
