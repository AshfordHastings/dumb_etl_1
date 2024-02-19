kafka-topics.sh --list  --bootstrap-server localhost:9092
kafka-topics.sh --create --topic users --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
kafka-topics.sh --create --topic users --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --config cleanup.policy=compact --config segment.bytes=1073741824
kafka-topics.sh --topic users1 --describe  --bootstrap-server localhost:9092
kafka-topics.sh --delete --topic users --bootstrap-server localhost:9092 
kafka-topics.sh --describe --topic track-events --bootstrap-server localhost:9092
kafka-topics.sh --bootstrap-server localhost:9092 --alter --topic track-events --partitions 3
kafka-console-consumer.sh --bootstrap-server <broker_address>:<port> --topic <topic_name> --from-beginning
kafka-console-producer.sh --broker-list localhost:9092 --topic users1 --property "parse.key=true" --property "key.separator=:"

# Using previous connector versoin, should be backwards compatible ish
# Scala version: 2.12.15
# Spark version: 3.5.0... actually, may just mean library version
# Kafka version: 0.10 > 

# Spark

spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 --master spark://spark-master:7077 spark-apps/stream_from_kafka.py
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1,org.postgresql:postgresql:42.2.5 --master spark://spark-master:7077 spark-apps/stream_from_kafka_to_cass.py

spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1,org.postgresql:postgresql:42.2.5,io.delta:delta-core_2.12:2.1.0,org.apache.hadoop:hadoop-aws:3.2.0 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" --master spark://spark-master:7077 spark-apps/stream_from_kafka_to_cass.py
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1,org.postgresql:postgresql:42.2.5,io.delta:delta-spark_2.12:3.0.0,org.apache.hadoop:hadoop-aws:3.2.0  --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" --master spark://spark-master:7077 spark-apps/stream_from_kafka_to_cass.py

pyspark --packages io.delta:delta-core_2.12:2.1.0 \
  --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" \
  --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog"

org.apache.hadoop:hadoop-aws:3.2.0,io.delta:delta-core_2.12:0.8.0
rm -r /tmp/checkpoint/offsets