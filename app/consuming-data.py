import boto3
import pandas as pd

# Initialize Athena client
athena = boto3.client("athena")

# Define query
query = "SELECT tag, count(*) as tag_count FROM stackoverflow_table GROUP BY tag ORDER BY tag_count DESC LIMIT 10"

# Execute query
response = athena.start_query_execution(
    QueryString=query,
    QueryExecutionContext={"Database": "<database_name>"},
    ResultConfiguration={"OutputLocation": "<s3_output_location>"},
)

# Get query execution ID
query_execution_id = response["QueryExecutionId"]

# Get query results
query_results = athena.get_query_results(QueryExecutionId=query_execution_id)

# Convert query results to DataFrame
columns = [
    col["Label"]
    for col in query_results["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
]
data = [list(row.values()) for row in query_results["ResultSet"]["Rows"][1:]]
df = pd.DataFrame(data, columns=columns)

# Print DataFrame
print(df)
