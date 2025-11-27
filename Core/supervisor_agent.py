from Core.llm_router import LLMAgent
import re

class SupervisorAgent:
    def __init__(self, memory_manager, logger=None):
        self.memory = memory_manager
        self.logger = logger
        self.llm = LLMAgent()

    def _log(self, msg):
        if self.logger:
            try:
                self.logger.log(msg)
            except:
                pass

    def handle_nl(self, user_message, agents):
        try:
            msg = user_message.lower().strip()
            self._log(f"[Supervisor] Message: {msg}")

            parsed = self.llm.parse_intent(user_message)
            intent = parsed.get("intent", "unknown")
            params = parsed.get("params", {})

            # Remember conversation
            try:
                self.memory.remember_session(
                    f"msg_{len(self.memory.session_state)+1}",
                    {"user": user_message, "parsed": parsed}
                )
            except:
                pass

            # ========== SMALL TALK ==========
            if msg in ["hi", "hello", "hey", "hola"]:
                return {"route": "chat", "result": "Hello! Upload a dataset to begin."}

            # ========== SIMPLE ==========
            if intent == "run_simple":
                return {"route": "simple", "result": agents["simple"].analyze()}

            # ========== EDA ==========
            if intent == "run_eda":
                return {"route": "eda", "result": agents["eda"].analyze()}

            # ========== CHART GENERATION ==========
            if intent == "generate_chart":
                chart_type = params.get("chart_type", "line")
                result = agents["chart"].generate_chart("assets/chart.png", chart_type)
                return {"route": "chart", "result": result}

            # ========== FORECASTING ==========
            if intent == "forecast":
                days = params.get("days")

                if not days:
                    m = re.search(r"(\\d+)", msg)
                    days = int(m.group(1)) if m else 7

                res = agents["forecast"].forecast(days=int(days))
                return {"route": "forecast", "result": res}

            # ========== REPORT ==========
            if intent == "generate_report":
                simple = agents["simple"].analyze()
                eda = agents["eda"].analyze()
                forecast = agents["forecast"].forecast()

                agents["report"].collect(
                    simple.get("insights"),
                    eda.get("insights"),
                    forecast.get("insights")
                )

                pptx_path = agents["report"].generate(
                    "assets/insightops_report.pptx",
                    "assets/chart.png"
                )

                return {"route": "report", "result": pptx_path}

            # ========== UNKNOWN ==========
            return {
                "route": "unknown",
                "result": "I didn't understand that. Try: run EDA, plot chart, forecast 7 days, generate report."
            }

        except Exception as e:
            self._log(f"Supervisor Error: {e}")
            return {"route": "error", "result": f"Error: {e}"}
