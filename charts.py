from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


TEAM_COLUMN = "team"
MY_TEAM = "My Team"
RIVAL_TEAM = "Rival Team"


def _action_columns(data: pd.DataFrame) -> list[str]:
    return [column for column in data.columns if column not in {TEAM_COLUMN, "player"}]


def _value(data: pd.Series, action: str) -> int:
    return int(data.get(action, 0))


def _team_row(teams_df: pd.DataFrame, team: str) -> pd.Series:
    rows = teams_df[teams_df[TEAM_COLUMN] == team]
    return rows.iloc[0] if not rows.empty else pd.Series(dtype=float)


def generate_tornado_chart(teams_df: pd.DataFrame, output_dir: Path) -> Path:
    actions = _action_columns(teams_df)
    team_row = _team_row(teams_df, MY_TEAM)
    rival_row = _team_row(teams_df, RIVAL_TEAM)
    plot_df = pd.DataFrame({
        "action": actions,
        "my_team": [_value(team_row, action) for action in actions],
        "rival": [_value(rival_row, action) for action in actions],
    }).iloc[::-1]

    fig, ax = plt.subplots(figsize=(11, 9))
    y = np.arange(len(plot_df))
    my_values = plot_df["my_team"].to_numpy()
    rival_values = plot_df["rival"].to_numpy()
    my_normalized = np.sqrt(my_values)
    rival_normalized = np.sqrt(rival_values)

    ax.barh(y, -my_normalized, color="#0047AB", label="Mi Equipo", alpha=0.8)
    ax.barh(y, rival_normalized, color="#B22222", label="Rival", alpha=0.8)
    for index, (my_value, rival_value) in enumerate(zip(my_values, rival_values)):
        if my_value > 0:
            ax.text(-my_normalized[index] - 0.2, index, str(my_value), va="center", ha="right", fontsize=10, fontweight="bold", color="#0047AB")
        if rival_value > 0:
            ax.text(rival_normalized[index] + 0.2, index, str(rival_value), va="center", ha="left", fontsize=10, fontweight="bold", color="#B22222")

    ax.set_yticks(y)
    ax.set_yticklabels([action.capitalize() for action in plot_df["action"]], fontsize=11, fontweight="bold")
    ax.axvline(0, color="black", linewidth=1.5)
    limit = max(my_normalized.max(), rival_normalized.max(), 1) * 1.3
    ax.set_xlim(-limit, limit)
    ax.set_xticks([])
    for spine in ["left", "right", "top", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.set_title("COMPARATIVA DE RENDIMIENTO: MI EQUIPO vs RIVAL", pad=40, fontsize=18, fontweight="bold")

    plot_path = output_dir / "tornado_visual.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path


def generate_radar_chart(teams_df: pd.DataFrame, output_dir: Path) -> Path:
    my_team = _team_row(teams_df, MY_TEAM)
    rival = _team_row(teams_df, RIVAL_TEAM)

    def ratio(numerator: int, denominator: int) -> float:
        return numerator / denominator if denominator > 0 else 0.0

    my_passes = _value(my_team, "pase")
    my_failed_passes = _value(my_team, "pase errado")
    rival_passes = _value(rival, "pase")
    rival_failed_passes = _value(rival, "pase errado")
    my_shots = _value(my_team, "tiro")
    my_shots_on_target = _value(my_team, "tiro a puerta")
    rival_shots = _value(rival, "tiro")
    rival_shots_on_target = _value(rival, "tiro a puerta")
    my_defensive_actions = sum(_value(my_team, action) for action in ["recuperacion", "despeje", "intercepcion"])
    rival_defensive_actions = sum(_value(rival, action) for action in ["recuperacion", "despeje", "intercepcion"])

    my_values = [
        ratio(my_passes, my_passes + my_failed_passes),
        ratio(my_shots_on_target, my_shots + my_shots_on_target),
        ratio(_value(my_team, "gol"), my_shots + my_shots_on_target),
        ratio(_value(my_team, "recuperacion"), my_defensive_actions),
        ratio(_value(my_team, "parada") + _value(my_team, "blocaje"), rival_shots_on_target),
        ratio(_value(my_team, "perdida"), my_passes + _value(my_team, "regate") + my_shots),
    ]
    rival_values = [
        ratio(rival_passes, rival_passes + rival_failed_passes),
        ratio(rival_shots_on_target, rival_shots + rival_shots_on_target),
        ratio(_value(rival, "gol"), rival_shots + rival_shots_on_target),
        ratio(_value(rival, "recuperacion"), rival_defensive_actions),
        ratio(_value(rival, "parada") + _value(rival, "blocaje"), my_shots_on_target),
        ratio(_value(rival, "perdida"), rival_passes + _value(rival, "regate") + rival_shots),
    ]
    labels = [
        "% Pases acertados",
        "% Tiros a puerta",
        "% Goles por tiro",
        "% Recuperaciones por accion defensiva",
        "% Paradas+blocajes sobre tiros rivales",
        "% Perdidas por accion ofensiva",
    ]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    my_plot = my_values + my_values[:1]
    rival_plot = rival_values + rival_values[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    ax.plot(angles, my_plot, color="#0047AB", linewidth=2, label="Mi Equipo")
    ax.fill(angles, my_plot, color="#0047AB", alpha=0.2)
    ax.plot(angles, rival_plot, color="#B22222", linewidth=2, label="Rival")
    ax.fill(angles, rival_plot, color="#B22222", alpha=0.2)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=9, fontweight="bold")
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.grid(color="#cccccc", linestyle="--", linewidth=0.6)
    ax.set_title("COMPARATIVA TELARAÑA: MI EQUIPO vs RIVAL", pad=30, fontsize=14, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.15), frameon=False)

    plot_path = output_dir / "radar_visual.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path


def generate_top3_players_by_action_chart(players_df: pd.DataFrame, output_dir: Path) -> Path:
    selected_metrics = [
        "tiro",
        "tiro a puerta",
        "pase",
        "regate",
        "recuperacion",
        "intercepcion",
        "perdida",
        "falta cometida",
    ]
    metrics = [action for action in selected_metrics if action in players_df.columns]
    rows = max(1, (len(metrics) + 2) // 3)
    fig, axes = plt.subplots(rows, 3, figsize=(18, 5 * rows), squeeze=False)
    axes_flat = axes.flatten()

    for ax, action in zip(axes_flat, metrics):
        counts = players_df[["player", action]].sort_values(action, ascending=False).head(3).sort_values(action)
        counts = counts[counts[action] > 0]
        if counts.empty:
            ax.text(0.5, 0.5, f"{action.capitalize()}\nSin datos", ha="center", va="center")
            ax.axis("off")
            continue

        values = counts[action].tolist()
        ax.barh(counts["player"], values, color=plt.cm.tab10(np.linspace(0, 1, len(values))), edgecolor="black")
        ax.set_title(action.capitalize(), fontsize=10, fontweight="bold")
        ax.set_xlabel("Conteo")
        for index, value in enumerate(values):
            ax.text(value + 0.2, index, str(value), va="center", fontsize=8)

    for ax in axes_flat[len(metrics):]:
        ax.axis("off")
    fig.suptitle("TOP 3 JUGADORES POR ACCIÓN", fontsize=18, fontweight="bold", y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    plot_path = output_dir / "top3_players_by_action.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path


def create_player_stats_table(players_df: pd.DataFrame) -> list[list[object]]:
    metrics = ["pase", "tiro", "tiro a puerta", "gol", "recuperacion", "intercepcion", "regate", "perdida"]
    headers = ["Jugador"] + [action.capitalize() for action in metrics]
    if players_df.empty:
        return [headers, ["-"] + [0] * len(metrics)]

    available_metrics = [action for action in metrics if action in players_df.columns]
    ranked = players_df.copy()
    ranked["total"] = ranked[available_metrics].sum(axis=1) if available_metrics else 0
    ranked = ranked.sort_values("total", ascending=False)

    table_data: list[list[object]] = [headers]
    for _, player in ranked.iterrows():
        table_data.append([player["player"]] + [_value(player, action) for action in metrics])
    return table_data
