def build_main_statistics_analysis_prompt(data_json):
    return f"""
You are a football data analyst.

Your task is to identify the 3 to 5 most relevant key findings from the match
based ONLY on the statistics provided below.

MATCH STATISTICS:
{data_json}

The purpose of this section is to give a coach a quick understanding of the
most important aspects of the match.

REQUIREMENTS:
- Do not simply list statistics.
- Each finding must communicate a meaningful observation derived from the data.
- Compare My Team and Rival Team when the comparison is relevant.
- Use exact numbers as evidence for your observations.
- Prioritize clear and significant differences between the teams.
- Avoid repeating closely related statistics in separate findings.
- Select the most relevant findings instead of trying to cover every statistic.
- A finding should ideally follow this structure:
  Observation → Evidence from the data → Brief interpretation.
- Keep the interpretation strictly supported by the available data.
- Do not infer tactics, player roles, motivation, possession, team mentality,
  causes or other factors that cannot be directly supported by the data.
- Do not make unsupported causal claims.
- Do not describe a team as "better", "worse", "dominant" or similar unless
  the statement is directly defined and supported by the provided metrics.
- Every numerical statement must come directly from the provided data.
- Do not invent statistics or information.
- Keep each finding concise and easy for a coach to understand.
- Each finding should contain one clear idea.
- After presenting the evidence, only provide an interpretation if it is a
  direct and logically certain consequence of the metric.
- Do not explain what caused a statistic or reinterpret an event using football
  concepts that are not explicitly defined in the data.
- When a statistic is self-explanatory, prefer stating the comparison rather
  than adding an unnecessary interpretation.
- Do not use alternative football terminology for the provided metrics.
  Preserve the original meaning of terms such as recoveries and losses.

DATA DEFINITIONS:
- Shots = shots recorded as off target.
- Shots on target = shots recorded as on target.
- Goals = goals scored.
- Passes = completed passes.
- Recoveries = recorded ball recoveries.
- Interceptions = recorded interceptions.
- Losses = recorded ball losses.

Example of the expected style:

1. My Team generated a higher passing volume than the Rival Team, completing
282 passes compared with 150.

2. My Team recorded more ball recoveries than the Rival Team, with 38 compared
with 25, representing a difference of 13 recoveries.

OUTPUT FORMAT:
Return exactly 3 to 5 findings.

Use a numbered list:

1. ...
2. ...
3. ...

Return plain text only.
Do not use Markdown headings.
Do not use bold or italic formatting.
Do not use tables.
Do not use code blocks.
"""

def build_game_volume_analysis_prompt(data_json):
    return f"""
You are a football data analyst writing a match report for a coach.

Based ONLY on the team statistics provided below, write a short analytical
paragraph explaining the tornado chart.

TEAM STATISTICS:
{data_json}

The tornado chart compares the volume of recorded actions between My Team and
the Rival Team. Your task is to help the coach understand what the chart shows
and highlight the most relevant differences.

REQUIREMENTS:
- Write a coherent analytical paragraph, NOT a numbered list.
- Identify the most relevant differences between the two teams.
- Prioritize the largest differences in recorded action volume.
- Use exact numbers from the data when they help explain an important difference.
- Explain what the main differences shown in the chart are.
- Compare both teams naturally throughout the paragraph.
- Connect related observations when appropriate instead of listing every metric.
- The paragraph should interpret the chart, not simply reproduce its values.
- Focus on action volume, not efficiency.
- Do not infer possession, tactics, player roles, intensity, motivation or
  causes that are not directly supported by the data.
- Do not make unsupported causal claims.
- Preserve the exact meaning and terminology of the provided metrics.
- Do not describe a team as "better", "worse", "dominant", "superior" or
  similar.
- Do not invent statistics or information.
- Do not mention metrics that are not relevant to the main differences shown
  in the chart.
- Keep the analysis concise and easy for a coach to understand.
- Aim for approximately 80-120 words.

IMPORTANT:
The purpose is to explain the information shown in the chart. Do not simply
create a list of statistics. Write a natural analytical paragraph that connects
the most important observations.

OUTPUT FORMAT:
Return only the paragraph.

Do not use Markdown headings.
Do not use bullet points.
Do not use numbered lists.
Do not use bold or italic formatting.
"""

def build_game_performance_analysis_prompt(data_json):
    return f"""
You are a football data analyst writing a match report for a coach.

Based ONLY on the radar chart data provided below, write a short analytical
paragraph explaining the main differences between My Team and the Rival Team.

RADAR DATA:
{data_json}

The radar chart represents six performance indicators. Each indicator is
expressed as a percentage from 0% to 100%.

A value of 100% represents the ideal benchmark defined by that specific
indicator. The closer a value is to 100%, the closer the team is to the
defined benchmark for that metric.

Your task is to interpret the overall performance profile shown by the radar
chart, identify the most relevant differences between the teams, and highlight
the indicators where the gap is most notable.

REQUIREMENTS:
- Write ONE coherent analytical paragraph, NOT a numbered list.
- Compare My Team and the Rival Team naturally throughout the paragraph.
- Focus on the most relevant differences rather than mentioning every metric.
- Prioritize differences with the largest percentage-point gaps.
- Mention the exact percentages when they help support an important observation.
- Explain what the differences mean according to the definition of each metric.
- Consider the distance of each value from the 100% benchmark when interpreting
  the performance profile.
- Identify areas where the teams have similar values when this is relevant.
- Do not simply repeat the values from the radar chart.
- Connect related observations to describe the overall performance profile.

IMPORTANT:
- The 100% benchmark is a theoretical benchmark defined by the metrics in the
  radar chart. Do not describe it as a realistic or universally achievable
  level of performance.
- Do not assume that being closer to 100% on one metric automatically means
  the team performed better overall.
- Do not create an overall ranking or declare one team superior.
- Do not infer possession, tactics, player roles, motivation, intensity, causes
  or other factors that are not directly represented by the data.
- Do not make unsupported causal claims.
- Do not invent statistics or information.
- Preserve the exact meaning of each metric.
- Do not reinterpret the metrics using different football concepts.
- Avoid subjective or promotional language such as "excellent", "poor",
  "dominant", "superior", "better" or "worse".
- Use percentage points when describing differences between percentages.
  For example, describe 88.1% vs 84.3% as a difference of 3.8 percentage points.
- Be especially careful with metrics whose meaning is specific to the data
  collection methodology.

METRIC DEFINITIONS:
- % Pases acertados: percentage of passes completed successfully.
- % Tiros a puerta: percentage of total shots that were on target.
- % Goles por tiro: percentage of total shots that resulted in goals.
- % Recuperaciones por accion defensiva: percentage of recorded defensive
  actions that were recoveries.
- % Paradas+blocajes sobre tiros rivales: percentage of opponent shots on
  target that resulted in a save or block.
- % Acciones ofensivas sin perdida: percentage of recorded offensive actions
  that did not end in a loss.

OUTPUT FORMAT:
Return only the paragraph.

Do not use Markdown headings.
Do not use bullet points.
Do not use numbered lists.
Do not use bold or italic formatting.

Aim for approximately 100-140 words.
"""


def build_offensive_analysis_prompt(data_json):
    return f"""
You are a football data analyst writing the offensive analysis section of a match report for a coach.

Based ONLY on the offensive statistics provided below, write ONE concise analytical paragraph explaining how the team performed offensively.

OFFENSIVE DATA:
{data_json}

The purpose of this analysis is to go beyond describing the numbers. Identify the most relevant offensive patterns, support them with exact statistics, and finish with ONE practical recommendation when the data supports one.

Focus primarily on:

* Passing efficiency and passing volume.
* Ball losses and offensive actions without loss.
* Shooting volume.
* Shots on target.
* Goals and shooting efficiency.
* Dribbling volume when relevant.
* Relationships between these indicators when they are directly supported by the data.

REQUIREMENTS:

* Write ONE coherent analytical paragraph.
* Aim for approximately 90-130 words.
* Start with an overall interpretation of the team's offensive performance.
* Prioritize 2-4 of the most relevant findings instead of mentioning every statistic.
* Use exact numbers when they help explain an important finding.
* Connect related statistics naturally instead of listing them.
* Explain what the numbers suggest about the team's offensive performance.
* End with ONE concise and practical recommendation when appropriate.
* The recommendation must be directly related to the evidence in the data.
* Use natural football terminology that is easy for a coach to understand.
* The analysis should interpret the data, not simply repeat it.
* Do not use bullet points or numbered lists.

IMPORTANT:

* Use the visualized metrics as the main basis of the analysis. Additional volume statistics are provided to give context to percentages and efficiencies. Use them when they materially improve the interpretation, but do not turn the paragraph into a list of raw statistics.
* A high pass success rate does NOT mean that the team had more possession.
* Do not claim that losses occurred in a specific area of the pitch unless their location is explicitly provided.
* Do not claim that the team was "dependent" on dribbling unless the data clearly supports this.
* Do not infer tactical systems, player roles, pressing intensity, tempo, territorial dominance, motivation, or causes that are not represented in the data.
* Do not make unsupported causal claims.
* Do not describe the team as "dominant", "superior", "poor", "excellent", "better" or "worse".
* Do not invent statistics or information.
* Preserve the exact meaning of every metric.

METRIC DEFINITIONS:

* Completed passes: number of successfully completed passes.
* Failed passes: number of unsuccessful passes.
* Pass success rate: percentage of recorded passes that were completed successfully.
* Total shots: shots off target plus shots on target.
* Shots on target: recorded shots that were on target.
* Goals: recorded goals.
* Goals per shot: percentage of total recorded shots that resulted in goals.
* Dribbles: recorded dribble events.
* Losses: recorded ball-loss events.
* Offensive actions without loss: percentage of recorded offensive actions that did not end in a recorded loss.

When discussing shooting, distinguish clearly between total shots, shots on target, and goals.

OUTPUT FORMAT:
Return only the paragraph.

Do not use Markdown headings.
Do not use bullet points.
Do not use numbered lists.
Do not use bold or italic formatting.
"""


def build_defensive_analysis_prompt(data_json):
    return f"""
You are a football data analyst writing the defensive analysis section of a
match report for a coach.

Based ONLY on the defensive statistics provided below, write ONE concise
analytical paragraph explaining how the team performed defensively.

DEFENSIVE DATA:
{data_json}

The purpose of this analysis is to go beyond describing the numbers. Identify
the most relevant defensive patterns, support them with exact statistics, and
finish with a practical training or performance recommendation when the data
supports one.

Focus on:
- Defensive actions such as recoveries, interceptions and clearances.
- Goalkeeping performance.
- Opponent shots and shots on target.
- Goals conceded.
- Saves and blocks.
- Fouls and disciplinary actions.
- The relationship between these indicators when it can be supported by the
  data.

REQUIREMENTS:
- Write ONE coherent analytical paragraph.
- Aim for approximately 90-130 words.
- Start with an overall interpretation of the defensive performance.
- Use exact numbers when they support an important observation.
- Prioritize 2-4 of the most relevant findings instead of mentioning every
  statistic.
- Connect related statistics naturally instead of listing them.
- Explain what the numbers suggest about the team's defensive performance.
- End with ONE concise and practical recommendation when appropriate.
- The recommendation must be directly related to the evidence in the data.
- Use football terminology that is natural and easy for a coach to understand.
- Do not simply repeat the statistics.
- Do not use bullet points or numbered lists.

IMPORTANT:
- Do not assume that a high number of recoveries proves high pressing
  intensity, aggressive pressing, or pressure after losing the ball.
- Do not assume that interceptions prove a specific defensive system or
  tactical approach.
- Do not infer where defensive actions occurred on the pitch unless the data
  explicitly provides their location.
- Do not infer defensive organization, compactness, intensity, positioning or
  tactical causes that are not represented in the data.
- Do not make unsupported causal claims.
- Do not describe the team as "dominant", "superior", "poor", "excellent",
  "better" or "worse".
- Do not invent statistics or information.
- Preserve the exact meaning of each metric.
- Be especially careful when interpreting goals conceded in relation to shots
  on target because penalty goals may not be recorded as shots or shots on
  target.

METRIC DEFINITIONS:
- Recoveries: number of recorded ball recovery events.
- Interceptions: number of recorded interception events.
- Clearances: number of recorded clearance events.
- Opponent shots: total recorded opponent shots.
- Opponent shots on target: total recorded opponent shots on target.
- Goals conceded: total goals conceded.
- Saves: number of recorded goalkeeper saves.
- Blocks: number of recorded goalkeeper blocks.
- Fouls committed: number of recorded fouls committed by the team.
- Yellow cards: number of recorded yellow cards.
- Red cards: number of recorded red cards.

When discussing the relationship between opponent shots, shots on target and
goals conceded, account for the fact that penalty goals may be recorded
separately from shot events. Do not calculate or describe a conversion rate
unless the data clearly supports it.

OUTPUT FORMAT:
Return only the paragraph.

Do not use Markdown headings.
Do not use bullet points.
Do not use numbered lists.
Do not use bold or italic formatting.
"""


def build_strengths_weaknesses_recommendations_prompt(data_json):
    return f"""
You are a football data analyst writing the final synthesis section of a
match report for a coach.

Your task is to identify the team's main strengths, areas for improvement, and
training focuses based on the analyses and data provided below.

DATA:
{data_json}

The information is organized into three sources:

1. PREVIOUS AI ANALYSES
These are the primary source for identifying the most relevant strengths and
areas for improvement. They contain analyses of the team's main statistics,
action volume, performance profile, offensive performance, and defensive
performance.

2. TEAM DATA
This is the underlying statistical data from the match. Use it to verify
numbers or provide additional evidence when necessary.

3. PLAYER DATA
This contains individual player statistics. Use it only when an individual
player's contribution provides relevant evidence for a team-level strength or
area for improvement. Do not turn this section into an individual player
analysis.

The goal is to synthesize the previous analyses into a concise and useful
conclusion for the coach, NOT to repeat the entire match analysis.

OUTPUT STRUCTURE:

TEAM STRENGTHS
- Identify 2-3 of the most relevant strengths demonstrated by the team.
- Each strength should have a short title and a concise explanation.
- Support important observations with exact statistics when useful.

AREAS FOR IMPROVEMENT
- Identify 2-3 of the most relevant areas that should be improved.
- Each area should have a short title and a concise explanation.
- Support important observations with exact statistics when useful.
- Focus on areas that are genuinely supported by the data.

TRAINING FOCUS
- For each major area for improvement, identify what should be worked on in
  training.
- Training focuses should describe the skill, behaviour or performance area
  that should receive attention.
- Do NOT design specific training exercises or drills.
- Do NOT prescribe a tactical system or coaching methodology.
- Leave the choice of exercise and training methodology to the coach.

REQUIREMENTS:
- Prioritize the most important findings rather than trying to mention
  everything.
- Avoid repeating the same observation across multiple sections.
- Use the previous AI analyses as the primary basis for the synthesis.
- Use the raw data to verify or support observations, not to generate another
  full statistical summary.
- Use exact statistics when they make the conclusion more concrete.
- Distinguish clearly between what the data shows and what can reasonably be
  interpreted from it.
- Connect related statistics when they support the same conclusion.
- Keep the language natural and easy for a coach to understand.
- Be concise and practical.
- Do not simply list statistics.
- Do not repeat the complete offensive or defensive analysis.
- Do not create individual player evaluations unless they are directly
  relevant to a team-level conclusion.

IMPORTANT:
- Do not invent statistics, events, causes or tactical explanations.
- Do not infer possession from passing accuracy or passing volume.
- Do not infer pressing intensity from recoveries or interceptions alone.
- Do not infer specific tactical systems, player roles, defensive structures,
  positioning or causes that are not represented in the data.
- Do not claim that a particular action caused another event unless the data
  explicitly establishes that relationship.
- Do not assume that a high or low value is inherently good or bad without
  considering the definition of the metric.
- Do not describe the team as "dominant", "superior", "excellent", "poor",
  "better" or "worse".
- Do not use generic recommendations that are unrelated to the evidence.
- Do not design drills or exercises.
- Do not make recommendations based solely on a single isolated statistic
  unless that statistic clearly represents a relevant performance issue.

OUTPUT FORMAT:

Return the following three sections:

TEAM STRENGTHS
- 2-3 strengths, each with a short title and a concise explanation.

AREAS FOR IMPROVEMENT
- 2-3 areas for improvement, each with a short title and a concise explanation.

TRAINING FOCUS
- 2-3 training focuses corresponding to the most relevant areas for
  improvement.
- Describe what should be worked on, NOT a specific exercise or drill.

Return only the three sections and their content.

Do not return JSON.
Do not use Markdown headings.
"""
