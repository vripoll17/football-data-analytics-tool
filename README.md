# Football Data Analytics Tool

A tool designed for coaches and football analysts to record match events in real time and generate a visual comparison report of a team’s performance against its opponent.

This project combines a graphical interface for logging match actions and a PDF report generator that creates comparative charts to analyze team performance.

## What does this project do?

- Records match events from a graphical interface
- Allows loading a team file with players and positions
- Creates or loads a match CSV file
- Stores events with timestamp, player, action, and position
- Generates a visual dashboard-style PDF with:
  - tornado chart for action comparison
  - radar chart comparing the team and the rival

## Main features

### 1. Event logger
The main application is in [log_data.py](log_data.py). It allows:

- selecting a team file in JSON or CSV format
- creating a new match file in CSV format
- loading an existing match file
- choosing a player and an action from the predefined list
- automatically registering events with a timestamp

### 2. Visual report generation
The report generator is in [report_generator.py](report_generator.py). From a match CSV, it creates a PDF with two charts:

- comparison of action volume by team
- radar analysis with relative performance metrics

### 3. Action configuration
Available actions are centralized in [utils/config.py](utils/config.py). This makes it easy to expand or adjust the event catalog.

## Project structure

```text
football-data-analytics-tool/
├── data/                      # CSV files generated for matches
├── notebooks/                 # analysis / exploration notebooks
├── reports/                   # generated PDFs
├── teams/                     # example team files in JSON/CSV
├── utils/
│   ├── __init__.py
│   ├── config.py              # list of possible actions
│   └── math.py                # simple math utilities
├── log_data.py                # graphical interface for event logging
├── report_generator.py        # PDF report generation with charts
├── requirements.txt           # project dependencies
├── README.md                  # project documentation
└── .gitignore                 # git configuration (if present in the repo)
```

## Requirements

You need Python 3.10+ and the project dependencies:

```bash
pip install -r requirements.txt
```

Main dependencies:

- matplotlib
- pandas
- reportlab
- numpy
- ipykernel
- notebook

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd football-data-analytics-tool
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

3. Install the requirements:

```bash
pip install -r requirements.txt
```

## How to use the logging app

Run:

```bash
python log_data.py
```

### Recommended workflow

1. Select a team file
   - accepts JSON or CSV
   - example available in [teams/test_team.json](teams/test_team.json)

2. Create or load a match
   - creating a match generates a new CSV inside the data/ folder

3. Select a player
   - you can also choose the option "Equipo rival" (Rival Team)

4. Click an action
   - for example: Pass, Shot, Goal, Recovery, Foul committed, etc.

5. Each event is saved with:
   - timestamp
   - player
   - action
   - position

The resulting CSV is then used for analysis and report generation.

## Team file format

### JSON

```json
{
  "team_name": "Barcelona",
  "players": [
    {"name": "Pedri", "position": "Midfielder"},
    {"name": "Lamine Yamal", "position": "Forward"},
    {"name": "Szczesny", "position": "Goalkeeper"}
  ]
}
```

### CSV

```csv
name,position
Pedri,Midfielder
Lamine Yamal,Forward
Szczesny,Goalkeeper
```

## How to generate the PDF report

Once you have the match CSV, run:

```bash
python report_generator.py data/<match_name>.csv
```

This generates a PDF in the `reports/` folder with the name:

```text
reports/Visual_Report_<match_name>.pdf
```

Example:

```bash
python report_generator.py data/barca_madrid.csv
```

## Supported actions

The project includes a base set of events defined in [utils/config.py](utils/config.py), such as:

- Goal
- Shot
- Shot on target
- Pass
- Failed pass
- Dribble
- Loss of possession
- Recovery
- Clearance
- Interception
- Foul committed
- Foul received
- Penalty committed
- Penalty received
- Penalty saved
- Yellow card
- Red card
- Save
- Block

## Generated output

The visual report includes:

- comparative chart of action frequency by team
- radar chart with percentage-based performance indicators
- PDF export ready for analysis or presentation

## Use cases

This project is useful for:

- coaches who want to log match events without relying on complex tools
- quick tactical analysis of a session or match
- preparation of visual reports for post-match review
- comparison between the home team and the rival

## Current limitations

- the logic is designed for match analysis events, not for a full tracking system
- the rival team is managed as a special entity inside the app
- the visualization is focused on quick and educational comparative analysis

## Possible future improvements

- add editing of logged events
- include minute and duration of each event
- support more advanced metrics
- export to Excel or JSON
- improve the user interface
- add filters by player, match phase, or field zone

## Credits

Project developed for football performance analysis and visual report generation from manually captured data.

## Quick note

If you want, I can also create a more polished GitHub-style README with:

- badges
- screenshots
- real usage examples
- architecture and roadmap sections
- a more professional open-source presentation
