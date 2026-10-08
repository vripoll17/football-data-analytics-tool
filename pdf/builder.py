from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, LongTable, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from charts import create_main_statistics_table


NAVY = colors.HexColor("#12304A")
BLUE = colors.HexColor("#176B87")
RED = colors.HexColor("#C84B4B")
PALE_BLUE = colors.HexColor("#EAF3F6")
PALE_RED = colors.HexColor("#F9ECEA")
MUTED = colors.HexColor("#61717D")
KPI_VALUE_STYLE = ParagraphStyle(
    "KpiValue",
    fontName="Helvetica-Bold",
    fontSize=22,
    leading=22,
    alignment=TA_CENTER,
    textColor=NAVY,
)


def _draw_page_footer(canvas, document) -> None:
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#D7E0E5"))
    canvas.setLineWidth(0.6)
    canvas.line(document.leftMargin, 1.05 * cm, width - document.rightMargin, 1.05 * cm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(document.leftMargin, 0.65 * cm, "Football Data Analytics Tool")
    canvas.drawRightString(width - document.rightMargin, 0.65 * cm, f"Page {document.page}")
    canvas.restoreState()


def _create_offensive_kpis(teams_df: pd.DataFrame) -> Table:
    team_rows = teams_df[teams_df["team"] == "My Team"]
    team_row = team_rows.iloc[0] if not team_rows.empty else pd.Series(dtype=float)
    values = [
        int(team_row.get("regate", 0)),
        int(team_row.get("perdida", 0)),
    ]
    table = Table(
        [
            ["DRIBBLES", "LOSSES"],
            [Paragraph(str(value), KPI_VALUE_STYLE) for value in values],
        ],
        colWidths=[8.25 * cm] * 2,
        rowHeights=[0.7 * cm, 1.05 * cm],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PALE_BLUE),
        ("BACKGROUND", (1, 0), (1, -1), PALE_RED),
        ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
        ("TEXTCOLOR", (0, 1), (-1, 1), NAVY),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTSIZE", (0, 1), (-1, 1), 22),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.white),
        ("INNERGRID", (0, 0), (-1, -1), 2, colors.white),
    ]))
    return table


def _create_defensive_kpis(teams_df: pd.DataFrame) -> Table:
    team_rows = teams_df[teams_df["team"] == "My Team"]
    team_row = team_rows.iloc[0] if not team_rows.empty else pd.Series(dtype=float)
    values = [
        int(team_row.get("falta cometida", 0)),
        int(team_row.get("tarjeta amarilla", 0)),
        int(team_row.get("tarjeta roja", 0)),
    ]
    table = Table(
        [
            ["FOULS COMMITTED", "YELLOW CARDS", "RED CARDS"],
            [Paragraph(str(value), KPI_VALUE_STYLE) for value in values],
        ],
        colWidths=[5.5 * cm] * 3,
        rowHeights=[0.7 * cm, 1.05 * cm],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PALE_RED),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#FFF4D6")),
        ("BACKGROUND", (2, 0), (2, -1), PALE_RED),
        ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
        ("TEXTCOLOR", (0, 1), (-1, 1), NAVY),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTSIZE", (0, 1), (-1, 1), 22),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.white),
        ("INNERGRID", (0, 0), (-1, -1), 2, colors.white),
    ]))
    return table


def _analysis_flowables(ai_analysis: str | None, styles: dict) -> list[Paragraph | Spacer]:
    if not ai_analysis:
        return [Paragraph("No se pudo generar el análisis de IA.", styles["BodyText"])]

    flowables: list[Paragraph | Spacer] = []
    for raw_line in ai_analysis.splitlines():
        line = raw_line.strip()
        if not line:
            flowables.append(Spacer(1, 0.15 * cm))
        elif line.startswith("### "):
            flowables.append(Paragraph(escape(line[4:]), styles["Heading3"]))
        elif line.startswith("## "):
            flowables.append(Paragraph(escape(line[3:]), styles["Heading2"]))
        elif line.startswith("# "):
            flowables.append(Paragraph(escape(line[2:]), styles["Heading1"]))
        elif line.startswith("- ") or line.startswith("* "):
            flowables.append(Paragraph(escape(line[2:]), styles["BodyText"], bulletText="-"))
        else:
            flowables.append(Paragraph(escape(line), styles["BodyText"]))

    return flowables


def _create_dataframe_table(data: pd.DataFrame) -> LongTable:
    cell_style = ParagraphStyle(
        "DetailedDataCell",
        fontName="Helvetica",
        fontSize=5.5,
        leading=6.5,
        alignment=TA_CENTER,
        textColor=NAVY,
    )
    header_style = ParagraphStyle(
        "DetailedDataHeader",
        parent=cell_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )
    headers = [Paragraph(escape(str(column)), header_style) for column in data.columns]
    rows = [
        [Paragraph(escape(str(value)), cell_style) for value in row]
        for row in data.fillna(0).itertuples(index=False, name=None)
    ]
    available_width = A4[0] - 2 * 1.4 * cm
    column_width = available_width / max(len(headers), 1)
    table = LongTable(
        [headers] + rows,
        colWidths=[column_width] * len(headers),
        repeatRows=1,
        splitByRow=1,
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 5.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D7E0E5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PALE_BLUE, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def build_pdf(
    tornado_path: Path,
    radar_path: Path,
    shot_conversion_path: Path,
    pass_accuracy_pie_path: Path,
    defensive_actions_path: Path,
    goalkeeper_actions_path: Path,
    top3_path: Path,
    top3_defensive_path: Path,
    teams_df: pd.DataFrame,
    players_df: pd.DataFrame,
    main_statistics_analysis: str | None,
    game_volume_analysis: str | None,
    game_performance_analysis: str | None,
    offensive_analysis: str | None,
    defensive_analysis: str | None,
    strenghts_weaknesses_recommendations_analysis: str | None,
    output_pdf: Path,
) -> None:
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(output_pdf), pagesize=A4, rightMargin=1.4 * cm, leftMargin=1.4 * cm, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=25, leading=29, alignment=TA_LEFT, textColor=NAVY, spaceAfter=12)
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=NAVY, spaceBefore=8, spaceAfter=9)
    subsection_style = ParagraphStyle("Subsection", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=BLUE, spaceBefore=5, spaceAfter=6)
    note_style = ParagraphStyle("Note", parent=styles["Normal"], alignment=TA_CENTER, fontSize=8.5, leading=11, textColor=MUTED)
    score_style = ParagraphStyle("Score", parent=styles["Heading2"], alignment=TA_CENTER, fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=colors.white)

    my_team_goals = int(teams_df.loc[teams_df["team"] == "My Team", "gol"].sum())
    rival_goals = int(teams_df.loc[teams_df["team"] == "Rival Team", "gol"].sum())

    main_statistics = Table(
        create_main_statistics_table(teams_df),
        colWidths=[3.4 * cm, 1.6 * cm, 1.9 * cm, 2.1 * cm, 1.6 * cm, 1.9 * cm, 1.9 * cm, 1.4 * cm],
    )

    main_statistics.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D7E0E5")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PALE_BLUE, colors.white]),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    score_card = Table([[Paragraph(f"MY TEAM  <font size=25>{my_team_goals}</font>  -  <font size=25>{rival_goals}</font>  RIVAL TEAM", score_style)]], colWidths=[17.2 * cm], rowHeights=[1.25 * cm])
    score_card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (-1, -1), 0, NAVY),
    ]))
    story = [
        Spacer(1, 0.5 * cm),
        Paragraph("VISUAL REPORT", title_style),
        score_card,
        Spacer(1, 0.65 * cm),
        Paragraph("1. Main team statistics", section_style),
        Spacer(1, 0.15 * cm),
        main_statistics,
        Spacer(1, 0.55 * cm),
        Paragraph("1.1. Key findings", subsection_style),
        Spacer(1, 0.2 * cm),
        *_analysis_flowables(main_statistics_analysis, styles),
        PageBreak(),
        Spacer(1, 0.5 * cm),
        Paragraph("2. Team comparison", section_style),
        Spacer(1, 0.3 * cm),
        Paragraph("2.1. Game volume", subsection_style),
        Spacer(1, 0.2 * cm),
        Image(str(tornado_path), width=19 * cm, height=13 * cm),
        Spacer(1, 0.5 * cm),
        *_analysis_flowables(game_volume_analysis, styles),
        PageBreak(),
        Paragraph("2.2. Game performance", subsection_style),
        Spacer(1, 0.5 * cm),
        Image(str(radar_path), width=17 * cm, height=12 * cm),
        Spacer(1, 1 * cm),
        *_analysis_flowables(game_performance_analysis, styles),
        Spacer(1, 1 * cm),
        Paragraph("<i>* Escala porcentual (0 a 1) basada en las métricas definidas.</i>", note_style),
        PageBreak(),
        Paragraph("3. Offensive analysis", section_style),
        Spacer(1, 0.65 * cm),
        Image(str(shot_conversion_path), width=17 * cm, height=10 * cm),
        Spacer(1, 0.8 * cm),
        Image(str(pass_accuracy_pie_path), width=12 * cm, height=10 * cm),
        Spacer(1, 0.8 * cm),
        _create_offensive_kpis(teams_df),
        Spacer(1, 0.5 * cm),
        Paragraph("3.1. Offensive findings", subsection_style),
        Spacer(1, 0.2 * cm),
        *_analysis_flowables(offensive_analysis, styles),
        PageBreak(),
        Paragraph("4. Defensive analysis", section_style),
        Spacer(1, 0.4 * cm),
        Image(str(defensive_actions_path), width=17 * cm, height=10 * cm),
        Spacer(1, 0.8 * cm),
        Image(str(goalkeeper_actions_path), width=17 * cm, height=10 * cm),
        Spacer(1, 0.8 * cm),
        _create_defensive_kpis(teams_df),
        Spacer(1, 0.5 * cm),
        Paragraph("4.1. Defensive findings", subsection_style),
        Spacer(1, 0.2 * cm),
        *_analysis_flowables(defensive_analysis, styles),
        PageBreak(),
        Paragraph("5. Player statistics", section_style),
        Spacer(1, 0.4 * cm),
        Paragraph("5.1. Top 3 players for offensive action", subsection_style),
        Image(str(top3_path), width=18 * cm, height=12 * cm),
        PageBreak(),
        Paragraph("5.2. Top 3 players for defensive action", subsection_style),
        Image(str(top3_defensive_path), width=18 * cm, height=12 * cm),
        PageBreak(),
        Paragraph("6. Strengths, weaknesses and recommendations", section_style),
        Spacer(1, 0.3 * cm),
        *_analysis_flowables(strenghts_weaknesses_recommendations_analysis, styles),
        PageBreak(),
        Paragraph("7. Detailed data", section_style),
        Spacer(1, 0.3 * cm),
        Paragraph("7.1. Teams data", subsection_style),
        _create_dataframe_table(teams_df),
        Spacer(1, 0.5 * cm),
        Paragraph("7.2.Players data", subsection_style),
        _create_dataframe_table(players_df),
    ]
    document.build(story, onFirstPage=_draw_page_footer, onLaterPages=_draw_page_footer)
