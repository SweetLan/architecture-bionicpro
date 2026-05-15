from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from clickhouse_driver import Client


default_args = {
    "owner": "bionicpro",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def build_report_mart():
    client = Client(
        host="clickhouse",
        port=9000,
        user="default",
        password="",
        database="default",
    )

    client.execute("""
        CREATE TABLE IF NOT EXISTS prosthesis_report_mart
        (
            report_date Date,
            user_id String,
            prosthesis_id String,
            client_name String,
            client_country String,
            telemetry_events_count UInt64,
            avg_response_ms Float64,
            max_response_ms Float64,
            avg_battery_level Float64,
            min_battery_level UInt8,
            processed_at DateTime
        )
        ENGINE = MergeTree
        PARTITION BY toYYYYMM(report_date)
        ORDER BY (user_id, prosthesis_id, report_date)
    """)

    client.execute("""
        INSERT INTO prosthesis_report_mart
        SELECT
            toDate(t.event_time) AS report_date,
            c.user_id AS user_id,
            t.prosthesis_id AS prosthesis_id,
            c.client_name AS client_name,
            c.client_country AS client_country,
            count() AS telemetry_events_count,
            avg(t.response_ms) AS avg_response_ms,
            max(t.response_ms) AS max_response_ms,
            avg(t.battery_level) AS avg_battery_level,
            min(t.battery_level) AS min_battery_level,
            now() AS processed_at
        FROM telemetry_events t
        INNER JOIN crm_clients c
            ON t.prosthesis_id = c.prosthesis_id
        WHERE toDate(t.event_time) = yesterday()
        GROUP BY
            report_date,
            c.user_id,
            t.prosthesis_id,
            c.client_name,
            c.client_country
    """)


with DAG(
    dag_id="prosthesis_reports_etl",
    default_args=default_args,
    description="ETL-процесс подготовки витрины отчётности по протезам",
    start_date=datetime(2026, 1, 1),
    schedule_interval="0 2 * * *",
    catchup=False,
    tags=["bionicpro", "reports", "etl"],
) as dag:

    build_report_mart_task = PythonOperator(
        task_id="build_report_mart",
        python_callable=build_report_mart,
    )