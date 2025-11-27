import pandas as pd
import joblib
from ml.trainer import ModelTrainer
from ml.explain import ShapExplainer

class MLTrainerAgent:
    def __init__(self):
        self.df = None
        self.target = None
        self.model = None
        self.path = None
        self.explainer = None

    def receive_data(self, df):
        self.df = df

    def set_target(self, target):
        if target not in self.df.columns:
            raise ValueError(f"Target '{target}' not found.")
        self.target = target

    def quick_compare(self):
        trainer = ModelTrainer(self.df, self.target)
        return trainer.quick_compare()

    def train(self, model_type="rf"):
        trainer = ModelTrainer(self.df, self.target)
        self.model, self.path = trainer.train(model_type)
        return f"Model trained and saved to {self.path}"

    def predict(self, row: dict):
        if not self.model:
            self.model = joblib.load(self.path)

        df = pd.DataFrame([row])
        return self.model.predict(df)[0]

    def shap_summary(self):
        dfX = self.df.drop(columns=[self.target])
        self.explainer = ShapExplainer(self.model)
        return self.explainer.summary_plot(dfX)

    def shap_force(self, row_idx):
        dfX = self.df.drop(columns=[self.target])
        return self.explainer.force_plot(dfX, row_idx)
