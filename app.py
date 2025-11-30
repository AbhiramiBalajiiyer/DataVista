
#--------------------
import streamlit as st
import pandas as pd
import os

from Agents.simple_agent import SimpleDataAgent
from Agents.eda_agent import EDAAgent
from Agents.chart_agent import ChartAgent
from Agents.forecast_agent import ForecastAgent
from Agents.report_agent import ReportAgent
from Core.supervisor_agent import SupervisorAgent
from Core.memory_manager import MemoryManager
from Core.logger import Logger

# -------------------------------------------------
# Constants
# -------------------------------------------------
ASSETS_DIR = "assets"
CHART_PATH = f"{ASSETS_DIR}/chart.png"
REPORT_PATH = f"{ASSETS_DIR}/insightops_report.pptx"
os.makedirs(ASSETS_DIR, exist_ok=True)

# -------------------------------------------------
# Streamlit UI Config
# -------------------------------------------------
st.set_page_config(page_title="InsightOps", layout="wide")
st.markdown(
    """
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 700;
            text-align: center;
            margin-bottom: 5px;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            color: #666;
            margin-bottom: 30px;
        }
        .card {
            padding: 20px;
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 30px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-title"> InsightOps — AI-Powered Analytics Suite</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload data → Chat → Analyze → Forecast → Generate Reports</div>', unsafe_allow_html=True)


# -------------------------------------------------
# Memory + Logger
# -------------------------------------------------
if "memory" not in st.session_state:
    st.session_state.memory = MemoryManager()

if "logger" not in st.session_state:
    st.session_state.logger = Logger()

# -------------------------------------------------
# Load Agents Once
# -------------------------------------------------
if "agents" not in st.session_state:
    st.session_state.agents = {
        "simple": SimpleDataAgent(),
        "eda": EDAAgent(),
        "chart": ChartAgent(),
        "forecast": ForecastAgent(),
        "report": ReportAgent(),
    }

if "supervisor" not in st.session_state:
    st.session_state.supervisor = SupervisorAgent(
        memory_manager=st.session_state.memory,
        logger=st.session_state.logger
    )

supervisor = st.session_state.supervisor
agents = st.session_state.agents

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
with st.sidebar:
    st.header("📂 Upload Data")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    st.markdown("---")

    st.subheader("Agents Installed")
    st.markdown("""
    - **SimpleDataAgent** – quick stats  
    - **EDAAgent** – missing values, correlation  
    - **ChartAgent** – chart generation  
    - **ForecastAgent** – ARIMA  
    - **ReportAgent** – PPTX reports  
    - **SupervisorAgent** – routes tasks  
    """)

if not uploaded_file:
    st.warning("Please upload a CSV file to begin.")
    st.stop()

# Auto-detect delimiter
sample = uploaded_file.read().decode("utf-8", errors="ignore")
uploaded_file.seek(0)  # reset pointer

delimiter = ","
if ";" in sample and sample.count(";") > sample.count(","):
    delimiter = ";"
elif "\t" in sample:
    delimiter = "\t"

df = pd.read_csv(uploaded_file, delimiter=delimiter)

# -------------------------------------------------
# Load DF into Agents
# -------------------------------------------------
for agent in agents.values():
    try:
        agent.receive_data(df)
    except Exception as e:
        st.sidebar.error(f"Agent failed: {e}")

# -------------------------------------------------
# Display Data Preview (Card)
# -------------------------------------------------
with st.container():
    #st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Data Preview")
    st.dataframe(df.head())
    #st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------
# Chat UI
# -------------------------------------------------
# st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("Ask InsightOps")

user_input = st.text_input(
    "Examples: `run EDA`, `plot chart`, `forecast 7 days`, `generate report`",
    placeholder="Type your request here..."
)

if user_input:
    response = supervisor.handle_nl(user_input, agents)
    route = response["route"]
    result = response["result"]

    st.markdown(f"### 🔍 Route: `{route}`")

    if route == "chart":
        # result is dict from ChartAgent.generate_chart
        if isinstance(result, dict) and result.get("success"):
            st.success("Chart generated successfully.")
            # show the NEW chart directly from returned path
            chart_path = result.get("path", "chart.png")
            if os.path.exists(chart_path):
                st.image(chart_path, caption="Generated Chart")
        else:
            st.error(result if isinstance(result, str)
                     else result.get("error", "Chart error."))

    elif route == "report":
        if isinstance(result, str) and os.path.exists(result):
            st.success("📘 Report successfully generated!")

            with open(result, "rb") as f:
                st.download_button(
                    "📥 Download InsightOps Report",
                    data=f,
                    file_name="InsightOps_Report.pptx",
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                )
        else:
            st.error("Report generation failed.")
    else:
        st.write(result)


st.markdown("</div>", unsafe_allow_html=True)
