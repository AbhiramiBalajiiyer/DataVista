
import os
import json
import re

try:
    import openai
except Exception:
    openai = None

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
if openai and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY


class LLMAgent:
    def __init__(self, model="gpt-4o-mini" if openai else None):
        self.model = model

    def parse_intent(self, user_message):
        """
        Return structured intent:
        {
            "intent": "forecast",
            "params": {"days": 14},
            "detail": "original user message"
        }
        """
        text = user_message.lower().strip()
        params = {}
        intent = "unknown"

        # RULE-BASED MATCHES (fast + stable)

        # 1. EDA detection
        if any(w in text for w in ["eda", "explore", "exploratory", "describe the data"]):
            intent = "run_eda"

        # 2. Charts
        elif any(w in text for w in ["chart", "plot", "graph", "visual"]):
            intent = "generate_chart"

            # detect chart type
            m = re.search(r"(bar|line|scatter|heatmap)", text)
            if m:
                params["chart_type"] = m.group(1)

        # 3. Forecast with day extraction
        elif any(w in text for w in ["forecast", "predict", "future", "next"]):
            intent = "forecast"

            # extract "forecast 30 days" / "next 14 days"
            m = re.search(r"(\d+)\s*(day|days)", text)
            params["days"] = int(m.group(1)) if m else None

        # 4. Report
        elif any(w in text for w in ["report", "ppt", "presentation", "deck"]):
            intent = "generate_report"

        # 5. Summary / insights
        elif any(w in text for w in ["summary", "insight", "insights",
                                     "what's happening", "tell me"]):
            intent = "run_simple"

        # LLM FALLBACK 
        if intent == "unknown" and openai and OPENAI_API_KEY:
            try:
                prompt = (
                    "You are an intent parser for a data analytics app. "
                    "Return ONLY a JSON object with fields: intent, params, detail.\n"
                    "intent ∈ {run_simple, run_eda, generate_chart, forecast, generate_report, explain, unknown}.\n\n"
                    f"User message: '''{user_message}'''"
                )

                resp = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0
                )

                reply = resp["choices"][0]["message"]["content"].strip()
                return json.loads(reply)

            except Exception:
                pass  # still return rule-based version

        return {
            "intent": intent,
            "params": params,
            "detail": user_message
        }
