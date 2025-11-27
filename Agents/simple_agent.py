import pandas as pd

class SimpleDataAgent:
    def __init__(self):
        self.data = None

    def receive_data(self, df):
        self.data = df

    def analyze(self):
        df = self.data

        original_rows = len(df)
        df = df.drop_duplicates()
        cleaned_rows = len(df)

        missing = df.isna().sum().to_dict()
        stats = df.describe(include="all").to_dict()

        insights = f"""
        --- SIMPLE DATA INSIGHTS ---
        Rows after cleaning: {cleaned_rows}
        Removed duplicates: {original_rows-cleaned_rows}
        Columns: {list(df.columns)}
        Missing values: {missing}
        ----------------------------
        """

        return {"data": df, "stats": stats, "insights": insights}
