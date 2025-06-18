## **Local Lakehouse for ShopSphere**

This Docker Compose environment simulates the entire ShopSphere data platform, allowing for local development and testing of the ETL pipelines.

### **Prerequisites**

* Docker  
* Docker Compose

### **How to Start**

1. Make sure you have created the directory structure outlined above.  
2. Place your Airflow DAGs and Spark scripts in the respective `dags/` and `spark_apps/` folders.  
3. From the root of the project (shopsphere-local-lakehouse/), run the following command:  

```bash
   docker-compose up --build -d
```

   This will build the custom Airflow image and start all the services in the background. It might take a few minutes the first time.

### **Accessing Services**

Once all containers are running, you can access the UIs for each service:

* **Airflow UI**: `http://localhost:8080` (login: `airflow` / `airflow`)  
* **Spark Master UI**: `http://localhost:8081`  
* **MinIO Console (Data Lake)**: `http://localhost:9001` (login: `admin` / `password`)  
* **JupyterLab**: `http://localhost:8888` (token: `shopsphere`)  
* **PostgreSQL Source DB**: Connect via localhost:5432 (user/pass: `shopsphere`)  
* **MongoDB Source DB**: Connect via localhost:27017 (user/pass: `admin`/`admin`)  
* **Nessie Catalog API**: `http://localhost:19120/api/v2/`

### **First Steps**

1. **Create a MinIO Bucket**: Go to the MinIO UI (`http://localhost:9001`), log in, and create a new bucket named `lakehouse`. This will be your data lake.  
2. **Configure Spark for Iceberg/Nessie**: When submitting Spark jobs (either from Airflow or Jupyter), you need to include packages and configurations to connect to your Nessie catalog and MinIO S3 storage.  
   * **Packages**: `org.apache.iceberg:iceberg-spark-runtime-3.4_2.12:1.4.2`, `org.projectnessie.nessie-integrations:nessie-spark-extensions-3.4_2.12:0.77.1`, `software.amazon.awssdk:bundle:2.17.230`  
   * **SQL Extensions**: `org.projectnessie.spark.extensions.NessieSparkSQLExtensions`  
   * **Catalog Config**: Set the catalog implementation to Nessie, point it to `http://nessie-catalog:19120/api/v1`, and configure the S3 warehouse path to `s3a://lakehouse/`warehouse.  
3. **Run Your DAGs**: Open the Airflow UI, un-pause your DAGs, and trigger a run to see the pipeline execute.

### **Stopping the Environment**

To stop all running services, run:

```bash
docker-compose down
```

To stop the services and remove all data volumes (for a clean restart), run:

```bash
docker-compose down -v  
```