# Function to detect csv encoding
# Previously the CSV file was not able to be read

import chardet

csv_file = 'data/sales_data_sample.csv'
with open(csv_file, 'rb') as f:
    result = chardet.detect(f.read())
    print(result)