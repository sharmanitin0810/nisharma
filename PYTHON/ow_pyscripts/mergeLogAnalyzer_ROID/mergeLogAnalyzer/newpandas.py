import pandas as pd

read_file = pd.read_excel (r'UtBtHandoverSimulation.xlsx')
read_file.to_csv (r'nitinpanda.csv', index = None, header=True) 
