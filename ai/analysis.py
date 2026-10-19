import os
import json
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from ai.prompts import (
    build_main_statistics_analysis_prompt,
    build_game_volume_analysis_prompt,
    build_game_performance_analysis_prompt,
    build_offensive_analysis_prompt,
    build_defensive_analysis_prompt,
    build_strengths_weaknesses_recommendations_prompt
)

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)

api_key = os.getenv("OPENROUTER_API_KEY")

AI_LANGUAGE = "Spanish"  # Change this to your preferred language, e.g., "English", "French", etc.
model = "nvidia/nemotron-3.5-super-vl:free"  # Change this to your preferred model
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _prompt_data(data: object, team_names: tuple[str, str] | None) -> str:
    data_json = json.dumps(data, indent=2, ensure_ascii=False)
    if not team_names:
        return data_json

    team_name, rival_name = team_names
    context = (
        "MATCH TEAM CONTEXT:\n"
        f"- My team: {team_name}\n"
        f"- Rival team: {rival_name}\n\n"
        f"RESPONSE LANGUAGE: {AI_LANGUAGE}\n"
        f"Write the entire analysis in {AI_LANGUAGE}. Do not use another language.\n"
        "Use these exact names when referring to the teams in the analysis.\n\n"
    )
    return context + data_json


def _generate_ai_response(prompt: str) -> str | None:
    if not api_key:
        print("\nError al contactar con OpenRouter: falta OPENROUTER_API_KEY en el archivo .env")
        return None

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            },
            timeout=60,
        )

        if not response.ok:
            print("\nError al contactar con OpenRouter:")
            print(f"HTTP {response.status_code}: {response.text}")
            return None

        data = response.json()

        return data["choices"][0]["message"]["content"]

    except requests.RequestException as e:
        print("\nError al contactar con OpenRouter:")
        print(e)
        return None
    except (KeyError, TypeError, ValueError) as e:
        print("\nRespuesta no válida de OpenRouter:")
        print(e)
        return None


def generate_main_statistics_analysis(
    main_statistics_for_ai: dict,
    team_names: tuple[str, str] | None = None,
) -> str | None:
    data_json = _prompt_data(main_statistics_for_ai, team_names)

    prompt = build_main_statistics_analysis_prompt(data_json)

    return _generate_ai_response(prompt)


def generate_game_volume_analysis(
    game_volume_statistics_for_ai: dict,
    team_names: tuple[str, str] | None = None,
) -> str | None:
    data_json = _prompt_data(game_volume_statistics_for_ai, team_names)

    prompt = build_game_volume_analysis_prompt(data_json)

    return _generate_ai_response(prompt)


def generate_game_performance_analysis(
    game_performance_statistics_for_ai: dict,
    team_names: tuple[str, str] | None = None,
) -> str | None:
    data_json = _prompt_data(game_performance_statistics_for_ai, team_names)

    prompt = build_game_performance_analysis_prompt(data_json)

    return _generate_ai_response(prompt)


def generate_offensive_analysis(
    offensive_statistics: dict,
    team_names: tuple[str, str] | None = None,
) -> str | None:
    data_json = _prompt_data(offensive_statistics, team_names)

    prompt = build_offensive_analysis_prompt(data_json)

    return _generate_ai_response(prompt)


def generate_defensive_analysis(
    defensive_statistics: dict,
    team_names: tuple[str, str] | None = None,
) -> str | None:
    data_json = _prompt_data(defensive_statistics, team_names)

    prompt = build_defensive_analysis_prompt(data_json)

    return _generate_ai_response(prompt)


def generate_strengths_weaknesses_recommendations_analysis(
    strengths_weaknesses_recommendations_data_for_ai: dict,
    team_names: tuple[str, str] | None = None,
) -> str | None:
    data_json = _prompt_data(strengths_weaknesses_recommendations_data_for_ai, team_names)

    prompt = build_strengths_weaknesses_recommendations_prompt(data_json)

    return _generate_ai_response(prompt)