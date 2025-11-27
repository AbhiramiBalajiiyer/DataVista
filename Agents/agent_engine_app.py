# Agents/agent_engine_app.py

from adk import AgentApp  # use the exact class from your lab

from Agents.chart_agent import ChartAgent
from Agents.forecast_agent import ForecastAgent
from Core.supervisor_agent import SupervisorAgent
from Core.memory_manager import MemoryManager
from Core.logger import Logger


# 1. Create your internal agents
memory = MemoryManager()
logger = Logger()

chart = ChartAgent()
forecast = ForecastAgent()
supervisor = SupervisorAgent(memory_manager=memory, logger=logger)

# 2. Build the ADK app (root agent)
app = AgentApp()          # or whatever base app your lab shows
root_agent = app          # ADK expects `root_agent` or `app`
