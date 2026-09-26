import os

from dotenv import load_dotenv
from google import genai
import pandas as pd
import json

from ai.prompts import build_match_analysis_prompt

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def generate_ai_analysis(player_stats_df: pd.DataFrame, team_stats_df: pd.DataFrame) -> str:
    player_stats = player_stats_df.to_dict(orient="records")
    team_stats = team_stats_df.to_dict(orient="records")

    data_for_ai = {
        "team_stats": team_stats,
        "player_stats": player_stats
    }

    data_json = json.dumps(data_for_ai, indent=2, ensure_ascii=False)

    prompt = build_match_analysis_prompt(data_json)

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("\nError al contactar con Gemini:")
        print(e)
        return None