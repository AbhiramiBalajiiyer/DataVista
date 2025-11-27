class EDAAgent:
    def __init__(self):
        self.data = None

    def receive_data(self, df):
        self.data = df

    def handle(self, task):
        """Retry analyze() up to 3 times."""
        for attempt in range(3):
            try:
                out = self.analyze()
                if "error" not in out:
                    return out
            except Exception:
                pass
        return {"error": "EDA failed after 3 attempts."}

    def analyze(self):
        df = self.data
        if df is None:
            return {"error": "No data"}

        # --------------------------
        # 1. Descriptive statistics
        # --------------------------
        try:
            stats_dict = df.describe(include="all").fillna("").to_dict()
        except:
            stats_dict = {}

        # --------------------------
        # 2. Sample of dataset
        # --------------------------
        df_sample = df.head(10)

        # --------------------------
        # 3. Insights Summary
        # --------------------------
        insights = []

        # Basic shape
        insights.append(f"Dataset contains {df.shape[0]} rows and {df.shape[1]} columns.")

        # Missing values
        missing = df.isna().sum()
        if missing.sum() > 0:
            top_missing = missing.sort_values(ascending=False).head(5)
            miss_txt = ", ".join([f"{idx}: {val}" for idx, val in top_missing.items()])
            insights.append(f"Columns with missing data: {miss_txt}")

        # Numeric columns: variance check
        num_cols = df.select_dtypes(include="number").columns
        if len(num_cols) > 0:
            var_cols = df[num_cols].var().sort_values(ascending=False)
            insights.append(f"Highest variance column: {var_cols.index[0]}")

        # Categorical columns
        cat_cols = df.select_dtypes(include="object").columns
        if len(cat_cols) > 0:
            insights.append(f"Categorical columns detected: {', '.join(cat_cols[:5])}")

        # Join insights
        summary_text = "\n".join(insights)

        # --------------------------
        # Return final structured output
        # --------------------------
        return {
            "data": df_sample,
            "stats": stats_dict,
            "insights": summary_text
        }
