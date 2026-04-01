import pandas as pd

# ==========================================
# PHASE 1: LOAD AND RESTRUCTURE
# ==========================================

# 1. LOAD THE RAW EXTRACTED DATA
master_df = pd.read_csv("Semester 1/Introduction to Data Science/group project/brisbane_airquality_raw.csv")

# 2. MELT: Convert the "Wide" station columns into a single "station" column
id_vars = ['Date', 'Time', 'Year', 'Pollutant']
station_columns = [col for col in master_df.columns if col not in id_vars]

df_long = pd.melt(master_df, 
                  id_vars=id_vars, 
                  value_vars=station_columns, 
                  var_name='station',
                  value_name='reading')

# 3. PIVOT: Split the "Pollutant" column into separate 'ozone' and 'pm2.5' columns
df_tidy = df_long.pivot_table(index=['Date', 'Time', 'station'], 
                              columns='Pollutant', 
                              values='reading').reset_index()


df_tidy.columns.name = None
df_tidy = df_tidy.rename(columns={'Ozone': 'ozone', 'PM2.5': 'pm2.5'})

# 4. COMBINE DATE & TIME
clean_date = df_tidy['Date'].astype(str).str[:10]
df_tidy['date'] = pd.to_datetime(clean_date + ' ' + df_tidy['Time'].astype(str), format='mixed', dayfirst=True)
df_tidy = df_tidy.drop(columns=['Date', 'Time'])

# ==========================================
# PHASE 2: SUBURB MAPPING (No Coordinates)
# ==========================================

# A. Load official boundaries just for the Suburb Names
boundaries_df = pd.read_csv("Semester 1/Introduction to Data Science/group project/suburb-boundaries.csv")
boundaries_df['suburb'] = boundaries_df['SUBURB_NAME'].str.title()

# Align the names for the merge
boundaries_df['station'] = boundaries_df['suburb'].replace({
    'Brisbane City': 'Brisbane CBD',
    'Port Of Brisbane': 'Fisherman Island'
})

# Keep only the two columns we need
bcc_mapping = boundaries_df[['station', 'suburb']]

# B. Regional Fallback Dictionary (Coordinates removed)
station_mapping = {
    "South Brisbane": {"station": "South Brisbane", "suburb": "South Brisbane"},
    "Roma": {"station": "Roma", "suburb": "Roma"},
    "Collingwood Park": {"station": "Collingwood Park", "suburb": "Collingwood Park"},
    "Lytton": {"station": "Lytton", "suburb": "Lytton"},
    "Deception Bay": {"station": "Deception Bay", "suburb": "Deception Bay"},
    "Rangeville": {"station": "Rangeville", "suburb": "Rangeville"},
    "Southport": {"station": "Southport", "suburb": "Southport"},
    "Tara Region 2": {"station": "Tara Region 2", "suburb": "Tara"},
    "Mountain Creek": {"station": "Mountain Creek", "suburb": "Mountain Creek"},
    "Coomera": {"station": "Coomera", "suburb": "Coomera"},
    "Flinders View": {"station": "Flinders View", "suburb": "Flinders View"},
    "Rocklea": {"station": "Rocklea", "suburb": "Rocklea"},
    "Wynnum West": {"station": "Wynnum West", "suburb": "Wynnum West"},
    "Charleville": {"station": "Charleville", "suburb": "Charleville"},
    "South Gladstone": {"station": "South Gladstone", "suburb": "South Gladstone"},
    "Mutdapilly": {"station": "Mutdapilly", "suburb": "Mutdapilly"},
    "Toowoomba": {"station": "Toowoomba", "suburb": "Toowoomba"},
    "Hopeland": {"station": "Hopeland", "suburb": "Hopeland"},
    "Mount Coot-tha": {"station": "Mount Coot-tha", "suburb": "Mount Coot-tha"},
    "Raceview": {"station": "Raceview", "suburb": "Raceview"},
    "North Maclean": {"station": "North Maclean", "suburb": "North Maclean"},
    "Woolloongabba": {"station": "Woolloongabba", "suburb": "Woolloongabba"},
    "Tara Region": {"station": "Tara Region", "suburb": "Tara"},
    "Fisherman Island": {"station": "Fisherman Island", "suburb": "Port of Brisbane"},
    "Parkwood": {"station": "Parkwood", "suburb": "Parkwood"},
    "Cannon Hill": {"station": "Cannon Hill", "suburb": "Cannon Hill"},
    "Brisbane CBD": {"station": "Brisbane CBD", "suburb": "Brisbane City"},
    "Springwood": {"station": "Springwood", "suburb": "Springwood"},
    "Miles Airport": {"station": "Miles Airport", "suburb": "Miles"},
    "Deagon": {"station": "Deagon", "suburb": "Deagon"},
    "Wynnum North": {"station": "Wynnum North", "suburb": "Wynnum North"},
    "Nambour": {"station": "Nambour", "suburb": "Nambour"}
}
fallback_df = pd.DataFrame(list(station_mapping.values()))

# C. Combine and prioritize official mappings
all_mapping = pd.concat([bcc_mapping, fallback_df]).drop_duplicates(subset=['station'], keep='first')

# D. Merge final mapping into the dataset
final_df = pd.merge(df_tidy, all_mapping, on='station', how='left')

# Reorder columns and save HOURLY file
final_df = final_df[['station', 'suburb', 'date', 'ozone', 'pm2.5']]
final_df.to_csv("Brisbane_AirQuality_Hourly_Tidy.csv", index=False)
print("Hourly processing complete.")

# ==========================================
# PHASE 3: DAILY AGGREGATION
# ==========================================

# 6. GROUP BY CALENDAR DAY
final_df['calendar_day'] = final_df['date'].dt.date

# Group by the updated columns
daily_df = final_df.groupby(['station', 'suburb', 'calendar_day']).agg({
    'pm2.5': 'mean',  
    'ozone': 'max'    
}).reset_index()

# Clean up
daily_df = daily_df.rename(columns={'calendar_day': 'date'})

# Final reorder to match your exact layout
daily_df = daily_df[['station', 'suburb', 'date', 'ozone', 'pm2.5']]

# Save DAILY file
daily_df.to_csv("Brisbane_AirQuality_Daily_Tidy.csv", index=False)
print("Daily aggregation complete. Pipeline finished!")