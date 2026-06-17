# CDC Banking Pipeline

A pipeline that watches a banking database for changes (new customers, balance updates, transactions) and streams those changes into a data warehouse in real time.

```
PostgreSQL  ->  Debezium  ->  Kafka  ->  Databricks  ->  Delta Lake
(source)       (capture)   (transport)   (process)       (storage)
```


## What is CDC?

CDC means Change Data Capture. Instead of copying a whole database every night, CDC watches the database log and only captures what changed. Banks and fintech companies use this to keep their data warehouse updated within seconds instead of hours.


## The Three Layers

**Bronze** - raw events exactly as they came from Kafka. Nothing is changed.

**Silver** - cleaned tables that show the current state of every row.

**Gold** - business numbers built from Silver, like total balance per customer.


## Tables

| Layer | Tables |
|-------|--------|
| Source (PostgreSQL) | users, accounts, transactions |
| Silver (Databricks) | silver_users, silver_accounts, silver_transactions |
| Gold (Databricks) | gold_account_summary, gold_daily_transactions, gold_top_senders |


## Tools Used

| Tool | Job |
|------|-----|
| PostgreSQL | Source database, runs locally |
| Debezium | Reads database changes, runs in Docker |
| Confluent Cloud (Kafka) | Carries the change events |
| Python + Faker | Fakes a live banking app writing data |
| Databricks | Reads Kafka events, writes to Delta Lake |


## Project Files

```
cdc-banking-pipeline/
  docker-compose.yml      runs Debezium
  data_generator.py       fakes banking activity
  create_tables.sql     creates the source tables
  cdc_pipeline.py       Databricks notebook, exported
  debezium-connector.json 
  README.md
```


## How to Run It

You need: PostgreSQL installed locally, Docker Desktop, Python, a free Confluent Cloud account, a free Databricks account.

**1. Clone the repo**

```bash
git clone https://github.com/Ujusophy/cdc-banking-pipeline
cd cdc-banking-pipeline
```

**2. Create the database and user**

Open psql and run:

```sql
CREATE DATABASE banking;
CREATE USER admin WITH PASSWORD 'admin123';
GRANT ALL PRIVILEGES ON DATABASE banking TO admin;
\c banking
```

**3. Create the source tables**

```bash
psql -U admin -d banking -f sql/create_tables.sql
```

**4. Set up Confluent Cloud**

Create a free cluster on confluent.io, then create three topics: `banking.public.users`, `banking.public.accounts`, `banking.public.transactions`. Grab your bootstrap server and API key, then add them into `docker-compose.yml`.

**5. Start the fake data generator**

```bash
pip install psycopg2-binary faker
python data_generator.py
```

**6. Start Debezium**

```bash
docker-compose up -d
```

**7. Register the Debezium connector**

Open `debezium-connector.json` and replace `YOUR_LOCAL_IP` with your machine's IP address, then run:

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @debezium-connector.json
```

**8. Run the notebook**

Import `notebooks/cdc_pipeline.py` into Databricks, add your Confluent Cloud credentials in the config cell, and run all cells. It reads from Kafka and writes to Delta Lake.
