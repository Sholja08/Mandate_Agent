# Mandate_Agent
An AI-powered **UPI Mandate Assistance Agent** built using **Python, LangGraph, LangChain, and FastMCP**, designed to help users manage UPI mandates such as creation issues, failures, status checks, cancellations, and bank complaints through natural language conversations.

 🚀 Features

- 🤖 AI-driven conversational agent for UPI mandate support
- 🔄 Handles mandate lifecycle issues:
  - Mandate creation failures
  - Pending / failed mandates
  - Mandate status checks
  - Mandate cancellation issues
- 🧠 Intelligent reasoning using **LangGraph state machines**
- 🔧 Secure backend tool execution using **FastMCP**
- 📡 Real-time response streaming for better UX
- 🏦 Bank & merchant context enrichment
- 📨 Auto-drafting professional emails for bank escalation
- 🌐 Multilingual response support

---

## 🛠️ Tech Stack

- **Python 3.9+**
- **LangChain** – Prompt orchestration & LLM integration  
- **LangGraph** – Stateful agent workflow and routing  
- **FastMCP** – Secure tool server for banking actions  
- **Pydantic** – Strongly typed state & structured outputs  
- **AsyncIO** – Non-blocking async execution  

---

## 🧩 Architecture Overview

User Query
↓
LangGraph State Machine
↓
LLM Decision (Structured Output)
↓
Tool Invocation (FastMCP)
↓
Mandate Data / Bank Response
↓
Resolution / Next Action / Email Draft


- The agent maintains a **shared state** across nodes
- Routing decisions are controlled by the LLM
- Each mandate-related action is executed as a tool node

---

## 🔄 Agent Workflow

1. User reports a UPI mandate issue
2. Agent identifies the mandate context
3. Authenticates the user (if required)
4. Fetches mandate details via tools
5. Explains the failure or status clearly
6. Suggests resolution steps
7. Optionally:
   - Drafts an escalation email
   - Raises a bank complaint

---

## 🧠 Core Concepts Used

- **LLM + Tools = Intelligent Agent**
- **Structured Outputs** to prevent hallucinations
- **State-driven routing** using LangGraph
- **Streaming responses** for real-time feedback
- **Separation of reasoning and execution**

---

## 📂 Project Structure

mandate-agent/
│
├── agent/
│ ├── prompts.py
│ ├── schema.py
│ ├── enums.py
│ ├── tools.py
│ ├── utils.py
│
├── mcp_tools/
│ ├── mandate_tools.py
│
├── resources/
│ ├── bank_contacts.py
│ ├── merchant_info.py
│
├── main.py
├── requirements.txt
└── README.md


---

## ▶️ How to Run

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the agent
python main.py
