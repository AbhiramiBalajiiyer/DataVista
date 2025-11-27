import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score

class ModelTrainer:
    def __init__(self, df: pd.DataFrame, target: str):
        self.df = df.copy()
        self.target = target

    def quick_compare(self):
        # Only numeric + fill missing
        X = self.df.drop(columns=[self.target]).select_dtypes(include="number").fillna(0)
        y = self.df[self.target].fillna(0)

        models = {
            "LinearRegression": LinearRegression(),
            "RandomForest": RandomForestRegressor(n_estimators=60, random_state=42),
        }

        results = {}
        for name, model in models.items():
            try:
                score = cross_val_score(model, X, y, cv=3, scoring="r2").mean()
            except Exception:
                score = None
            results[name] = score

        return results

    def train(self, model_type="rf"):
        X = self.df.drop(columns=[self.target]).select_dtypes(include="number").fillna(0)
        y = self.df[self.target].fillna(0)

        if model_type == "linear":
            model = LinearRegression()
            name = "linear"
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            name = "rf"

        model.fit(X, y)

        os.makedirs("ml/model_store", exist_ok=True)
        path = f"ml/model_store/{name}.pkl"
        joblib.dump(model, path)

        return model, path
