from pathlib import Path
import csv
import json
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from utils.config import ACTIONS

class EventLoggerApp:
	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.root.title("Football Event Logger")
		self.root.geometry("920x680")

		self.team_file: Path | None = None
		self.match_file: Path | None = None
		self.players: list[str] = []
		self.player_positions: dict[str, str] = {}
		self.team_name = "My Team"
		self.rival_team_name = "Rival Team"
		self.rival_label = "Equipo rival"
		self.match_headers: list[str] = ["timestamp", "player", "action"]
		self.selected_player: str | None = None
		self.team_file_var = tk.StringVar(value="No team selected")
		self.match_file_var = tk.StringVar(value="No match selected")
		self.selected_player_var = tk.StringVar(value="No player selected")
		self.event_status_var = tk.StringVar(value="Ready")
		self.action_buttons: list[ttk.Button] = []

		self._build_ui()

	def _build_ui(self) -> None:
		container = ttk.Frame(self.root, padding=14)
		container.pack(fill=tk.BOTH, expand=True)

		team_frame = ttk.LabelFrame(container, text="First Event: Select Team")
		team_frame.pack(fill=tk.X, expand=False)

		ttk.Label(team_frame, text="Team file (players):").grid(
			row=0, column=0, padx=8, pady=10, sticky="w"
		)
		ttk.Entry(team_frame, textvariable=self.team_file_var, width=70).grid(
			row=0, column=1, padx=8, pady=10, sticky="ew"
		)
		ttk.Button(team_frame, text="Select Team", command=self.select_team).grid(
			row=0, column=2, padx=8, pady=10
		)

		team_frame.grid_columnconfigure(1, weight=1)

		match_frame = ttk.LabelFrame(container, text="Second Event: Create Match or Load Match")
		match_frame.pack(fill=tk.X, expand=False, pady=(12, 0))

		ttk.Label(match_frame, text="Match file (events CSV):").grid(
			row=0, column=0, padx=8, pady=10, sticky="w"
		)
		ttk.Entry(match_frame, textvariable=self.match_file_var, width=70).grid(
			row=0, column=1, padx=8, pady=10, sticky="ew"
		)
		ttk.Button(match_frame, text="Create Match", command=self.create_match).grid(
			row=0, column=2, padx=6, pady=10
		)
		ttk.Button(match_frame, text="Load Match", command=self.load_match).grid(
			row=0, column=3, padx=6, pady=10
		)

		ttk.Label(match_frame, textvariable=self.event_status_var).grid(
			row=1, column=1, columnspan=3, padx=8, pady=(0, 10), sticky="w"
		)

		match_frame.grid_columnconfigure(1, weight=1)

		capture_frame = ttk.LabelFrame(container, text="Third Event: Capture Events")
		capture_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

		meta_frame = ttk.Frame(capture_frame)
		meta_frame.pack(fill=tk.X, padx=8, pady=(8, 6))

		ttk.Label(meta_frame, text="Selected player:").pack(side=tk.LEFT)
		ttk.Label(meta_frame, textvariable=self.selected_player_var).pack(side=tk.LEFT, padx=(6, 20))
		ttk.Label(meta_frame, textvariable=self.event_status_var).pack(side=tk.LEFT)

		content_frame = ttk.Frame(capture_frame)
		content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

		self.players_frame, self.players_inner = self._create_scrollable_section(content_frame, "Players")
		self.players_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

		self.actions_frame, self.actions_inner = self._create_scrollable_section(content_frame, "Actions")
		self.actions_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

		self._render_action_buttons()

	def _create_scrollable_section(self, parent: ttk.Frame, title: str) -> tuple[ttk.LabelFrame, ttk.Frame]:
		section = ttk.LabelFrame(parent, text=title)

		canvas = tk.Canvas(section, borderwidth=0, highlightthickness=0)
		scrollbar = ttk.Scrollbar(section, orient="vertical", command=canvas.yview)
		inner = ttk.Frame(canvas)

		window_id = canvas.create_window((0, 0), window=inner, anchor="nw")
		canvas.configure(yscrollcommand=scrollbar.set)

		inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
		canvas.bind("<Configure>", lambda e: canvas.itemconfigure(window_id, width=e.width))

		canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		return section, inner

	def select_team(self) -> None:
		teams_dir = Path("teams")
		teams_dir.mkdir(parents=True, exist_ok=True)

		selected = filedialog.askopenfilename(
			title="Select team file",
			initialdir=str(teams_dir.resolve()),
			filetypes=[
				("Team files", "*.json *.csv"),
				("JSON", "*.json"),
				("CSV", "*.csv"),
				("All files", "*.*"),
			],
		)

		if not selected:
			return

		selected_path = Path(selected)
		if not selected_path.exists():
			messagebox.showerror("Error", "Selected file does not exist.")
			return

		self.team_file = selected_path
		self.team_file_var.set(str(selected_path))

		try:
			self.players, self.player_positions = self._load_players(selected_path)
			self.team_name = self._load_team_name(selected_path)
		except Exception as exc:
			messagebox.showerror("Load Error", f"Could not read players: {exc}")
			return

		if not self.players:
			self.event_status_var.set("No players found in team file")
			return

		self._render_player_buttons()

		print("\n=== Team Loaded ===")
		print(f"File: {selected_path}")
		print(f"Total players: {len(self.players)}")
		for idx, player in enumerate(self.players, start=1):
			print(f"{idx:02d}. {player}")

		self.event_status_var.set(f"Team loaded: {len(self.players)} players")

	def create_match(self) -> None:
		if not self.players:
			self.event_status_var.set("Select team first")
			return

		data_dir = Path("data")
		data_dir.mkdir(parents=True, exist_ok=True)

		default_name = f"match_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
		selected = filedialog.asksaveasfilename(
			title="Create match file",
			initialdir=str(data_dir.resolve()),
			initialfile=default_name,
			defaultextension=".csv",
			filetypes=[("CSV", "*.csv"), ("All files", "*.*")],
		)

		if not selected:
			return

		rival_team_name = simpledialog.askstring(
			title="Rival team",
			prompt="Nombre del equipo rival:",
			parent=self.root,
		)
		if not rival_team_name or not rival_team_name.strip():
			self.event_status_var.set("Enter a rival team name")
			return
		self.rival_team_name = rival_team_name.strip()

		match_path = Path(selected)
		self._create_empty_match_csv(match_path, self.team_name, self.rival_team_name)

		self.match_file = match_path
		self.match_headers = self._read_match_headers(match_path)
		self.match_file_var.set(str(match_path))

		print("\n=== Match Created ===")
		print(f"File: {match_path}")
		print("CSV initialized with headers")

		self.event_status_var.set(f"Match created: {match_path.name}")

	def load_match(self) -> None:
		data_dir = Path("data")
		data_dir.mkdir(parents=True, exist_ok=True)

		selected = filedialog.askopenfilename(
			title="Load match file",
			initialdir=str(data_dir.resolve()),
			filetypes=[("CSV", "*.csv"), ("All files", "*.*")],
		)

		if not selected:
			return

		match_path = Path(selected)
		if not match_path.exists():
			messagebox.showerror("Error", "Selected match file does not exist.")
			return

		self.match_file = match_path
		metadata = self._read_match_metadata(match_path)
		self.team_name = metadata.get("team_name", self.team_name)
		self.rival_team_name = metadata.get("rival_name", self.rival_team_name)
		self.match_headers = self._read_match_headers(match_path)
		if "position" not in self.match_headers:
			self._add_match_column(match_path, "position")
			self.match_headers = self._read_match_headers(match_path)
		self.match_file_var.set(str(match_path))

		print("\n=== Match Loaded ===")
		print(f"File: {match_path}")
		print(f"Headers: {self.match_headers}")

		self.event_status_var.set(f"Match loaded: {match_path.name}")

	def _render_player_buttons(self) -> None:
		for child in self.players_inner.winfo_children():
			child.destroy()

		for idx, player in enumerate(self.players):
			btn = ttk.Button(
				self.players_inner,
				text=player,
				command=lambda p=player: self._select_player(p),
				width=24,
			)
			btn.grid(row=idx // 3, column=idx % 3, padx=6, pady=6, sticky="ew")

		rival_row = (len(self.players) + 2) // 3
		ttk.Button(
			self.players_inner,
			text=self.rival_label,
			command=lambda: self._select_player(self.rival_label),
			width=24,
		).grid(row=rival_row, column=0, columnspan=3, padx=6, pady=(10, 6), sticky="ew")

		for col in range(3):
			self.players_inner.grid_columnconfigure(col, weight=1)

	def _render_action_buttons(self) -> None:
		for child in self.actions_inner.winfo_children():
			child.destroy()

		self.action_buttons.clear()
		for idx, action in enumerate(ACTIONS):
			btn = ttk.Button(
				self.actions_inner,
				text=action,
				command=lambda a=action: self._register_event(a),
				width=20,
			)
			btn.grid(row=idx // 2, column=idx % 2, padx=6, pady=6, sticky="ew")
			btn.state(["disabled"])
			self.action_buttons.append(btn)

		for col in range(2):
			self.actions_inner.grid_columnconfigure(col, weight=1)

	def _select_player(self, player: str) -> None:
		self.selected_player = player
		self.selected_player_var.set(player)
		for btn in self.action_buttons:
			btn.state(["!disabled"])
		self.event_status_var.set(f"Player selected: {player}")

	def _register_event(self, action: str) -> None:
		if not self.match_file:
			self.event_status_var.set("No match file selected")
			return

		if not self.selected_player:
			self.event_status_var.set("Select a player first")
			return

		timestamp = datetime.now().isoformat(timespec="seconds")
		position = self._get_player_position(self.selected_player)
		row = self._build_event_row(
			timestamp=timestamp,
			player=self.selected_player,
			action=action,
			position=position,
		)
		with self.match_file.open("a", encoding="utf-8", newline="") as f:
			writer = csv.writer(f)
			writer.writerow(row)

		print("\n=== Event Captured ===")
		print(f"Match: {self.match_file}")
		print(f"{timestamp} | {self.selected_player} | {action}")

		self.event_status_var.set(f"Last event: {self.selected_player} - {action}")

	def _create_empty_match_csv(self, match_path: Path, team_name: str, rival_name: str) -> None:
		with match_path.open("w", encoding="utf-8", newline="") as f:
			writer = csv.writer(f)
			writer.writerow(["# team_name", team_name])
			writer.writerow(["# rival_name", rival_name])
			writer.writerow(["timestamp", "player", "action", "position"])

	def _add_match_column(self, match_path: Path, column_name: str) -> None:
		with match_path.open("r", encoding="utf-8", newline="") as f:
			rows = list(csv.reader(f))

		if not rows:
			rows = [["timestamp", "player", "action", column_name]]
		else:
			header_index = next((idx for idx, row in enumerate(rows) if row and not row[0].startswith("#")), None)
			if header_index is None:
				raise ValueError("Match CSV has no headers")
			rows[header_index].append(column_name)
			for idx in range(header_index + 1, len(rows)):
				rows[idx].append("")

		with match_path.open("w", encoding="utf-8", newline="") as f:
			writer = csv.writer(f)
			writer.writerows(rows)

	def _read_match_headers(self, match_path: Path) -> list[str]:
		with match_path.open("r", encoding="utf-8", newline="") as f:
			reader = csv.reader(f)
			headers = next((row for row in reader if row and not row[0].startswith("#")), None)

		if not headers:
			raise ValueError("Match CSV has no headers")

		normalized = [str(h).strip() for h in headers if str(h).strip()]
		required = {"timestamp", "player", "action"}
		if not required.issubset(set(normalized)):
			raise ValueError("Match CSV must include headers: timestamp, player, action")

		return normalized

	def _read_match_metadata(self, match_path: Path) -> dict[str, str]:
		metadata: dict[str, str] = {}
		with match_path.open("r", encoding="utf-8", newline="") as f:
			for row in csv.reader(f):
				if not row or not row[0].startswith("#"):
					break
				key = row[0][1:].strip()
				if len(row) > 1 and row[1].strip():
					metadata[key] = row[1].strip()
		return metadata

	def _build_event_row(self, timestamp: str, player: str, action: str, position: str = "") -> list[str]:
		values = {
			"timestamp": timestamp,
			"player": player,
			"action": action,
			"position": position,
			"minute": "",
		}
		return [values.get(header, "") for header in self.match_headers]

	def _get_player_position(self, player: str) -> str:
		if player == self.rival_label:
			return "Rival"
		return self.player_positions.get(player, "")

	def _load_players(self, team_file: Path) -> tuple[list[str], dict[str, str]]:
		ext = team_file.suffix.lower()
		if ext == ".json":
			return self._load_players_json(team_file)
		if ext == ".csv":
			return self._load_players_csv(team_file)
		raise ValueError("Supported formats are .json and .csv")

	def _load_players_json(self, team_file: Path) -> tuple[list[str], dict[str, str]]:
		with team_file.open("r", encoding="utf-8") as f:
			data = json.load(f)

		players: list[str] = []
		positions: dict[str, str] = {}

		# Supported format 1: {"players": [{"name": "..."}, ...]}
		if isinstance(data, dict) and isinstance(data.get("players"), list):
			for item in data["players"]:
				if isinstance(item, dict):
					name = str(item.get("name", "")).strip()
					if name:
						players.append(name)
						positions[name] = str(item.get("position", "")).strip()
				elif isinstance(item, str) and item.strip():
					name = item.strip()
					players.append(name)
					positions[name] = ""
			return players, positions

		# Supported format 2: ["Name 1", "Name 2"]
		if isinstance(data, list):
			for item in data:
				if isinstance(item, str) and item.strip():
					name = item.strip()
					players.append(name)
					positions[name] = ""
				elif isinstance(item, dict):
					name = str(item.get("name", "")).strip()
					if name:
						players.append(name)
						positions[name] = str(item.get("position", "")).strip()
			return players, positions

		raise ValueError("Invalid JSON structure for players")

	def _load_players_csv(self, team_file: Path) -> tuple[list[str], dict[str, str]]:
		players: list[str] = []
		positions: dict[str, str] = {}
		with team_file.open("r", encoding="utf-8", newline="") as f:
			reader = csv.DictReader(f)
			if not reader.fieldnames:
				raise ValueError("CSV has no headers")

			headers = {h.lower(): h for h in reader.fieldnames}
			name_header = headers.get("name")
			position_header = headers.get("position")
			if not name_header:
				raise ValueError("CSV must include a 'name' column")

			for row in reader:
				name = str(row.get(name_header, "")).strip()
				if name:
					players.append(name)
					positions[name] = str(row.get(position_header, "")).strip() if position_header else ""

		return players, positions

	def _load_team_name(self, team_file: Path) -> str:
		if team_file.suffix.lower() == ".json":
			with team_file.open("r", encoding="utf-8") as f:
				data = json.load(f)
			if isinstance(data, dict):
				team_name = str(data.get("team_name", "")).strip()
				if team_name:
					return team_name
		return "My Team"


def main() -> None:
	root = tk.Tk()
	app = EventLoggerApp(root)
	root.mainloop()


if __name__ == "__main__":
	main()
