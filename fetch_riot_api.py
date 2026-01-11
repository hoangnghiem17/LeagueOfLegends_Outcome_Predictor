from riotwatcher import LolWatcher, ApiError
import pandas as pd
from dotenv import load_dotenv
import os
import requests
from urllib.parse import quote

# 1) Setup: Initialize the LolWatcher with API Key
load_dotenv()
RIOT_API_KEY = os.getenv('RIOT_API_KEY')

if RIOT_API_KEY is None:
    raise ValueError("RIOT_API_KEY not found in .env file! Please check your .env file.")
else:
    print(f"API Key loaded: {RIOT_API_KEY[:10]}...{RIOT_API_KEY[-5:]} (showing first 10 and last 5 chars)")

watcher = LolWatcher(RIOT_API_KEY)

# 2) Set Riot-ID Information
game_name = 'euclidean aatrox'  
tag_line = 'EUW' 
routing_region = 'europe'  
my_region = 'euw1'

# 3) Fetch API to find out PUUID (Summoner ID)
encoded_game_name = quote(game_name)
encoded_tag_line = quote(tag_line)

# Construct URL
get_puuid_url = f"https://{routing_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{encoded_game_name}/{encoded_tag_line}"

# Make request
headers = {
    "X-Riot-Token": RIOT_API_KEY
}

try:
    response = requests.get(get_puuid_url, headers=headers)
    puuid = response.json()['puuid']
    print(response.json())
    print(puuid)
except Exception as e:
    print(f"Error: {e}")

if puuid is None:
    raise ValueError("PUUID not found in response! Please check your .env file.")
else:
    print(f"PUUID found: {puuid}")

# 4) Feature Selection: Select attributes that contribute to win or lose

selected_attributes = [
    # Participant basic info
    'championName',
    'summonerName',
    'queueId',
    'gameMode',
    'gameType',
    
    # Win/Loss (target variable)
    'win',
    
    # Game outcome
    'gameEndedInSurrender',
    'gameEndedInEarlySurrender',

    # KDA
    'kills',
    'deaths',
    'assists',
    
    # Gold
    'goldEarned',
    'goldSpent',
    
    # CS (Creep Score)
    'totalMinionsKilled',
    
    # Objectives
    'baronKills',
    'dragonKills',
    'turretKills',
    'turretTakedowns',  # From challenges
    'turretsLost',
    'inhibitorKills',
    'inhibitorTakedowns',
    'inhibitorsLost',
    'objectivesStolen',
    'objectivesStolenAssists',
    
    # First events
    'firstBloodKill',
    'firstBloodAssist',
    'firstTowerKill',
    'firstTowerAssist',
    
    # Damage
    'totalDamageDealtToChampions',
    'damagePerMinute',  # From challenges
    
    # Healing & CC
    'totalHeal',
    'totalTimeCCDealt',
    'timeCCingOthers',
    
    # Vision
    'wardsPlaced',
    'wardsKilled',
    
    # Combat stats
    'killingSprees',
    'longestTimeSpentLiving',
    'totalTimeSpentDead',
    'bountyLevel',
    
    # Spells
    'spell1Casts',
    'spell2Casts',
    'spell3Casts',
    'spell4Casts',
    
    # Other
    'timePlayed',
    'challenges'  # Container object (specific challenge attributes extracted separately)
]

print(f"Total selected attributes: {len(selected_attributes)}")
print(f"\nGrouped attributes:")
print(f"  Participant basic info: 4")
print(f"  Win/Loss: 1")
print(f"  Game outcome: 2")
print(f"  KDA: 3")
print(f"  Gold: 2")
print(f"  CS: 2")
print(f"  Objectives: 9")
print(f"  First events: 4")
print(f"  Damage: 8")
print(f"  Healing & CC: 3")
print(f"  Vision: 2")
print(f"  Combat stats: 6")
print(f"  Spells: 4")
print(f"  Other: 3")
print(f"  Challenges container: 1")

# 5) Get all match_ids to use that to retrieve match data (API limits only 100 match_ids possible at a time)
def get_all_ranked_match_ids(watcher, region, puuid):
    """Retrieve all ranked match IDs (100 per request max)"""
    all_match_ids = []
    start = 0
    
    while True:
        match_ids = watcher.match.matchlist_by_puuid(region, puuid, start=start, count=100)
        if not match_ids:
            break
        all_match_ids.extend(match_ids)
        if len(match_ids) < 100:
            break
        start += 100
    
    return all_match_ids

all_match_ids = get_all_ranked_match_ids(watcher, routing_region, puuid)
print(f"Total match IDs retrieved: {len(all_match_ids)}")

# 6) # Investigate data structure: one match has 10 entries for each player (5 vs 5)
example_match_id = all_match_ids[0]
match = watcher.match.by_id(my_region, example_match_id)
print(type(match))
#print(f"Keys of match: {match.keys()}")
#print(f"Keys of info (attributes for feature engineering): {match['info'].keys()}")
#print(f"Values of info: {match['info'].values()}")
#print(f"Keys of metadata: {match['metadata'].keys()}")
#print(f"Values of metadata: {match['metadata'].values()}")
#print(match)

# 7) Extract data from all matches: Iterate through all 938 matches to retrieve selected attributes using match.by_id 
def get_match_dataframe(watcher, region, match_ids, selected_attributes):
    """
    Extract match data into DataFrame using selected attributes.
    
    Parameters:
    -----------
    watcher : LolWatcher
        Initialized RiotWatcher instance
    region : str
        Routing region (europe, americas, asia)
    match_ids : list
        List of match IDs to process
    selected_attributes : list
        List of attribute names to extract from participant data
    
    Returns:
    --------
    pd.DataFrame
        DataFrame with one row per participant, containing selected attributes
    """
    participants_data = []
    
    # Attributes that are nested inside 'challenges' object
    challenges_attrs = ['turretTakedowns', 'soloKills', 'damagePerMinute']
    
    print(f"Processing {len(match_ids)} matches...")
    
    for idx, match_id in enumerate(match_ids):
        try:
            # Fetch match data from API
            match_data = watcher.match.by_id(region, match_id)
            match_info = match_data['info']
            
            # Process each participant (10 per match)
            for participant in match_info['participants']:
                row = {'matchId': match_id} 
                
                # Extract each selected attribute
                for attr in selected_attributes:
                    if attr == 'challenges':
                        # Skip 'challenges' itself, we extract specific challenge attributes
                        continue
                    elif attr in challenges_attrs:
                        # Extract from nested challenges object
                        row[attr] = participant.get('challenges', {}).get(attr)
                    else:
                        # Extract directly from participant object
                        row[attr] = participant.get(attr)
                
                participants_data.append(row)
            
            # Progress indicator every 100 matches
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(match_ids)} matches ({len(participants_data)} participants so far)")
                
        except ApiError as e:
            print(f"  API Error for match {match_id}: {e}")
            continue
        except Exception as e:
            print(f"  Error processing match {match_id}: {e}")
            continue
    
    df = pd.DataFrame(participants_data)
    
    print(f"\n✅ Complete! Created DataFrame with {len(df)} rows from {len(match_ids)} matches")
    print(f"   Shape: {df.shape} (rows × columns)")
    
    return df

# Process ALL match IDs with selected attributes#
df_all_matches = get_match_dataframe(watcher, routing_region, all_match_ids, selected_attributes)
df_all_matches.to_excel('all_matches_data_py.xlsx', index=False, engine='openpyxl')
print("="*70)
print("EXTRACTING DATA FROM ALL MATCHES")
print("="*70)

print(f"\nDataFrame Info:")
print(f"  Total rows: {len(df_all_matches)}")
print(f"  Total columns: {len(df_all_matches.columns)}")
print(f"  Expected: ~{len(all_match_ids) * 10} rows (10 participants per match)")
print(f"\nFirst few rows:")
print(df_all_matches.head())
print(f"\nColumn names: {list(df_all_matches.columns)}")
