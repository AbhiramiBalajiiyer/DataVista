# # app.py - Frosted White Glassmorphism UI (InsightOps)
# import streamlit as st
# import pandas as pd
# import os
# from io import BytesIO
# from model_trainer import ModelTrainer
# from shap_wrapper import explain_model
# from sql_agent import SQLAgent
# from workflow import save_workflow, load_workflow
# from ui_helpers import stream_message


# # Local uploaded image path (for header)
# HEADER_IMAGE_PATH = "/mnt/data/940cbf07-fed1-4dcb-a1fb-d9c9e40ba5d3.png"

# # Import agents & utilities
# from simple_agent import SimpleDataAgent
# from eda_agent import EDAAgent
# from chart_agent import ChartAgent
# from forecast_agent import ForecastAgent
# from report_agent import ReportAgent

# from supervisor_agent import SupervisorAgent
# from memory_manager import MemoryManager
# from observability import Logger

# # Optional memory bank
# try:
#     from memory_bank import MemoryBank
#     HAS_MEMORY_BANK = True
# except:
#     HAS_MEMORY_BANK = False

# # Set page config
# st.set_page_config(page_title="InsightOps — Frosted UI", layout="wide")


# # -------------------------
# #   BEAUTIFUL FROSTED-GLASS UI HEADER (NO IMAGE)
# # -------------------------
# st.markdown("""
# <style>
#     .main {
#         background: #f7f9fc;
#     }
#     .glass-header {
#         background: rgba(255, 255, 255, 0.5);
#         padding: 30px;
#         border-radius: 20px;
#         box-shadow: 0 4px 20px rgba(0,0,0,0.1);
#         backdrop-filter: blur(12px);
#         margin-bottom: 25px;
#         display: flex;
#         align-items: center;
#         gap: 20px;
#     }
#     .logo-badge {
#         width: 55px;
#         height: 55px;
#         border-radius: 15px;
#         background: linear-gradient(135deg, #3b82f6, #06b6d4);
#         display: flex;
#         align-items: center;
#         justify-content: center;
#         font-size: 30px;
#         color: white;
#         font-weight: bold;
#     }
#     .title-text {
#         font-size: 40px;
#         font-weight: 700;
#         color: #1a1a1a;
#         letter-spacing: -1px;
#         margin-bottom: -3px;
#     }
#     .subtitle-text {
#         font-size: 16px;
#         color: #444;
#     }
# </style>

# <div class="glass-header">
#     <div class="logo-badge">IO</div>
#     <div>
#         <div class="title-text">InsightOps</div>
#         <div class="subtitle-text">Frosted glass AI multi-agent analyst</div>
#     </div>
# </div>
# """, unsafe_allow_html=True)



# # ================================
# # Initialize Supervisor + Memory
# # ================================
# if "supervisor" not in st.session_state:
#     memory = MemoryManager()
#     logger = Logger()

#     st.session_state["supervisor"] = SupervisorAgent(
#         memory_manager=memory,
#         logger=logger
#     )

# supervisor = st.session_state["supervisor"]

# # ================================
# # LAYOUT
# # ================================
# col_left, col_center, col_right = st.columns([1, 2, 1])

# # ---------- LEFT PANEL ----------
# with col_left:
#     st.header("Controls")

#     uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

#     if uploaded_file:
#         df = pd.read_csv(uploaded_file)
#         sql = SQLAgent(); sql.load_df(df)
#         trainer = ModelTrainer(df, target_col)  # prompt user to choose or auto-detect
#         st.session_state["agents"].update({"sql": sql, "trainer": trainer})

#         st.success(f"Loaded dataset — {df.shape[0]} rows")
#         st.dataframe(df.head())

#         if "agents" not in st.session_state:
#             simple = SimpleDataAgent()
#             eda = EDAAgent()
#             chart = ChartAgent()
#             forecast = ForecastAgent()
#             report = ReportAgent()

#             # Supply data to agents
#             simple.receive_data(df)
#             eda.receive_data(df)
#             chart.receive_data(df)
#             forecast.receive_data(df)
#             #report.receive_data(df)

#             st.session_state["agents"] = {
#                 "simple": simple,
#                 "eda": eda,
#                 "chart": chart,
#                 "forecast": forecast,
#                 "report": report,
#             }

#     st.markdown("---")
#     st.subheader("Quick Actions")

#     if st.button("Run EDA"):
#         if "agents" in st.session_state:
#             out = st.session_state["agents"]["eda"].analyze()
#             st.code(out["insights"])
#         else:
#             st.warning("Upload a CSV first!")

# # ---------- CENTER: CHAT ----------
# with col_center:
#     st.header("Chat with InsightOps")

#     # Initialize message history
#     if "messages" not in st.session_state:
#         st.session_state["messages"] = []

#     # Display past messages
#     for msg in st.session_state["messages"]:
#         with st.chat_message(msg["role"]):
#             st.write(msg["content"])

#     # ---- SINGLE chat input at bottom (correct placement) ----
#     user_input = st.chat_input("Ask me anything...")

#     if user_input:
#         # Add user message
#         st.session_state["messages"].append({"role": "user", "content": user_input})
#         with st.chat_message("user"):
#             st.write(user_input)

#         # If no dataset loaded yet
#         if "agents" not in st.session_state:
#             reply = "Please upload a CSV first so I can analyze it 😊"
#         else:
#             reply = supervisor.handle_nl(
#                 user_input,
#                 st.session_state["agents"]
#             )["result"]

#         # Add assistant response
#         st.session_state["messages"].append({"role": "assistant", "content": reply})
#         with st.chat_message("assistant"):
#             st.write(reply)


# # ---------- RIGHT PANEL ----------
# with col_right:
#     st.header("Memory & Logs")

#     if "agents" in st.session_state:
#         st.success("Agents active: " + ", ".join(st.session_state["agents"].keys()))
#     else:
#         st.warning("No dataset loaded")

#     st.markdown("---")
#     st.markdown("**Quick prompts**")
#     st.write("- run EDA")
#     st.write("- generate chart")
#     st.write("- forecast next 14 days")
#     st.write("- create report")

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

    st.subheader("🧠 Agents Installed")
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
    st.subheader("📄 Data Preview")
    st.dataframe(df.head())
    #st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------
# Chat UI
# -------------------------------------------------
# st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("💬 Ask InsightOps")

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
