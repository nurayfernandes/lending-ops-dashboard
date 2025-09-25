from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


def forecast_series_stub(series: pd.Series, horizon: int = 14) -> pd.DataFrame:
    """Stub simples: média móvel + tendência linear.
    Retorna DataFrame com colunas [ds, y, yhat].
    """
    s = series.dropna().astype(float)
    if s.empty:
        return pd.DataFrame({"ds": [], "y": [], "yhat": []})

    s = s.asfreq("D").interpolate()
    y = s.values
    x = np.arange(len(y))
    # ajuste linear
    A = np.vstack([x, np.ones(len(x))]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    # média móvel simples
    ma = pd.Series(y).rolling(window=min(7, max(1, len(y)//4))).mean().bfill().values
    yhat_in = (ma + (slope * x + intercept)) / 2

    # forecast
    future_x = np.arange(len(y), len(y) + horizon)
    future_trend = slope * future_x + intercept
    future_ma = np.full(horizon, ma[-1])
    yhat_future = (future_trend + future_ma) / 2

    idx = s.index
    future_idx = pd.date_range(idx[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")

    df_in = pd.DataFrame({"ds": idx, "y": y, "yhat": yhat_in})
    df_future = pd.DataFrame({"ds": future_idx, "y": np.nan, "yhat": yhat_future})
    return pd.concat([df_in, df_future], ignore_index=True)


def score_conversion_propensity_stub(X: pd.DataFrame, y: pd.Series) -> np.ndarray:
    """Treina rapidamente um classificador logístico e retorna probabilidades positivas.
    Se y não for fornecido completo, usa rótulos binários simples com base em mediana.
    """
    if y is None or y.isna().all():
        y = (X.mean(axis=1) > X.mean(axis=1).median()).astype(int)
    model = make_pipeline(StandardScaler(with_mean=False), LogisticRegression(max_iter=200))
    model.fit(X.fillna(0.0), y)
    return model.predict_proba(X.fillna(0.0))[:, 1]


