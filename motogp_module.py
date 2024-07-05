import pandas as pd
import numpy as np



def showStandings(data: pd.DataFrame, year: int, category: str):
    '''
    
    Function to calculate standings for a given year and category
    
    '''
    data = data[(data['year'] == year) & (data['category'] == category)].copy()
    standings = data.groupby(['rider_name'])['points'].sum().sort_values(ascending=False).reset_index()
    return standings

def finishPosition(data: pd.DataFrame, year: int, category: str, position: int = 1):
    '''
    
    Function to calculate the number of finishes in a given position for each rider
    
    '''
    
    data = data[(data['year'] == year) & (data['category'] == category)].copy()
    
    finish_position = data[data['position'] == position].groupby(['rider_name']).size().sort_values(ascending=False).reset_index()
    finish_position = finish_position.rename(columns={0:f'amount_of_{position}'})
    
    all_riders = data['rider_name'].unique()    
    winning_riders = finish_position['rider_name'].unique()    
    zero_victory_riders = [rider for rider in all_riders if rider not in winning_riders]
    zero_victory_df = pd.DataFrame({
        'rider_name': zero_victory_riders,
        f'amount_of_{position}': 0
    })
    
    finish_position = pd.concat([finish_position, zero_victory_df], ignore_index=True)
    
    return finish_position

def noPointsFinishes(data: pd.DataFrame, year: int, category: str):
    '''
    
    Function to calculate the number of finishes with no points for each rider
    
    '''
    data = data[(data['year'] == year) & (data['category'] == category)].copy()
    no_points = data[(data['position'] > 15) | (data['position'] < 0)].groupby(['rider_name']).size().sort_values(ascending=False).reset_index()
    no_points = no_points.rename(columns={0:f'amount_of_0_points'}) 
    all_riders = data['rider_name'].unique()
    
    no_points_riders = no_points['rider_name'].unique()   
    riders_with_points = [rider for rider in all_riders if rider not in no_points_riders]   
    zero_victory_df = pd.DataFrame({
        'rider_name': riders_with_points,
        'amount_of_0_points': 0
    })
    
    no_points = pd.concat([no_points, zero_victory_df], ignore_index=True)
    
    return no_points

def riderPositions(data: pd.DataFrame, year: int, category: str):
    '''
    
    Function to calculate the positions achieved by each rider
    
    '''
    riders_positions = pd.merge(
        finishPosition(data, year=year, category=category, position=1),
        finishPosition(data, year=year, category=category, position=2),
        on='rider_name', how='left'
    )

    riders_positions = pd.merge(
        riders_positions,
        finishPosition(data, year=year, category=category, position=3),
        on='rider_name', how='left'
    )
    riders_positions = pd.merge(
        riders_positions,
        noPointsFinishes(data, year=year, category=category),
        on='rider_name', how='left'
    )
    riders_positions = riders_positions.fillna(0)
    
    return riders_positions

def mostCommonPosition(data: pd.DataFrame, year: int, category: str):
    '''
    
    Function to calculate the most common position achieved by each rider
    
    '''
    most_commo_position = data[(data['year'] == year) & (data['category'] == category)].copy()
    most_commo_position = most_commo_position.groupby('rider_name')['position'].median().sort_values(ascending=True).reset_index()
    most_commo_position = most_commo_position.rename(columns={'position':'median_position'}) 
    return most_commo_position

def medianTimeToLeader(data: pd.DataFrame, year: int, category: str):
    '''
    Function to calculate the median time difference to the leader for each rider.
    '''
    
    data = data.copy()
    data['time'] = data['time'].astype(str)

    def timeFormat(time_str):
        if 'Lap' in time_str:
            laps = int(time_str.split()[0])
            lap_time_seconds = laps * 100
            return lap_time_seconds
        elif "'" in time_str:
            minutes, seconds = time_str.split("'")
            seconds = float(seconds.replace('+', ''))
            total_seconds = int(minutes) * 60 + seconds
            return total_seconds
        else:
            time_diff = float(time_str.replace('+', ''))
            return time_diff
    

    data['time_to_leader'] = data.apply(
        lambda row: 0 if row['position'] == 1 else timeFormat(row['time']), axis=1
    )
    

    data.loc[data['position'] < 0, 'time_to_leader'] = np.nan

    median_time_diff = data[(data['year'] == year) & (data['category'] == category)].copy()
    median_time_diff = median_time_diff.groupby('rider_name')['time_to_leader'].median().sort_values(ascending=True).reset_index()
    median_time_diff = median_time_diff.rename(columns={'time_to_leader': 'median_time_diff'})
    
    return median_time_diff

def raceCount(data: pd.DataFrame, category: str, till_year:str): 
    '''
    
    Function to calculate the number of races participated in by each rider by the year we evaluate riders promotion
    For example, If we evaluate promotion by the results of season 2022, it will count all races prior and including season 2022    
    
    '''
    race_counts = data[data['year']<= till_year].copy().groupby(['rider_name', 'category']).size().reset_index(name='race_count')
    race_counts = race_counts[race_counts['category'] == category].sort_values(by='race_count',ascending=False)
    race_counts = race_counts.drop(columns='category')
    return race_counts

def gotPromotionToMotoGP(data: pd.DataFrame, season_start: int, season_end: int, riders_amount: int):
    '''
    
    Function to identify riders who got promoted to MotoGP    
    
    '''
    merged_data_list = []
    
    for year in range(season_start, season_end):
        merged_data = (
            showStandings(data, year=year, category='Moto2').head(riders_amount)
            .merge(raceCount(data, 'Moto2', year), on='rider_name', how='inner')
            .merge(finishPosition(data, year, 'Moto2', 1), on='rider_name', how='inner')
            .merge(finishPosition(data, year, 'Moto2', 2), on='rider_name', how='inner')
            .merge(finishPosition(data, year, 'Moto2', 3), on='rider_name', how='inner')
            .merge(noPointsFinishes(data, year, 'Moto2'), on='rider_name', how='inner')
            .merge(mostCommonPosition(data, year=year, category='Moto2'), on='rider_name', how='inner')
            .merge(medianTimeToLeader(data, year=year, category='Moto2'), on='rider_name', how='inner')
        )
        merged_data['year'] = year
        merged_data['got_promoted'] = 0
        if year == 2021:
            promoted_riders = ['Gardner, Remy', 'Fernandez, Raul', 'Di Giannantonio, Fabio', 'Bezzecchi, Marco']
            merged_data.loc[merged_data['rider_name'].isin(promoted_riders), 'got_promoted'] = 1
            merged_data['rider_name'] = merged_data['rider_name'] + '_' + str(year)
        else:
            next_year_standings = showStandings(data, year=year + 1, category='MotoGP')['rider_name']
            merged_data['got_promoted'] = merged_data['rider_name'].isin(next_year_standings).astype(int)
            if season_end - season_start > 1:
                merged_data['rider_name'] = merged_data['rider_name'] + '_' + str(year)
        
        merged_data_list.append(merged_data)
    data_merged_all_years = pd.concat(merged_data_list, ignore_index=True)
    return data_merged_all_years
