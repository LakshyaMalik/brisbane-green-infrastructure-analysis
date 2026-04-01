import pandas as pd

# Load your file
master_df = pd.read_csv("Semester 1/Introduction to Data Science/group project/Brisbane_AirQuality_O3_PM25.csv")

# Print the exact column names as a list
print(master_df.columns.tolist())