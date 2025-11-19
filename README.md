# Langgraph-Parallel-Agents  
**True Parallel LLM Agents with LangGraph + Gemini 2.5 Flash + Streamlit**

A clean, production-ready demo that runs **multiple Gemini agents completely in parallel** (not one after the other.

Ask a single question like  
> “What’s the weather in Tokyo right now and what is 47 × 312?”

and watch two specialized agents work **at the same time**:

- Calculator Agent → solves the math instantly  
- Weather Agent → extracts the city and fetches real-time weather (Open-Meteo, no key needed)

Results are combined and displayed in a beautiful Streamlit chat interface.

## Live Demo Feel
Try these:
- `Solve 15^3 and weather in Paris`
- `123 * 456 and temperature in Dubai`
- `sin(π/4) + cos(π/3) and how is New York today?`

## Features
- True async parallel execution using LangGraph
- Gemini 2.5 Flash (super fast & cheap)
- Real-time weather via Open-Meteo (free forever)
- Clean separation: `main.py` (logic) + Streamlit UI
- Proper async event loop handling in Streamlit
- Ready for deployment (Streamlit Community Cloud, Docker, etc.)

## Project Structure
Langgraph-agents/
├── main.py              # All agent logic, graph, weather API
├── app.py               # Streamlit frontend (or streamlit_app.py)
├── .env                 # Your GOOGLE_API_KEY (gitignored)
├── .env.example         # Template for others
├── .gitignore
├── requirements.txt
└── README.md


## Quick Start

```bash
# 1. Clone
git clone https://github.com/Pratishtha-348/Langgraph-agents.git
cd Langgraph-agents

# 2. Create virtual env
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Add your Gemini key
cp .env.example .env
# edit .env and paste your key
Get free Gemini API key → https://aistudio.google.com/app/apikey
Bash# 5. Run
streamlit run app.py
requirements.txt
txtstreamlit>=1.38
langgraph>=0.2
langchain-google-genai>=2.0
httpx>=0.27
python-dotenv>=1.0

User Query  
├──► Calculator Agent (Gemini)  
└──► Weather Agent → extracts city → Open-Meteo API  
          ▼  
      Combine Node → Final Beautiful Answer

Both agents start instantly thanks to multiple entry points in LangGraph.

## Deploy Anywhere
- Streamlit Community Cloud (free, one-click deploy)
- Docker
- Railway / Render / Fly.io

### Docker example
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
