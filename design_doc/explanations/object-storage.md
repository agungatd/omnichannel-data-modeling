In data lakehouse architectures, the statement highlights a fundamental trade-off between storage flexibility and performance. Let me break this down:

## Why Object Storage Has Higher Latency

**Network vs. Local Access**: Object storage (like AWS S3, Azure Blob, Google Cloud Storage) requires network calls to retrieve data, while attached storage (local SSDs, directly attached drives) provides direct memory-bus or local I/O access. This introduces several latency sources:

- Network round-trip time (RTT)
- HTTP/REST API overhead for object requests
- Authentication and metadata lookups
- Potential throttling and rate limiting

**Access Patterns**: Object storage is optimized for large, sequential reads rather than small, random access patterns. Traditional databases often need small, specific data chunks, which amplifies the latency problem.

## How Processing Engines Mitigate This

**Intelligent Data Fetching**: Modern processing engines like Apache Spark, Trino, or Databricks implement several optimizations:

- **Prefetching**: Anticipate data needs and fetch larger chunks proactively
- **Parallel I/O**: Issue multiple concurrent requests to object storage
- **Caching**: Keep frequently accessed data in local memory or fast storage tiers
- **Columnar reading**: Only fetch relevant columns rather than entire rows

**Compute-Storage Separation Benefits**: Processing engines can scale compute resources independently, often compensating for storage latency through parallel processing power.

## How Table Formats Help

Modern table formats like **Delta Lake**, **Apache Iceberg**, and **Apache Hudi** provide crucial optimizations:

**Metadata Management**: These formats maintain rich metadata about data organization, enabling:
- **Predicate pushdown**: Skip reading irrelevant files entirely
- **File pruning**: Eliminate unnecessary data access based on partition information
- **Statistics-based optimization**: Use min/max values and other statistics to avoid reading files

**Data Organization**: 
- **Columnar storage**: Parquet files store related data together, improving compression and reducing I/O
- **Partitioning**: Organize data by commonly queried dimensions
- **Compaction**: Optimize file sizes for efficient object storage access patterns

**Advanced Features**:
- **Z-ordering/clustering**: Co-locate related data to minimize files accessed
- **Bloom filters**: Quickly determine if data exists in a file without reading it
- **Data skipping**: Skip entire files based on query predicates

## The Combined Effect

While object storage might have 10-100x higher base latency than local storage, these optimizations can reduce actual query latency by orders of magnitude through:

1. **Reducing data volume**: Only read necessary data
2. **Parallelization**: Distribute the latency impact across many concurrent operations  
3. **Intelligent caching**: Keep hot data readily available
4. **Vectorized processing**: Process larger chunks more efficiently

The result is that well-architected data lakehouses can achieve query performance comparable to traditional data warehouses while maintaining the flexibility and cost benefits of object storage.