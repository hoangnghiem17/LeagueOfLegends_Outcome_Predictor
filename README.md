# Analyzing my League of Legends (LoL) Playstyle

This repository analyzes my LoL playstyle using data fetched from the official Riot Developer API. The analysis focuses on understanding whether an aggressive, fighting-oriented playstyle contributes to game success.

## Background

League of Legends is a 5v5 multiplayer online battle arena (MOBA) game where each team has 5 participants with unique roles. My main role is **top lane** (on top of the map), and I primarily play **fighters** (champions with a mix of defense and attack, close-range combat). 

**Hypothesis:** I play aggressively and snowball my lead by fighting and getting kills, rather than focusing on farming and passive play.

**Champions Analyzed:** Aatrox and Camille (top lane fighters)

## Method

### Data Collection
1. **API Setup**: Used Riot Developer API via `riotwatcher` Python library
   - Fetched account information (PUUID) using Riot ID: `euclidean aatrox#EUW`
   - Retrieved all available match IDs (938 matches from 2021 onwards)
   - Extracted detailed match data for each game

2. **Data Preprocessing**:
   - Filtered to my account: `euclidean aatrox` (892 games)
   - Filtered to top lane champions: Aatrox and Camille (92 games)
   - Selected 18 relevant attributes for analysis:
     - **KDA**: kills, deaths, assists
     - **Economy**: goldEarned, totalMinionsKilled
     - **Combat**: totalDamageDealtToChampions, turretKills
     - **Vision & Control**: wardsPlaced, longestTimeSpentLiving
     - **Time metrics**: timePlayed, totalTimeSpentDead
     - **Spell usage**: spell1Casts, spell2Casts, spell3Casts, spell4Casts

3. **Exploratory Data Analysis (EDA)**:
   - Correlation matrix analysis to identify multicollinearity
   - Distribution analysis (KDA, gold, damage, CS, wards, time)
   - Scatter plots: kills vs damage, gold vs damage
   - Violin plots: damage distribution by win/loss
   - Statistical testing: t-test comparing damage in wins vs losses

### Files
- `fetch_riot_api.py`: Script to fetch match data from Riot API and export to Excel
- `EDA.ipynb`: Jupyter notebook containing complete exploratory data analysis
- `all_matches_data_py.xlsx`: Exported dataset with all match data

## Insights

### 1. **Strong Positive Correlations Support Aggressive Playstyle**
- **Kills ↔ Gold**: r = 0.78 - More kills lead to more gold
- **Kills ↔ Damage**: r = 0.78 - More kills associated with higher damage output
- **Gold ↔ Damage**: r = 0.84 - Higher gold enables more damage (better items)

**Interpretation**: These three metrics move together, supporting the hypothesis that an aggressive playstyle (fighting → kills → gold → damage) creates a positive feedback loop.

### 2. **KDA Distribution Pattern**
- **High assists** (median ~9+): Active participation in teamfights and skirmishes
- **Medium kills**: Consistent with top lane role
- **Low deaths**: Good survival skills despite aggressive play

**Interpretation**: The distribution pattern (high assists, medium kills, low deaths) is consistent with a fighting-oriented playstyle where I actively participate in teamfights while maintaining reasonable survival.

### 3. **Damage and Game Outcome**
- **Winning games**: Median damage ~55-60k
- **Losing games**: Median damage ~35-40k
- **Mean difference**: 7,433 damage (~20% increase in wins)
- **Statistical test**: t = 1.77, p = 0.0798 (not significant at α = 0.05, but trending)

**Interpretation**: While not statistically significant, there is a **trend** (p < 0.10) suggesting higher damage output is associated with winning. The relationship could be bidirectional:
- High damage → Wins (aggressive playstyle leads to victory)
- Wins → High damage (winning enables more damage through snowball effect)

### 4. **Game Length and Playstyle Evolution**
- **Early/Mid game**: Focus on skirmishes and combat (kills, damage, gold)
- **Late game**: Shift toward control (wards, minions, map control)
  - `timePlayed` ↔ `totalMinionsKilled`: r = 0.78
  - `timePlayed` ↔ `wardsPlaced`: r = 0.79

**Interpretation**: As games progress, the playstyle shifts from aggressive fighting to controlled map control, which is typical for longer games.

### 5. **Interesting Correlations**
- **deaths ↔ assists**: r = 0.61 - May indicate trading 1-for-1 (dying for assists)
- **wardsPlaced ↔ totalMinionsKilled**: r = 0.90 - Vision control correlates with farming (controlled playstyle)
- **wardsPlaced ↔ longestTimeSpentLiving**: r = 0.80 - More vision helps stay alive longer

## Limitations

- **Small sample size**: Only 92 final games (Aatrox + Camille) after filtering. The API likely didn't return all games due to a name change, reducing available data.
- **Mixed game modes**: Analysis includes all game types (normal, ranked, draft, ARAM) to maximize sample size. This limits interpretation since ARAM games have fundamentally different mechanics (no wards, shorter games, different objectives).
- **Focus on combat stats**: With the current sample size, analysis focused on combat metrics. With more data, attributes like `wardsPlaced` and `totalMinionsKilled` could be analyzed separately for ranked games vs ARAM for a more complete picture.
- **Statistical power**: The t-test for damage difference between wins/losses did not reach significance (p = 0.0798), likely due to limited sample size reducing statistical power.

## Setup

### Prerequisites
```bash
pip install riotwatcher pandas openpyxl python-dotenv seaborn matplotlib numpy scipy
```

### Configuration
1. Get a Riot API key from [Riot Developer Portal](https://developer.riotgames.com/)
2. Create a `.env` file in the project root:
   ```
   RIOT_API_KEY=your_api_key_here
   ```
3. Update `fetch_riot_api.py` with your Riot ID:
   ```python
   game_name = 'your_game_name'
   tag_line = 'your_tag'
   ```

### Usage
1. **Fetch data**: Run `fetch_riot_api.py` to retrieve match data
   ```bash
   python fetch_riot_api.py
   ```
   This creates `all_matches_data_py.xlsx`

2. **Run EDA**: Open `EDA.ipynb` in Jupyter Notebook and run all cells

## Future Work

- Collect more match data to increase sample size and statistical power
- Filter by game mode (ranked only) for more focused analysis
- Compare playstyle patterns between Aatrox and Camille
- Build a classification model to predict game outcomes based on in-game metrics
- Analyze early game vs late game performance separately
