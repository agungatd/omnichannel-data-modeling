# 🧠 Omnichannel Data Modeling – Senior Data Engineer Take-Home Assignment

## 🛍️ Case Overview

This project models data for ShopSphere, a fast-scaling omnichannel platform integrating web, POS, and third-party marketplace data.

## 🎯 Objectives

- Unify customer identities across sources
- Enable real-time dashboards and fraud detection
- Create a lakehouse-based design that supports SCD and schema evolution

## 📁 Folder Structure

- `design_doc/`: Written explanation and trade-offs
- `schema/`: Logical model diagrams and SQL DDLs
- `sample_data/`: CSV and JSON sample data
- `scripts/`: Plans for ingestion, SCD, and identity resolution

## 🧠 Key Features

- Real-time and batch data integration
- Customer 360 and behavioral data modeling
- Inventory tracking and anomaly detection
- GDPR-compliant audit trails with time-travel

---

## 🔧 Tech Assumptions

- Data Lakehouse: Apache Iceberg
- Storage: S3 / HDFS
- Streaming: Kafka
- Batch: PostgreSQL, MongoDB
- Orchestration: Airflow (assumed)

---

## ✍️ Instructions

1. Clone this repo.
2. Fill out the `.md` files with your designs and rationales.
3. Add your diagrams and sample DDLs.
4. Upload to GitHub and share the link or ZIP it for submission.

---

## 📬 Questions?

Feel free to add comments in the Markdown files if assumptions are made.
