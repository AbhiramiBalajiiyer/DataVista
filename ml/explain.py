import shap
import matplotlib.pyplot as plt
import pandas as pd
import os

class ShapExplainer:
    """
    Unified SHAP explainer used by InsightOps ML module.
    Produces saved image files instead of blocking visualizations.
    """

    def __init__(self, model):
        self.model = model

    def _ensure_dir(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def summary_plot(self, X: pd.DataFrame, path="assets/shap_summary.png"):
        """Generate a SHAP summary bar plot and save it."""
        self._ensure_dir(path)

        explainer = shap.Explainer(self.model, X)
        shap_values = explainer(X)

        plt.figure(figsize=(8, 6))
        shap.plots.bar(shap_values.mean(0), show=False)

        plt.tight_layout()
        plt.savefig(path)
        plt.close()

        return path

    def full_summary(self, X: pd.DataFrame, path="assets/shap_full_summary.png"):
        """A full beeswarm summary plot (like your original file)."""
        self._ensure_dir(path)

        explainer = shap.Explainer(self.model, X)
        shap_values = explainer(X)

        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X, show=False)
        plt.savefig(path, bbox_inches="tight")
        plt.close()

        return path

    def force_plot(self, X: pd.DataFrame, row_idx: int, path="assets/shap_force.png"):
        """Generate a force plot for a specific row."""
        self._ensure_dir(path)

        explainer = shap.Explainer(self.model, X)
        shap_values = explainer(X)

        shap.plots.force(shap_values[row_idx], matplotlib=True, show=False)
        plt.savefig(path)
        plt.close()

        return path
