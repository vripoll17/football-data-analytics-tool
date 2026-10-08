import os
import json

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

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

print("API key cargada:", bool(api_key))
print("Longitud:", len(api_key) if api_key else 0)

model = "inclusionai/ling-3.0-flash-sante:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


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
    main_statistics_for_ai: dict
) -> str | None:

    data_json = json.dumps(
        main_statistics_for_ai,
        indent=2,
        ensure_ascii=False
    )

    prompt = build_main_statistics_analysis_prompt(data_json)

    return _generate_ai_response(prompt)


def generate_game_volume_analysis(
    game_volume_statistics_for_ai: dict
) -> str | None:

    data_json = json.dumps(
        game_volume_statistics_for_ai,
        indent=2,
        ensure_ascii=False
    )

    prompt = build_game_volume_analysis_prompt(data_json)

    return _generate_ai_response(prompt)


def generate_game_performance_analysis(
    game_performance_statistics_for_ai: dict
) -> str | None:

    data_json = json.dumps(
        game_performance_statistics_for_ai,
        indent=2,
        ensure_ascii=False
    )

    prompt = build_game_performance_analysis_prompt(data_json)

    return _generate_ai_response(prompt)


def generate_offensive_analysis(
    offensive_statistics: dict
) -> str | None:

    data_json = json.dumps(
        offensive_statistics,
        indent=2,
        ensure_ascii=False
    )

    prompt = build_offensive_analysis_prompt(data_json)

    return _generate_ai_response(prompt)


def generate_defensive_analysis(
    defensive_statistics: dict
) -> str | None:

    data_json = json.dumps(
        defensive_statistics,
        indent=2,
        ensure_ascii=False
    )

    prompt = build_defensive_analysis_prompt(data_json)

    return _generate_ai_response(prompt)


def generate_strengths_weaknesses_recommendations_analysis(
    strengths_weaknesses_recommendations_data_for_ai: dict
) -> str | None:

    data_json = json.dumps(
        strengths_weaknesses_recommendations_data_for_ai,
        indent=2,
        ensure_ascii=False
    )

    prompt = build_strengths_weaknesses_recommendations_prompt(data_json)

    return _generate_ai_response(prompt)