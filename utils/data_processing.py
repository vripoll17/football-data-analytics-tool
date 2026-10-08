import pandas as pd

def clean_data(df):
    # remove timestamp column
    df = df.drop(columns=["timestamp"])

    # convert to lowercase
    df["action"] = df["action"].str.strip().str.lower()
    df["position"] = df["position"].str.strip().str.lower()

    # replace "Equipo rival" with "rival" in the player column
    df["player"] = df["player"].replace("Equipo rival", "rival")

    return df

def calculate_player_stats(df):
    # create a new DataFrame to store the stats for each player
    players_df = pd.DataFrame()

    # create rows for each player and columns for each action
    actions = df["action"].unique()
    players_df["player"] = df["player"].unique()

    # remove rival data we only want player data
    players_df = players_df[players_df["player"] != "rival"]

    # initialize the DataFrame with the actions
    for action in actions:
        players_df[action] = 0

    # count the occurrences of each action for each player and update the DataFrame
    counts = df.groupby(["player", "action"]).size()
    for (player, action), count in counts.items():
        if player != "rival":
            players_df.loc[players_df["player"] == player, action] += count

    return players_df


def calculate_match_stats(df, team_name: str = "My Team", rival_name: str = "Rival Team"):
    # create a new DataFrame to store the stats for each team
    teams_df = pd.DataFrame() 

    # create rows for each team and columns for each action
    actions = df["action"].unique()
    teams = ["My Team", "Rival Team"]

    # Initialize the DataFrame with the teams and actions
    teams_df["team"] = teams
    for action in actions:
        teams_df[action] = 0

    # Count the occurrences of each action for each player and group by team
    counts = df.groupby(["player", "action"]).size()
    for (player, action), count in counts.items():
        if player == "rival":
            teams_df.loc[teams_df["team"] == "Rival Team", action] += count
        else:
            teams_df.loc[teams_df["team"] == "My Team", action] += count

    teams_df.attrs["team_name"] = team_name
    teams_df.attrs["rival_name"] = rival_name
    return teams_df


def get_team_names(teams_df: pd.DataFrame) -> tuple[str, str]:
    return (
        teams_df.attrs.get("team_name", "My Team"),
        teams_df.attrs.get("rival_name", "Rival Team"),
    )

def prepare_main_statistics_for_ai(teams_df: pd.DataFrame) -> dict[str, int]:
    main_metrics = [
        ("Goals", "gol"),
        ("Shots", "tiro"),
        ("Shots on target", "tiro a puerta"),
        ("Passes", "pase"),
        ("Recoveries", "recuperacion"),
        ("Interceptions", "intercepcion"),
        ("Losses", "perdida"),
    ]

    my_team_stats = teams_df.loc[teams_df["team"] == "My Team"].iloc[0]
    rival_team_stats = teams_df.loc[teams_df["team"] == "Rival Team"].iloc[0]
    team_name, rival_name = get_team_names(teams_df)

    main_statistics_for_ai = {
        f"{team_name} {label}": int(my_team_stats.get(column, 0)) for label, column in main_metrics
    }
    main_statistics_for_ai.update({
        f"{rival_name} {label}": int(rival_team_stats.get(column, 0)) for label, column in main_metrics
    })

    return main_statistics_for_ai


def calculate_radar_metrics(teams_df: pd.DataFrame) -> tuple[list[float], list[float], list[str]]:
    my_team = teams_df.loc[teams_df["team"] == "My Team"].iloc[0]
    rival = teams_df.loc[teams_df["team"] == "Rival Team"].iloc[0]

    def ratio(numerator: int, denominator: int) -> float:
        return numerator / denominator if denominator > 0 else 0.0

    my_passes = int(my_team.get("pase", 0))
    my_failed_passes = int(my_team.get("pase errado", 0))
    rival_passes = int(rival.get("pase", 0))
    rival_failed_passes = int(rival.get("pase errado", 0))
    my_shots = int(my_team.get("tiro", 0))
    my_shots_on_target = int(my_team.get("tiro a puerta", 0))
    rival_shots = int(rival.get("tiro", 0))
    rival_shots_on_target = int(rival.get("tiro a puerta", 0))
    my_defensive_actions = sum(int(my_team.get(action, 0)) for action in ["recuperacion", "despeje", "intercepcion"])
    rival_defensive_actions = sum(int(rival.get(action, 0)) for action in ["recuperacion", "despeje", "intercepcion"])

    my_offensive_actions = my_passes + int(my_team.get("regate", 0)) + my_shots
    rival_offensive_actions = rival_passes + int(rival.get("regate", 0)) + rival_shots
    my_values = [
        ratio(my_passes, my_passes + my_failed_passes),
        ratio(my_shots_on_target, my_shots + my_shots_on_target),
        ratio(int(my_team.get("gol", 0)), my_shots + my_shots_on_target),
        ratio(int(my_team.get("recuperacion", 0)), my_defensive_actions),
        ratio(int(my_team.get("parada", 0)) + int(my_team.get("blocaje", 0)), rival_shots_on_target),
        ratio(my_offensive_actions - int(my_team.get("perdida", 0)), my_offensive_actions),
    ]
    rival_values = [
        ratio(rival_passes, rival_passes + rival_failed_passes),
        ratio(rival_shots_on_target, rival_shots + rival_shots_on_target),
        ratio(int(rival.get("gol", 0)), rival_shots + rival_shots_on_target),
        ratio(int(rival.get("recuperacion", 0)), rival_defensive_actions),
        ratio(int(rival.get("parada", 0)) + int(rival.get("blocaje", 0)), my_shots_on_target),
        ratio(rival_offensive_actions - int(rival.get("perdida", 0)), rival_offensive_actions),
    ]
    labels = [
        "% Pases acertados",
        "% Tiros a puerta",
        "% Goles por tiro",
        "% Recuperaciones por accion defensiva",
        "% Paradas+blocajes sobre tiros rivales",
        "% Acciones ofensivas sin perdida",
    ]

    return my_values, rival_values, labels

def prepare_game_performance_statistics_for_ai(radar_data: tuple) -> dict:
    my_values, rival_values, labels = radar_data

    return {
        "metrics": [
            {
                "name": label,
                "my_team": round(my_value * 100, 1),
                "rival": round(rival_value * 100, 1)
            }
            for label, my_value, rival_value
            in zip(labels, my_values, rival_values)
        ]
    }


def prepare_offensive_statistics_for_ai(teams_df: pd.DataFrame) -> dict:
    my_team_rows = teams_df.loc[teams_df["team"] == "My Team"]
    my_team = my_team_rows.iloc[0] if not my_team_rows.empty else pd.Series(dtype=float)

    completed_passes = int(my_team.get("pase", 0))
    failed_passes = int(my_team.get("pase errado", 0))
    total_shots = int(my_team.get("tiro", 0)) + int(my_team.get("tiro a puerta", 0))
    shots_on_target = int(my_team.get("tiro a puerta", 0))
    goals = int(my_team.get("gol", 0))

    pass_attempts = completed_passes + failed_passes

    return {
        "passing": {
            "completed_passes": completed_passes,
            "failed_passes": failed_passes,
            "pass_success_rate": round(completed_passes / pass_attempts * 100, 1) if pass_attempts else 0.0,
        },
        "shooting": {
            "total_shots": total_shots,
            "shots_on_target": shots_on_target,
            "goals": goals,
            "goals_per_shot": round(goals / total_shots * 100, 1) if total_shots else 0.0,
        },
        "dribbling": {
            "dribbles": int(my_team.get("regate", 0)),
        },
        "ball_retention": {
            "losses": int(my_team.get("perdida", 0)),
        },
    }


def prepare_defensive_statistics_for_ai(teams_df: pd.DataFrame) -> dict:
    my_team_rows = teams_df.loc[teams_df["team"] == "My Team"]
    rival_rows = teams_df.loc[teams_df["team"] == "Rival Team"]
    my_team = my_team_rows.iloc[0] if not my_team_rows.empty else pd.Series(dtype=float)
    rival = rival_rows.iloc[0] if not rival_rows.empty else pd.Series(dtype=float)

    return {
        "defensive_actions": {
            "recoveries": int(my_team.get("recuperacion", 0)),
            "interceptions": int(my_team.get("intercepcion", 0)),
            "clearances": int(my_team.get("despeje", 0)),
        },
        "goalkeeping": {
            "opponent_shots_on_target": int(rival.get("tiro a puerta", 0)),
            "goals_conceded": int(rival.get("gol", 0)),
            "saves": int(my_team.get("parada", 0)),
            "blocks": int(my_team.get("blocaje", 0)),
            "penalty_goals_conceded": int(my_team.get("penalti cometido", 0)),
        },
        "discipline": {
            "fouls_committed": int(my_team.get("falta cometida", 0)),
            "yellow_cards": int(my_team.get("tarjeta amarilla", 0)),
            "red_cards": int(my_team.get("tarjeta roja", 0)),
        },
    }
    