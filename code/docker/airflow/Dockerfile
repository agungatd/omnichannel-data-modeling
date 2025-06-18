# Use the official Airflow image as a base
FROM apache/airflow:2.8.2

# Switch to root user to install packages
USER root

# Install necessary system packages (e.g., openjdk for Java)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a directory for drivers
RUN mkdir -p /opt/airflow/jars

# Download PostgreSQL JDBC Driver
ADD https://jdbc.postgresql.org/download/postgresql-42.6.0.jar /opt/airflow/jars/

# Download MongoDB Spark Connector JARs
# Note: In a real project, manage these dependencies with a build tool
ADD https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.2.1/mongo-spark-connector_2.12-10.2.1.jar /opt/airflow/jars/
ADD https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-core/4.8.2/mongodb-driver-core-4.8.2.jar /opt/airflow/jars/
ADD https://repo1.maven.org/maven2/org/mongodb/bson/4.8.2/bson-4.8.2.jar /opt/airflow/jars/
ADD https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/4.8.2/mongodb-driver-sync-4.8.2.jar /opt/airflow/jars/

# Switch back to the airflow user
USER airflow

# Install Airflow providers and other Python packages
RUN pip install --no-cache-dir \
    apache-airflow-providers-apache-spark \
    apache-airflow-providers-postgres
