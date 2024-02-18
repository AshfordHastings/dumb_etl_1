In Spark Streaming, the input data stream is divided into microbatches, and each microbatch is processed as a series of Spark jobs. The way these microbatches are processed across the cluster nodes depends on Spark's distributed computing model, which involves partitioning the data across the cluster.

### How Microbatches are Processed Across Nodes:

1. **Partitioning**: When a microbatch is received, it is divided into smaller partitions based on the configuration and the nature of the input source. These partitions are the fundamental units of parallelism in Spark.

2. **Distribution**: The partitions of each microbatch are distributed across the available nodes in the Spark cluster. Spark's scheduler assigns tasks to process each partition to different executors, which run on nodes of the cluster. The assignment takes into account data locality to minimize data transfer across the nodes and improve processing efficiency.

3. **Parallel Processing**: Each executor processes its assigned partitions in parallel. If there are more partitions than executors, executors will process them in sequence, but overall, the processing happens in parallel across the cluster. This means that while a single partition is processed by a single executor at a time, multiple partitions (and thus, parts of the microbatch) are processed simultaneously by different executors across the cluster.

4. **Aggregation Across Nodes**: For operations that require data aggregation or shuffling (e.g., reduceByKey, groupBy), Spark will perform necessary data shuffles across the network to bring together data that needs to be aggregated. This might involve transferring data between nodes but is managed efficiently by Spark's shuffle mechanism.

5. **Fault Tolerance**: Spark Streaming's microbatch processing model benefits from Spark's built-in fault tolerance. If a node processing a partition fails, Spark can reassign the task to another node, and the data can be recomputed from the source, thanks to Spark's lineage information.

### Example:

Consider a streaming application that reads data from Kafka and performs a word count operation. The data stream is divided into microbatches (e.g., every 5 seconds of data). Each microbatch is then partitioned (the number of partitions can be configured or depends on the source configuration), and these partitions are processed in parallel across the cluster. The word count operation is performed on each partition, and results from all partitions are aggregated to produce the final count for the microbatch.

### Conclusion:

In summary, microbatches in Spark Streaming are processed in parallel across all nodes of the cluster, with each node working on different partitions of the microbatch. This parallel processing model, combined with Spark's efficient data shuffling and fault tolerance mechanisms, enables Spark Streaming to process large volumes of data in real-time efficiently.