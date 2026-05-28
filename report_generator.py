from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer

from utils.config import ACTIONS

def load_data(csv_path: str | Path) -> pd.DataFrame:
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"El archivo CSV no existe: {csv_file}")

    data = pd.read_csv(csv_file)
    df = data.copy()
    
    # Limpieza y clasificación
    for col in ["player", "action", "position"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Identificación: Mi Equipo vs Rival
    df["team"] = df.apply(
        lambda x: "Rival" if "rival" in str(x.get("player", "")).lower() or "rival" in str(x.get("position", "")).lower() 
        else "Mi Equipo", axis=1
    )
    return df

def generate_tornado_chart(data: pd.DataFrame, output_dir: Path) -> Path:
    # Calculamos las estadísticas para el gráfico
    stats = []
    for action in ACTIONS:
        mi_equipo = int(((data["team"] == "Mi Equipo") & (data["action"] == action)).sum())
        rival = int(((data["team"] == "Rival") & (data["action"] == action)).sum())
        stats.append({"Accion": action, "Mi Equipo": mi_equipo, "Rival": rival})
    
    df_plot = pd.DataFrame(stats).iloc[::-1].reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(11, 9))
    y = np.arange(len(df_plot))
    
    mi_vals = df_plot["Mi Equipo"].values
    ri_vals = df_plot["Rival"].values
    
    # Escala visual (raíz cuadrada) para que los pases no eclipsen al resto
    norm_mi = np.sqrt(mi_vals)
    norm_ri = np.sqrt(ri_vals)
    
    # Dibujo de barras
    ax.barh(y, -norm_mi, color="#0047AB", label="Mi Equipo", alpha=0.8)
    ax.barh(y, norm_ri, color="#B22222", label="Rival", alpha=0.8)

    # Etiquetas con valores reales
    for i, (m, r) in enumerate(zip(mi_vals, ri_vals)):
        if m > 0:
            ax.text(-norm_mi[i] - 0.2, i, str(m), va='center', ha='right', fontsize=10, fontweight='bold', color="#0047AB")
        if r > 0:
            ax.text(norm_ri[i] + 0.2, i, str(r), va='center', ha='left', fontsize=10, fontweight='bold', color="#B22222")

    # Estética del gráfico
    ax.set_yticks(y)
    ax.set_yticklabels(df_plot["Accion"], fontsize=11, fontweight='bold')
    ax.axvline(0, color='black', linewidth=1.5)
    
    # Ajuste de límites para que quepan las etiquetas
    limit = max(norm_mi.max(), norm_ri.max()) * 1.3 if len(df_plot) > 0 else 1
    ax.set_xlim(-limit, limit)
    
    ax.set_xticks([])
    for s in ["left", "right", "top", "bottom"]: ax.spines[s].set_visible(False)
    
    plt.title("COMPARATIVA DE RENDIMIENTO: MI EQUIPO vs RIVAL", pad=40, fontsize=18, fontweight='bold')

    plot_path = output_dir / "tornado_visual.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path

def generate_radar_chart(data: pd.DataFrame, output_dir: Path) -> Path:
    # Estadisticas para grafico telarana (metricas porcentuales)
    def count(team: str, action: str) -> int:
        return int(((data["team"] == team) & (data["action"] == action)).sum())

    def safe_ratio(num: int, den: int) -> float:
        return num / den if den > 0 else 0.0

    mi_pase = count("Mi Equipo", "Pase")
    mi_pase_err = count("Mi Equipo", "Pase errado")
    ri_pase = count("Rival", "Pase")
    ri_pase_err = count("Rival", "Pase errado")

    mi_tiro = count("Mi Equipo", "Tiro")
    mi_tiro_ap = count("Mi Equipo", "Tiro a puerta")
    mi_gol = count("Mi Equipo", "Gol")
    ri_tiro = count("Rival", "Tiro")
    ri_tiro_ap = count("Rival", "Tiro a puerta")
    ri_gol = count("Rival", "Gol")

    mi_rec = count("Mi Equipo", "Recuperacion")
    mi_des = count("Mi Equipo", "Despeje")
    mi_int = count("Mi Equipo", "Intercepcion")
    ri_rec = count("Rival", "Recuperacion")
    ri_des = count("Rival", "Despeje")
    ri_int = count("Rival", "Intercepcion")

    mi_par = count("Mi Equipo", "Parada")
    mi_blo = count("Mi Equipo", "Blocaje")
    ri_par = count("Rival", "Parada")
    ri_blo = count("Rival", "Blocaje")

    mi_reg = count("Mi Equipo", "Regate")
    ri_reg = count("Rival", "Regate")
    mi_per = count("Mi Equipo", "Perdida")
    ri_per = count("Rival", "Perdida")

    mi_total_pases = mi_pase + mi_pase_err
    ri_total_pases = ri_pase + ri_pase_err
    mi_total_tiros = mi_tiro + mi_tiro_ap
    ri_total_tiros = ri_tiro + ri_tiro_ap
    mi_total_def = mi_rec + mi_des + mi_int
    ri_total_def = ri_rec + ri_des + ri_int

    mi_vals = [
        safe_ratio(mi_pase, mi_total_pases),
        safe_ratio(mi_tiro_ap, mi_total_tiros),
        safe_ratio(mi_gol, mi_total_tiros),
        safe_ratio(mi_rec, mi_total_def),
        safe_ratio(mi_par + mi_blo, ri_tiro_ap),
        safe_ratio(mi_per, mi_pase + mi_reg + mi_tiro),
    ]
    ri_vals = [
        safe_ratio(ri_pase, ri_total_pases),
        safe_ratio(ri_tiro_ap, ri_total_tiros),
        safe_ratio(ri_gol, ri_total_tiros),
        safe_ratio(ri_rec, ri_total_def),
        safe_ratio(ri_par + ri_blo, mi_tiro_ap),
        safe_ratio(ri_per, ri_pase + ri_reg + ri_tiro),
    ]

    actions = [
        "% Pases acertados",
        "% Tiros a puerta",
        "% Goles por tiro",
        "% Recuperaciones por accion defensiva",
        "% Paradas+blocajes sobre tiros rivales",
        "% Perdidas por accion ofensiva",
    ]

    angles = np.linspace(0, 2 * np.pi, len(actions), endpoint=False).tolist()
    angles += angles[:1]
    mi_plot = mi_vals + mi_vals[:1]
    ri_plot = ri_vals + ri_vals[:1]

    max_val = 1

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})

    ax.plot(angles, mi_plot, color="#0047AB", linewidth=2, label="Mi Equipo")
    ax.fill(angles, mi_plot, color="#0047AB", alpha=0.2)

    ax.plot(angles, ri_plot, color="#B22222", linewidth=2, label="Rival")
    ax.fill(angles, ri_plot, color="#B22222", alpha=0.2)

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_thetagrids(np.degrees(angles[:-1]), actions, fontsize=9, fontweight="bold")
    ax.set_ylim(0, max_val)
    ax.set_yticks([])
    ax.grid(color="#cccccc", linestyle="--", linewidth=0.6)

    plt.title("COMPARATIVA TELARANA: MI EQUIPO vs RIVAL", pad=30, fontsize=14, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.15, 1.15), frameon=False)

    plot_path = output_dir / "radar_visual.png"
    fig.savefig(plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return plot_path

def build_pdf(plot_path: Path, radar_path: Path, output_pdf: Path):
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(output_pdf), pagesize=A4, margins=(1*cm, 1*cm, 1*cm, 1*cm))
    styles = getSampleStyleSheet()
    
    story = []
    
    # Título del informe
    title_style = ParagraphStyle("Title", parent=styles["Title"], fontSize=26, spaceAfter=30)
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("REPORTE VISUAL DE PARTIDO", title_style))
    story.append(Paragraph("Análisis comparativo de volumen de juego", 
                 ParagraphStyle("Sub", parent=styles["Normal"], alignment=TA_CENTER, fontSize=12, textColor=colors.grey)))
    
    story.append(Spacer(1, 2*cm))

    # El grafico principal (tornado)
    story.append(Image(str(plot_path), width=19*cm, height=13*cm))
    
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("<i>* Los valores indican el número total de eventos registrados.</i>", 
                 ParagraphStyle("Note", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9)))

    story.append(PageBreak())

    # Grafico telarana
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("COMPARATIVA TELARANA ENTRE EQUIPOS", title_style))
    story.append(Spacer(1, 1*cm))
    story.append(Image(str(radar_path), width=17*cm, height=12*cm))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("<i>* Escala porcentual (0 a 1) basada en las cinco metricas definidas.</i>", 
                 ParagraphStyle("Note", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9)))

    doc.build(story)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    args = parser.parse_args()
    
    csv_path = Path(args.csv_file)
    output_path = Path(".") / "reports" / f"Visual_Report_{csv_path.stem}.pdf"

    try:
        data = load_data(csv_path)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            plot_path = generate_tornado_chart(data, Path(tmpdir))
            radar_path = generate_radar_chart(data, Path(tmpdir))
            build_pdf(plot_path, radar_path, output_path)
            
        print(f"✅ Informe visual generado en: {output_path.absolute()}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()