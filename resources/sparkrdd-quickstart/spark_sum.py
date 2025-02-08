from pyspark import SparkContext, SparkConf
from pyspark.sql.functions import *
import sys

_, source = sys.argv

conf = SparkConf().setAppName("spark-sum")
sc = SparkContext(conf=conf)

numbers_rdd = sc.textFile(source)
numbers_int_rdd = numbers_rdd.map(lambda x: int(x))
result = numbers_int_rdd.sum()

print(
    f"""
------------------------------------------
------------------------------------------
------------------------------------------
SUM = {result}
------------------------------------------
------------------------------------------
------------------------------------------
"""
)

sc.stop()
