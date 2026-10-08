from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path
import pandas as pd

from charts import (
    generate_pass_accuracy_pie_chart,
    generate_defensive_actions_chart,
    generate_goalkeeper_actions_chart,
    generate_radar_chart,
    generate_shot_conversion_chart,
    generate_top3_players_offensive_chart,
    generate_top3_players_defensive_chart,
    generate_tornado_chart,
)

from pdf.builder import build_pdf

from utils.data_processing import (
    calculate_match_stats,
    calculate_player_stats, 
    clean_data, 
    prepare_main_statistics_for_ai, 
    calculate_radar_metrics, 
    prepare_game_performance_statistics_for_ai,
    prepare_offensive_statistics_for_ai,
    prepare_defensive_statistics_for_ai,
    get_team_names,
)

from ai.analysis import (
    generate_main_statistics_analysis,
    generate_game_volume_analysis,
    generate_game_performance_analysis,
    generate_offensive_analysis,
    generate_defensive_analysis,
    generate_strengths_weaknesses_recommendations_analysis
)


def load_dataframes(csv_path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"El archivo CSV no existe: {csv_file}")

    metadata = _read_match_metadata(csv_file)
    cleaned_df = clean_data(pd.read_csv(csv_file, comment="#"))
    teams_df = calculate_match_stats(
        cleaned_df,
        metadata.get("team_name", "My Team"),
        metadata.get("rival_name", "Rival Team"),
    )
    players_df = calculate_player_stats(cleaned_df)
    return teams_df, players_df


def _read_match_metadata(csv_file: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    with csv_file.open("r", encoding="utf-8", newline="") as file:
        for row in csv.reader(file):
            if not row or not row[0].startswith("#"):
                break
            key = row[0][1:].strip()
            if len(row) > 1 and row[1].strip():
                metadata[key] = row[1].strip()
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera un informe PDF a partir de un CSV de acciones.")
    parser.add_argument("csv_file")
    args = parser.parse_args()
    csv_path = Path(args.csv_file)
    output_path = Path("reports") / f"Visual_Report_{csv_path.stem}.pdf"

    try:
        teams_df, players_df = load_dataframes(csv_path)
        team_names = get_team_names(teams_df)
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory)

            main_statistics_for_ai = prepare_main_statistics_for_ai(teams_df)
            main_statistics_analysis = generate_main_statistics_analysis(main_statistics_for_ai, team_names)

            tornado_path = generate_tornado_chart(teams_df, output_dir)

            game_volume_statistics_for_ai = teams_df.to_dict(orient="records")
            game_volume_analysis = generate_game_volume_analysis(game_volume_statistics_for_ai, team_names)

            radar_path = generate_radar_chart(teams_df, output_dir)
            
            game_performance_statistics = calculate_radar_metrics(teams_df)
            game_performance_statistics_for_ai = prepare_game_performance_statistics_for_ai(game_performance_statistics)
            game_performance_analysis = generate_game_performance_analysis(game_performance_statistics_for_ai, team_names)
            
            shot_conversion_path = generate_shot_conversion_chart(teams_df, output_dir)
            pass_accuracy_pie_path = generate_pass_accuracy_pie_chart(teams_df, output_dir)

            offensive_statistics_for_ai = prepare_offensive_statistics_for_ai(teams_df)
            offensive_analysis = generate_offensive_analysis(offensive_statistics_for_ai, team_names)

            defensive_actions_path = generate_defensive_actions_chart(teams_df, output_dir)
            goalkeeper_actions_path = generate_goalkeeper_actions_chart(teams_df, output_dir)

            defensive_statistics_for_ai = prepare_defensive_statistics_for_ai(teams_df)
            defensive_analysis = generate_defensive_analysis(defensive_statistics_for_ai, team_names)

            top3_offensive_path = generate_top3_players_offensive_chart(players_df, output_dir)
            top3_defensive_path = generate_top3_players_defensive_chart(players_df, output_dir)

            analysis_recopilation = {
                "main_statistics_analysis": main_statistics_analysis,
                "game_volume_analysis": game_volume_analysis,
                "game_performance_analysis": game_performance_analysis,
                "offensive_analysis": offensive_analysis,
                "defensive_analysis": defensive_analysis,
            }

            strengths_weaknesses_recommendations_data_for_ai = {"ai_analysis": analysis_recopilation, 
                "teams_data": teams_df.to_dict(orient="records"), 
                "players_data": players_df.to_dict(orient="records")
            }

            strenghts_weaknesses_recommendations_analysis = generate_strengths_weaknesses_recommendations_analysis(
                strengths_weaknesses_recommendations_data_for_ai,
                team_names,
            )

            build_pdf(
                tornado_path,
                radar_path,
                shot_conversion_path,
                pass_accuracy_pie_path,
                defensive_actions_path,
                goalkeeper_actions_path,
                top3_offensive_path,
                top3_defensive_path,
                teams_df,
                players_df,
                main_statistics_analysis,
                game_volume_analysis,
                game_performance_analysis,
                offensive_analysis,
                defensive_analysis,
                strenghts_weaknesses_recommendations_analysis,
                output_path,
            )
        print(f"Informe visual generado en: {output_path.absolute()}")
    except Exception as error:
        print(f"Error: {error}")
        raise


if __name__ == "__main__":
    main()
