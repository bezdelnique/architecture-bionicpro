from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.hooks.base import BaseHook
import clickhouse_connect
import logging
import tempfile
import os
import csv

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1),
    'start_date': datetime(2024, 1, 1),
}

CLICKHOUSE_TABLE = 'default.customers'
BATCH_SIZE = 10


def get_max_id_clickhouse(**context):
    conn = BaseHook.get_connection('olap_clickhouse')
    client = clickhouse_connect.get_client(
        host=conn.host,
        port=conn.port,
        username=conn.login,
        password=conn.password,
        database=conn.schema or 'default'
    )

    try:
        query = f"SELECT COALESCE(MAX(id), 0) FROM {CLICKHOUSE_TABLE}"
        result = client.query(query)
        max_id = result.result_rows[0][0]
        logging.info(f"Max ID в ClickHouse: {max_id}")
        context['ti'].xcom_push(key='max_id', value=max_id)
        return max_id
    finally:
        client.close()


def fetch_and_generate_csv(**context):
    ti = context['ti']
    max_id = ti.xcom_pull(task_ids='get_max_id_clickhouse', key='max_id')
    if max_id is None:
        max_id = 0

    pg_hook = PostgresHook(postgres_conn_id='crm_postgres')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()

    try:
        select_query = """
            SELECT id, age, gender, country
            FROM public.customers
            WHERE id > %s
            ORDER BY id ASC
            LIMIT %s;
        """
        cursor.execute(select_query, (max_id, BATCH_SIZE))
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not rows:
        logging.info("Нет новых данных для переноса.")
        ti.xcom_push(key='csv_file_path', value=None)
        return

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='', encoding='utf-8') as tmp:
        writer = csv.writer(tmp, quoting=csv.QUOTE_MINIMAL)

        for row in rows:
            processed_row = []
            for value in row:
                if value is None:
                    processed_row.append(r'\N')
                else:
                    processed_row.append(value)
            writer.writerow(processed_row)

        file_path = tmp.name

    logging.info(f"Сгенерирован CSV-файл: {file_path} (строк: {len(rows)})")
    ti.xcom_push(key='csv_file_path', value=file_path)
    return file_path


def import_csv_to_clickhouse(**context):
    ti = context['ti']
    file_path = ti.xcom_pull(task_ids='fetch_and_generate_csv', key='csv_file_path')

    if not file_path or not os.path.exists(file_path):
        logging.info("Файл не найден или нет данных для импорта.")
        return

    conn = BaseHook.get_connection('olap_clickhouse')
    client = clickhouse_connect.get_client(
        host=conn.host,
        port=conn.port,
        username=conn.login,
        password=conn.password,
        database=conn.schema or 'default'
    )

    try:
        with open(file_path, 'rb') as f:
            client.raw_insert(
                table=CLICKHOUSE_TABLE,
                column_names=['id', 'age', 'gender', 'country'],
                insert_block=f,
                fmt='CSV'
            )

        logging.info(f"Данные из файла {file_path} успешно загружены в ClickHouse.")
    finally:
        client.close()

        if os.path.exists(file_path):
            os.unlink(file_path)
            logging.info(f"Временный файл {file_path} удалён.")


with DAG(
    dag_id='crm_to_olap_incremental_csv',
    default_args=default_args,
    description='Инкрементальный перенос данных из PostgreSQL CRM в OLAP ClickHouse с использованием CSV',
    schedule_interval='*/15 * * * *',
    catchup=False,
    tags=['crm', 'olap'],
) as dag:

    task_get_max_id = PythonOperator(
        task_id='get_max_id_clickhouse',
        python_callable=get_max_id_clickhouse,
    )

    task_fetch_and_generate = PythonOperator(
        task_id='fetch_and_generate_csv',
        python_callable=fetch_and_generate_csv,
    )

    task_import_csv = PythonOperator(
        task_id='import_csv_to_clickhouse',
        python_callable=import_csv_to_clickhouse,
    )

    task_get_max_id >> task_fetch_and_generate >> task_import_csv
