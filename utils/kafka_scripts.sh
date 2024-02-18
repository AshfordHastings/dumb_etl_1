kafka-topics.sh --list  --bootstrap-server localhost:9092
kafka-topics.sh --create --topic users --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
kafka-topics.sh --create --topic users --bootstrap-server kafka:9092 --partitions 3 --replication-factor 1 --config cleanup.policy=compact --config segment.bytes=1073741824
kafka-topics.sh --topic users1 --describe  --bootstrap-server localhost:9092
kafka-topics.sh --delete --topic users --bootstrap-server localhost:9092 
kafka-topics.sh --describe --topic track-events --bootstrap-server localhost:9092
kafka-topics.sh --bootstrap-server localhost:9092 --alter --topic track-events --partitions 3
kafka-console-consumer.sh --bootstrap-server <broker_address>:<port> --topic <topic_name> --from-beginning
kafka-console-producer.sh --broker-list localhost:9092 --topic users1 --property "parse.key=true" --property "key.separator=:"

spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 --master spark://spark-master:7077 spark-apps/stream_from_kafka.py
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1,org.postgresql:postgresql:42.2.5 --master spark://spark-master:7077 spark-apps/stream_from_kafka_to_cass.py
# Using previous connector versoin, should be backwards compatible ish
# Scala version: 2.12.15
# Spark version: 3.5.0... actually, may just mean library version
# Kafka version: 0.10 > 