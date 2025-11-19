# main.py → PROFESSIONAL VERSION (Used in production agents)

import asyncio
import httpx
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Use Gemini 1.5 Flash (or 2.5 when stable)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0)

class AgentState(TypedDict, total=False):
    user_query: str
    calculation_result: str
    weather_result: str
    final_answer: str


# ========================
# 1. Calculator Agent (Pure & Simple)
# ========================
async def calculator_agent(state: AgentState):
    prompt = f"""
    You are a precise math calculator. Only respond if there's math.
    User: {state['user_query']}

    If no math → reply: "No math to solve."
    Else → solve step-by-step and end with: Final Answer: [result]
    """
    resp = await llm.ainvoke(prompt)
    return {"calculation_result": resp.content.strip()}


# ========================
# 2. Weather Agent — Let the LLM do the smart work!
# ========================
async def weather_agent(state: AgentState):
    prompt = f"""
    You are a weather expert. Your job is to:
    1. Extract the city name from the user's question (if any)
    2. If no city → reply: "No city mentioned."
    3. If city found → return ONLY the city name in this format:
       CITY: <city name here>

    Be smart: "weather in paris", "tokyo temp", "mohali weather and 5+9" → extract the city.
    Ignore numbers and math.

    User question: {state['user_query']}

    Respond with exactly one line:
    """
    resp = await llm.ainvoke(prompt)
    text = resp.content.strip()

    if "CITY:" not in text.upper():
        return {"weather_result": "No city mentioned."}

    city = text.split("CITY:", 1)[1].strip().strip('"\'.,?!')
    if not city or len(city) < 2:
        return {"weather_result": "Could not detect a valid city."}

    # Now fetch real weather
    location = await geocode_and_get_weather(city)
    if not location:
        return {"weather_result": f"Could not find city: {city.title()}"}

    return {"weather_result": location}


# ========================
# Open-Meteo Helper (clean & reusable)
# ========================
async def geocode_and_get_weather(city: str):
    # Step 1: Geocode
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1, "language": "en"}
        )
        data = r.json()
        if not data.get("results"):
            return None
        loc = data["results"][0]

        lat, lon = loc["latitude"], loc["longitude"]
        name = f"{loc['name']}, {loc.get('admin1', '')} {loc.get('country', '')}".strip(", ")

        # Step 2: Weather
        r2 = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
                "timezone": "auto"
            }
        )
        w = r2.json()
        c, d = w["current"], w["daily"]

        desc = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 61: "Rain", 71: "Snow", 95: "Thunderstorm"
        }.get(c["weather_code"], "Unknown")

        return f"""
**Current Weather in {name}**
• Temperature: **{c['temperature_2m']}°C** (feels like {c['apparent_temperature']}°C)
• Condition: {desc}
• Wind: {c['wind_speed_10m']} km/h

**Today**: High {d['temperature_2m_max'][0]}°C | Low {d['temperature_2m_min'][0]}°C | Rain {d['precipitation_probability_max'][0]}%
        """.strip()


# ========================
# Combine
# ========================
def combine_results(state: AgentState):
    calc = state.get("calculation_result", "No math to solve.").strip()
    weather = state.get("weather_result", "No weather requested.").strip()

    return {"final_answer": f"""
**Your Question:** {state['user_query']}

**Math Result**
{calc}

**Weather**
{weather}
    """.strip() + "\n"}


# ========================
# Build Graph
# ========================
graph = StateGraph(AgentState)
graph.add_node("calculator", calculator_agent)
graph.add_node("weather", weather_agent)
graph.add_node("combine", combine_results)

graph.set_entry_point("calculator")
graph.set_entry_point("weather")
graph.add_edge("calculator", "combine")
graph.add_edge("weather", "combine")
graph.add_edge("combine", END)

app = graph.compile()


# ========================
# For Streamlit
# ========================
async def run_agents(query: str) -> str:
    result = await app.ainvoke({"user_query": query})
    return result["final_answer"]