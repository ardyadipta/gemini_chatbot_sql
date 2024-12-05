# Script to upload CSV to MySQL server

import pandas as pd
import mysql.connector

# Step 1: Load the CSV file
csv_file = "/tmp/sales_data_sample.csv"  # Replace with your CSV file path
df = pd.read_csv(csv_file, encoding='ISO-8859-1')

# Replace NaN values with None (MySQL's NULL)
df = df.where(pd.notnull(df), None)

# Step 2: Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Replace with your MySQL root password
    database="sales_database"   # Replace with your database name
)
cursor = conn.cursor()

# Step 3: Define a function to map Pandas dtypes to MySQL types
def map_dtype_to_sql(dtype):
    if pd.api.types.is_integer_dtype(dtype):
        return "INT"
    elif pd.api.types.is_float_dtype(dtype):
        return "FLOAT"
    elif pd.api.types.is_bool_dtype(dtype):
        return "BOOLEAN"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "DATETIME"
    else:
        return "VARCHAR(255)"  # Default to VARCHAR for object/string types

# Step 4: Generate the SQL schema from the DataFrame
table_name = "sales"  # Replace with your desired table name
schema = ", ".join([
    f"`{col}` {map_dtype_to_sql(dtype)}"
    for col, dtype in zip(df.columns, df.dtypes)
])

# Step 5: Create the table
create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema});"
cursor.execute(create_table_query)
print(f"Table `{table_name}` created successfully!")

# Step 6: Load the data into the table
for _, row in df.iterrows():
    placeholders = ", ".join(["%s"] * len(row))
    insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
    cursor.execute(insert_query, tuple(row))

conn.commit()
cursor.close()
conn.close()
print("Data inserted successfully!")
