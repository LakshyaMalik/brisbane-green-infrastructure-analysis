import requests
import pandas as pd

# Combined dictionary for both pollutants
resources = {
    'PM2.5': {
        '2024': '1cf37e6c-2c68-4409-a8b3-6a80c97e0f52',
        '2023': '5b1163e3-7803-4158-adb6-9fe200183053',
        '2022': '705ead06-8ae5-47a2-a797-f2b361a4d42f',
        '2021': 'a6f86c6b-712d-4fab-a9b8-2cd69de3fef2',
        '2020': '25a15320-1cba-46a9-a559-b5cf39d2ee7e',
        '2019': '4dc8e1b2-7a3c-45e0-a0bd-a3459b8638d2',
    },
    'Ozone': {
        '2024': 'a9af06d6-f6c5-4923-89b8-28e869342783',
        '2023': 'da1925e6-6f98-4bba-a161-4f8c55d16eda',
        '2022': '1344e5c8-e952-4bcb-a624-c94ea20257b3',
        '2021': '75b83405-d47d-469f-9a7e-4839196fd883',
        '2020': '374dcdce-5e5e-46e1-acf6-3c1239c454c0',
        '2019': '264bcb13-9d89-4e7c-8942-792d0114a56d',
    }
}

def get_air_data(pollutant, year, rid):
    url = "https://www.data.qld.gov.au/api/3/action/datastore_search_sql"
    sql = f'''SELECT * FROM "{rid}" LIMIT 50000'''
    
    try:
        response = requests.get(url, params={'sql': sql})
        data = response.json()
        
        if data['success']:
            df = pd.DataFrame(data['result']['records'])
            
            # Keep Date, Time, and stations in South East QLD
            keywords = ['Date', 'Time', 'South']
            df = df[[c for c in df.columns if any(word in c for word in keywords)]]
            
            # Clean station names
            df.columns = [c.split('(')[0].strip() for c in df.columns]
            
            # Add metadata columns 
            df['Year'] = year
            df['Pollutant'] = pollutant
            return df
    except Exception as e:
        print(f"Error fetching {pollutant} {year}: {e}")
    return pd.DataFrame()

all_frames = []
for pollutant, years in resources.items():
    for year, rid in years.items():
        print(f"Downloading {pollutant} for {year}...")
        df = get_air_data(pollutant, year, rid)
        if not df.empty:
            all_frames.append(df)

if all_frames:
    master_df = pd.concat(all_frames, axis=0, ignore_index=True)
    master_df.to_csv("brisbane_airquality_raw.csv", index=False)
