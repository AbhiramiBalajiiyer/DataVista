import matplotlib.pyplot as plt
import pandas as pd
import os

class ChartAgent:
    def __init__(self):
        self.df = None

    def _split_single_text_column(self, df):
        """
        If the DataFrame has exactly one column and that column (or its name)
        looks like a comma-separated header, split it into multiple columns.
        """
        if df.shape[1] != 1:
            return df

        col_name = df.columns[0]
        first_vals = df.iloc[:, 0].astype(str)

        # Heuristics: header-like column name OR first row contains commas
        if ("," in col_name) or (first_vals.str.contains(",").any()):
            # Determine header: if col_name contains commas, use that; else try to use first row as header
            if "," in col_name:
                new_cols = [c.strip() for c in col_name.split(",")]
                # If the header got folded into the column name, then data begins at first row
                new_df = df.iloc[:, 0].str.split(",", expand=True)
                new_df.columns = new_cols[: new_df.shape[1]]
                # If the header row is present as first row (duplicate), drop it if it equals header tokens
                # Check first row content
                first_row = new_df.iloc[0].astype(str).tolist()
                if all([a == b for a, b in zip(first_row, new_cols[: len(first_row)])]):
                    new_df = new_df.iloc[1:].reset_index(drop=True)
                return new_df
            else:
                # Use first row as header
                splitted = df.iloc[:, 0].str.split(",", expand=True)
                header = splitted.iloc[0].astype(str).tolist()
                new_df = splitted.iloc[1:].reset_index(drop=True)
                new_df.columns = [h.strip() for h in header]
                return new_df

        return df

    def receive_data(self, df):
        """Store the dataset; attempt to normalize if it's a single comma-joined column."""
        if df is None:
            self.df = None
            return

        df = df.copy()
        df.columns = df.columns.str.strip()

        # If the CSV was parsed into one column that contains commas, split it
        df = self._split_single_text_column(df)

        # Convert Date column if present
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Try converting non-date columns to numeric where possible
        for col in df.columns:
            if col != "Date" and not pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], errors="coerce")

        self.df = df

    def generate_chart(self, output_path, chart_type="line"):
        if self.df is None:
            return {"success": False, "error": "Dataset not loaded inside ChartAgent."}

        df = self.df.copy()

        # detect numeric columns (excluding Date)
        num_cols = df.select_dtypes(include=["number"]).columns.tolist()

        # If no numeric columns but there are object columns that look numeric, try to coerce again
        if len(num_cols) == 0:
            for col in df.columns:
                if col != "Date":
                    coerced = pd.to_numeric(df[col], errors="coerce")
                    if coerced.notna().sum() > 0:
                        df[col] = coerced
            num_cols = df.select_dtypes(include=["number"]).columns.tolist()

        if len(num_cols) == 0:
            return {"success": False, "error": "No numeric columns found. Column dtypes:\n" + str(df.dtypes)}

        has_date = "Date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["Date"])

        chart_type = (chart_type or "line").lower()

        # Reset any previous figure
        plt.close("all")
        plt.figure(figsize=(10, 5 + 1 * len(num_cols)))

        try:
            if chart_type == "line":
                if has_date:
                    for col in num_cols:
                        plt.plot(df["Date"], df[col], marker='o', label=col)
                    plt.xlabel("Date")
                    plt.gcf().autofmt_xdate()
                else:
                    for col in num_cols:
                        plt.plot(df.index, df[col], marker='o', label=col)
                    plt.xlabel("Index")

            elif chart_type == "bar":
                if has_date:
                    x = range(len(df))
                    total = len(num_cols)
                    width = 0.8 / max(total, 1)
                    for i, col in enumerate(num_cols):
                        plt.bar([xi + (i - total/2)*width for xi in x], df[col].fillna(0), width=width, label=col)
                    plt.xticks(x, df["Date"].dt.strftime('%Y-%m-%d'), rotation=45, ha='right')
                    plt.xlabel("Date")
                else:
                    df[num_cols].plot(kind="bar", figsize=(10, 5))
            elif chart_type == "hist":
                df[num_cols[0]].dropna().plot(kind="hist", bins=20)
            elif chart_type == "scatter":
                if len(num_cols) < 2:
                    return {"success": False, "error": "Scatter plot needs at least TWO numeric columns."}
                plt.scatter(df[num_cols[0]], df[num_cols[1]], alpha=0.7)
                plt.xlabel(num_cols[0]); plt.ylabel(num_cols[1])
            else:
                # default multi-line
                for col in num_cols:
                    plt.plot(df.index, df[col], marker='o', label=col)

            plt.legend()
            plt.title("Generated Chart")
            plt.tight_layout()
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()

            return {"success": True, "chart_type": chart_type, "path": output_path, "columns_plotted": num_cols}
        except Exception as e:
            plt.close("all")
            return {"success": False, "error": str(e)}
