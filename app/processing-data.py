import datetime

from pyspark.sql.functions import explode, col, count, lit

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import explode
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job

glueContext = GlueContext(SparkContext.getOrCreate())
spark = glueContext.spark_session
job = Job(glueContext)
job.init("stackoverflow-glue-job")

# Read all JSON files from S3
raw_bucket_name = "stackoverflow-raw-bucket"
raw_prefix = "questions_raw"
processed_bucket_name = "stackoverflow-processed-file"

current_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
year, month, day = current_time.split("-")[:3]
raw_path = f"s3://{raw_bucket_name}/{raw_prefix}/{year}/{month}/{day}/*.json"

raw_df = spark.read.json(raw_path)

# Extract tags from each question
tags_df = raw_df.select(explode(col("items.tags")).alias("tag"))

# Count occurrences of each tag
tags_df = tags_df.groupBy("tag").agg(count("*").alias("count"))

# Add year, month, and date columns to DataFrame
tags_df = (
    tags_df.withColumn("year", lit(year))
    .withColumn("month", lit(month))
    .withColumn("date", lit(day))
)

# Sort by count and limit to top 10 tags
top_tags_df = tags_df.orderBy(col("count").desc()).limit(10)

# Write results to S3 as partitioned Parquet files
s3_output_path = f"s3://{processed_bucket_name}/USE_CASES/STACKOVERFLOW_TAGS/"

# Write processed data to S3 in Parquet format
top_tags_df.write.partitionBy("year", "month", "day").mode("append").parquet(
    s3_output_path
)

# Write metadata to Glue Data Catalog
glue_db = "stackoverflow_db"
glue_table = "trending_tags"

top_tags_df.write.format("glueparquet").option("database", glue_db).option(
    "table", glue_table
).partitionBy("year", "month", "day").mode("append").saveAsTable(glue_table)

job.commit()
