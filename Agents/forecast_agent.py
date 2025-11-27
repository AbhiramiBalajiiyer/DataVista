# # forecast_agent.py (Auto-ARIMA version)
# import pandas as pd
# import numpy as np
# from pmdarima import auto_arima

# class ForecastAgent:
#     def __init__(self):
#         self.data = None
#         self.target_col = None

#     def receive_data(self, df):
#         self.data = df

#         # Auto-detect target numeric column
#         numeric_cols = df.select_dtypes(include="number").columns
#         self.target_col = numeric_cols[0] if len(numeric_cols) else None

#     def forecast(self, days=7):
#         if self.data is None:
#             return {"error": "No data loaded for forecasting."}

#         if self.target_col is None:
#             return {"error": "No numeric column found for forecasting."}

#         series = self.data[self.target_col].dropna()

#         if len(series) < 20:
#             return {"error": "Not enough data to run Auto-ARIMA forecasting."}

#         try:
#             # Fit Auto-ARIMA model
#             model = auto_arima(
#                 series,
#                 seasonal=False,
#                 stepwise=True,
#                 trace=False,
#                 error_action="ignore",
#                 suppress_warnings=True
#             )

#             forecast_values = model.predict(days)

#             # Build output dataframe
#             start_idx = len(series)
#             end_idx = start_idx + days - 1

#             df_forecast = pd.DataFrame({
#                 "day": list(range(start_idx, end_idx + 1)),
#                 "forecast": forecast_values
#             })

#             # Insights text
#             insight = (
#                 f"Forecast generated for next **{days} days** "
#                 f"using Auto-ARIMA (best model: {model.order})."
#             )

#             return {"insights": insight, "forecast": df_forecast}

#         except Exception as e:
#             return {"error": f"Auto-ARIMA failed: {str(e)}"}


# forecast_agent.py
# forecast_agent.py
import pandas as pd
import numpy as np
from pmdarima import auto_arima
from sklearn.linear_model import LinearRegression


class ForecastAgent:
    def __init__(self):
        self.data = None
        self.target_col = None
        self.min_points_for_arima = 10  # threshold for ARIMA

    # ---------- Helpers ----------

    def _split_single_text_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        If the DataFrame has exactly one column and that column (or its name)
        looks like a comma-separated header, split it into multiple columns.
        """
        if df.shape[1] != 1:
            return df

        col_name = df.columns[0]
        first_vals = df.iloc[:, 0].astype(str)

        # If header or first row contains commas, treat as CSV folded into one column
        if ("," in col_name) or (first_vals.str.contains(",").any()):
            if "," in col_name:
                # header stored in column name
                new_cols = [c.strip() for c in col_name.split(",")]
                new_df = df.iloc[:, 0].str.split(",", expand=True)
                new_df.columns = new_cols[: new_df.shape[1]]
                # drop first row if it duplicates header
                first_row = new_df.iloc[0].astype(str).tolist()
                if all(a == b for a, b in zip(first_row, new_cols[: len(first_row)])):
                    new_df = new_df.iloc[1:].reset_index(drop=True)
                return new_df
            else:
                # header stored in first row
                splitted = df.iloc[:, 0].str.split(",", expand=True)
                header = splitted.iloc[0].astype(str).tolist()
                new_df = splitted.iloc[1:].reset_index(drop=True)
                new_df.columns = [h.strip() for h in header]
                return new_df

        return df

    # ---------- Public API ----------

    def receive_data(self, df: pd.DataFrame):
        """Normalize incoming dataset and choose a numeric target column."""
        if df is None:
            self.data = None
            self.target_col = None
            return

        df = df.copy()
        df.columns = df.columns.str.strip()

        # Fix “one big column” CSVs
        df = self._split_single_text_column(df)

        # Parse date if present
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        # Coerce all non-date columns to numeric where possible
        for col in df.columns:
            if col.lower() not in ["date", "time", "timestamp"] and not pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], errors="coerce")

        self.data = df

        # Choose numeric column with most non‑NaN values (good default target)
        num_cols = df.select_dtypes(include="number").columns
        if len(num_cols):
            self.target_col = max(num_cols, key=lambda c: df[c].notna().sum())
        else:
            self.target_col = None

    def forecast(self, days: int = 7):
        """Forecast next `days` points for the auto-selected target column."""
        if self.data is None:
            return {"error": "No data loaded for forecasting."}

        if self.target_col is None:
            return {"error": "No numeric column found for forecasting."}

        series = self.data[self.target_col].dropna()
        n = len(series)

        if n == 0:
            return {
                "error": (
                    f"Target column '{self.target_col}' is empty after cleaning. "
                    "Check if values contain symbols or are non-numeric."
                )
            }

        # ---- CASE 1: Short series → linear trend model ----
        if n < self.min_points_for_arima:
            X = np.arange(n).reshape(-1, 1)
            y = series.values.astype(float)

            model = LinearRegression()
            model.fit(X, y)

            future_X = np.arange(n, n + days).reshape(-1, 1)
            fc = model.predict(future_X)

            df_fc = pd.DataFrame({
                "day": range(n, n + days),
                "forecast": fc,
            })

            insight = (
                f"Series has only {n} valid points; used linear trend regression on "
                f"'{self.target_col}' to forecast the next {days} days."
            )
            return {"insights": insight, "forecast": df_fc}

        # ---- CASE 2: Normal series → Auto‑ARIMA ----
        try:
            model = auto_arima(
                series,
                seasonal=False,
                stepwise=True,
                trace=False,
                error_action="ignore",
                suppress_warnings=True,
            )

            fc = model.predict(days)

            df_fc = pd.DataFrame({
                "day": range(n, n + days),
                "forecast": fc,
            })

            insight = (
                f"Forecast generated for next {days} days on '{self.target_col}' "
                f"using Auto-ARIMA (order: {model.order})."
            )
            return {"insights": insight, "forecast": df_fc}

        except Exception as e:
            # ---- CASE 3: ARIMA fails → fallback to linear trend ----
            X = np.arange(n).reshape(-1, 1)
            y = series.values.astype(float)
            reg = LinearRegression().fit(X, y)
            future_X = np.arange(n, n + days).reshape(-1, 1)
            fc = reg.predict(future_X)

            df_fc = pd.DataFrame({
                "day": range(n, n + days),
                "forecast": fc,
            })

            insight = (
                f"Auto-ARIMA failed ({e}); fell back to linear trend regression "
                f"for the next {days} days on '{self.target_col}'."
            )
            return {"insights": insight, "forecast": df_fc}
