def build_match_analysis_prompt(data_json):

    return f"""
You are a football data analyst specialized in statistical match analysis.

Analyze the following match data:

{data_json}

IMPORTANT RULES:

1. USE ONLY THE INFORMATION PROVIDED
- Do not invent events, situations, tactics, player roles, or explanations.
- Do not assume why something happened.
- If the data is insufficient to explain something, explicitly say so.

2. DISTINGUISH FACTS FROM INTERPRETATION
- First describe what the statistics show.
- Then provide a cautious interpretation.
- Avoid unsupported tactical conclusions.

3. DO NOT INVENT OR MODIFY STATISTICS
- Every numerical value mentioned must come directly from the provided data.
- Do not create statistics that are not present.

4. FOOTBALL TERMINOLOGY

- pase = completed pass
- pase errado = misplaced/inaccurate pass
- perdida = possession lost
- recuperacion = ball recovery
- intercepcion = interception
- despeje = clearance
- tiro = shot
- tiro a puerta = shot on target
- regate = successful dribble
- falta cometida = foul committed
- parada = goalkeeper save
- blocaje = goalkeeper block/claim
- tarjeta amarilla = yellow card

5. PLAYER ANALYSIS
Consider:
- passing volume and accuracy
- possession losses
- recoveries
- interceptions
- shots and shots on target
- goals
- dribbles
- defensive actions

Do not judge a player's overall performance from one statistic alone.

6. EFFICIENCY
When discussing efficiency, explain the relationship between the relevant statistics.
Do not confuse:
- goals / shots
- goals / shots on target
- completed passes / total passes

7. UNCERTAINTY
When the sample size is small, explicitly mention it.

8. RECOMMENDATIONS
Recommendations must be directly connected to observed statistics.
Do not recommend tactical changes that cannot be supported by the available data.

9. OUTPUT FORMAT

OUTPUT FORMAT RULES

Return the analysis as plain text only.

Do NOT use Markdown formatting.
Do NOT use:
- Markdown headings (#, ##, ###)
- bold or italic formatting
- tables
- code blocks

Use numbered section titles and simple hyphen-prefixed lines for lists.

Example:

1. Executive Summary

- My Team completed 282 passes.
- My Team recorded 8 shots on target.
- Rival Team recorded 2 shots on target.

2. Team Performance

Passing:
My Team completed 282 passes and had 38 misplaced passes.

Ball Retention:
My Team recorded 34 possession losses compared with 24 for Rival Team.

Keep the structure clear and readable.

### 1. Executive Summary
3-5 concise bullet points.

### 2. Team Performance
Compare both teams using objective statistics.

### 3. Offensive Analysis
Analyze shots, shots on target, goals, dribbles and offensive contributions.

### 4. Defensive Analysis
Analyze recoveries, interceptions, clearances, goalkeeper statistics, fouls and goals conceded.

### 5. Player Analysis
Identify statistically notable players and explain why using their numbers.

### 6. Strengths
List 3-5 strengths supported by the data.

### 7. Weaknesses
List 3-5 weaknesses supported by the data.

### 8. Recommendations
Give 3-5 practical recommendations directly linked to the identified weaknesses.

Keep the analysis concise, objective and evidence-based.

Before writing the final analysis, verify every numerical claim against
the provided statistics. If a number cannot be verified, do not include it.
"""