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


def calculate_match_stats(df):
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

    return teams_df