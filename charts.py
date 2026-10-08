from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils.data_processing import calculate_radar_metrics, get_team_names


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


def _visible_team_names(teams_df: pd.DataFrame) -> tuple[str, str]:
    return get_team_names(teams_df)


def create_main_statistics_table(teams_df: pd.DataFrame) -> list[list[object]]:
    main_metrics = [
        ("Goles", "gol"),
        ("Tiros", "tiro"),
        ("Tiros a puerta", "tiro a puerta"),
        ("Pases", "pase"),
        ("Recuperaciones", "recuperacion"),
        ("Intercepciones", "intercepcion"),
        ("Pérdidas", "perdida"),
    ]

    def team_metric_row(team: str) -> list[object]:
        team_row = _team_row(teams_df, team)
        team_name, rival_name = _visible_team_names(teams_df)
        display_name = team_name if team == MY_TEAM else rival_name
        return [display_name] + [int(team_row.get(column, 0)) for _, column in main_metrics]

    return [
        ["Equipo"] + [label for label, _ in main_metrics],
        team_metric_row(MY_TEAM),
        team_metric_row(RIVAL_TEAM),
    ]


def generate_tornado_chart(teams_df: pd.DataFrame, output_dir: Path) -> Path:
    team_name, rival_name = _visible_team_names(teams_df)
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

    ax.barh(y, -my_normalized, color="#0047AB", label=team_name, alpha=0.8)
    ax.barh(y, rival_normalized, color="#B22222", label=rival_name, alpha=0.8)
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
    ax.set_title(f"COMPARATIVA DE RENDIMIENTO: {team_name} vs {rival_name}", pad=40, fontsize=18, fontweight="bold")
    ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, 1.08), ncol=2)

    plot_path = output_dir / "tornado_visual.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path


def generate_defensive_actions_chart(teams_df: pd.DataFrame, output_dir: Path) -> Path:
    team_name, _ = _visible_team_names(teams_df)
    actions = ["recuperacion", "despeje", "intercepcion"]
    action_labels = ["Recuperaciones", "Despejes", "Intercepciones"]
    my_team = _team_row(teams_df, MY_TEAM)
    my_values = [_value(my_team, action) for action in actions]

    positions = np.arange(len(actions))
    fig, ax = plt.subplots(figsize=(9, 5.5))
    my_bars = ax.bar(positions, my_values, color="#176B87", width=0.55)

    ax.bar_label(my_bars, padding=3, fontsize=9)
    ax.set_xticks(positions)
    ax.set_xticklabels(action_labels)
    ax.set_ylabel("Número de acciones")
    ax.set_title(f"VOLUMEN DE ACCIONES DEFENSIVAS - {team_name}", fontsize=15, fontweight="bold")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()

    plot_path = output_dir / "defensive_actions_visual.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path


def generate_goalkeeper_actions_chart(teams_df: pd.DataFrame, output_dir: Path) -> Path:
    team_name, rival_name = _visible_team_names(teams_df)
    my_team = _team_row(teams_df, MY_TEAM)
    rival = _team_row(teams_df, RIVAL_TEAM)
    labels = [f"Tiros a puerta de {rival_name}", "Paradas", "Blocajes", f"Goles de {rival_name}"]
    values = [
        _value(rival, "tiro a puerta"),
        _value(my_team, "parada"),
        _value(my_team, "blocaje"),
        _value(rival, "gol"),
    ]

    positions = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.barh(positions, values, color=["#B22222", "#176B87", "#176B87", "#B22222"])

    ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_yticks(positions)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Número de acciones")
    ax.set_title(f"RENDIMIENTO DEL PORTERO - {team_name}", fontsize=15, fontweight="bold")
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    fig.tight_layout()

    plot_path = output_dir / "goalkeeper_actions_visual.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path


def generate_radar_chart(teams_df: pd.DataFrame, output_dir: Path) -> Path:
    team_name, rival_name = _visible_team_names(teams_df)
    my_values, rival_values, labels = calculate_radar_metrics(teams_df)

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    my_plot = my_values + my_values[:1]
    rival_plot = rival_values + rival_values[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    ax.plot(angles, my_plot, color="#0047AB", linewidth=2, label=team_name)
    ax.fill(angles, my_plot, color="#0047AB", alpha=0.2)
    ax.plot(angles, rival_plot, color="#B22222", linewidth=2, label=rival_name)
    ax.fill(angles, rival_plot, color="#B22222", alpha=0.2)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=9, fontweight="bold")
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.grid(color="#cccccc", linestyle="--", linewidth=0.6)
    ax.set_title(f"COMPARATIVA TELARAÑA: {team_name} vs {rival_name}", pad=30, fontsize=14, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.15), frameon=False)

    plot_path = output_dir / "radar_visual.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path


def generate_shot_conversion_chart(teams_df: pd.DataFrame, output_dir: Path) -> Path:
    team_name, _ = _visible_team_names(teams_df)
    my_team = _team_row(teams_df, MY_TEAM)

    my_shots_on_target = _value(my_team, "tiro a puerta")
    my_total_shots = _value(my_team, "tiro") + my_shots_on_target
    my_goals = _value(my_team, "gol")

    levels = ["Tiros", "A puerta", "Goles"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(
        levels,
        [my_total_shots, my_shots_on_target, my_goals],
        marker="o",
        label=team_name,
        color="tab:red",
    )
    ax.set_title(f"Conversión de tiros - {team_name}")
    ax.set_ylabel("Conteo")

    plot_path = output_dir / "shot_conversion_visual.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path


def generate_pass_accuracy_pie_chart(teams_df: pd.DataFrame, output_dir: Path) -> Path:
    team_name, _ = _visible_team_names(teams_df)
    labels = ["Pases", "Pases errados"]
    colors = ["#0047AB", "#B22222"]

    team_row = _team_row(teams_df, MY_TEAM)
    passes = _value(team_row, "pase")
    failed_passes = _value(team_row, "pase errado")
    values = [passes, failed_passes]

    fig, ax = plt.subplots(figsize=(6, 5))
    if sum(values) == 0:
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
        ax.axis("off")
    else:
        ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": "white"},
        )
    ax.set_title(team_name)

    fig.suptitle("PORCENTAJE DE PASES Y PASES ERRADOS", fontsize=16, fontweight="bold")
    fig.tight_layout()

    plot_path = output_dir / "pass_accuracy_pie_visual.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path


def _generate_top3_players_chart(
    players_df: pd.DataFrame,
    output_dir: Path,
    actions: list[str],
    title: str,
    filename: str,
    columns: int = 3,
) -> Path:
    metrics = [action for action in actions if action in players_df.columns]
    rows = max(1, (len(metrics) + columns - 1) // columns)
    fig, axes = plt.subplots(rows, columns, figsize=(6 * columns, 5 * rows), squeeze=False)
    axes_flat = axes.flatten()

    for ax, action in zip(axes_flat, metrics):
        counts = players_df[["player", action]].sort_values(action, ascending=False).head(3).sort_values(action)
        counts = counts[counts[action] > 0]
        if counts.empty:
            ax.text(0.5, 0.5, f"{action.capitalize()}\nSin datos", ha="center", va="center")
            ax.axis("off")
            continue

        values = counts[action].tolist()
        bars = ax.bar(counts["player"], values, color=plt.cm.tab10(np.linspace(0, 1, len(values))), edgecolor="black")
        ax.set_title(action.capitalize(), fontsize=10, fontweight="bold")
        ax.set_ylabel("Conteo")
        ax.tick_params(axis="x", labelrotation=30)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.2, str(value), ha="center", fontsize=8)

    for ax in axes_flat[len(metrics):]:
        ax.axis("off")
    fig.suptitle(title, fontsize=18, fontweight="bold", y=1.02)
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    plot_path = output_dir / filename
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path


def generate_top3_players_offensive_chart(players_df: pd.DataFrame, output_dir: Path) -> Path:
    return _generate_top3_players_chart(
        players_df,
        output_dir,
        ["tiro", "tiro a puerta", "pase", "pase errado", "regate", "perdida"],
        "TOP 3 JUGADORES EN ACCIONES OFENSIVAS",
        "top3_players_offensive.png",
    )


def generate_top3_players_defensive_chart(players_df: pd.DataFrame, output_dir: Path) -> Path:
    return _generate_top3_players_chart(
        players_df,
        output_dir,
        ["recuperacion", "despeje", "intercepcion", "falta cometida"],
        "TOP 3 JUGADORES EN ACCIONES DEFENSIVAS",
        "top3_players_defensive.png",
        columns=2,
    )


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
