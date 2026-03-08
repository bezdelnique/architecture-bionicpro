from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import execute_values
import logging

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

def get_max_id(**context):
    """Task 1: Get the maximum ID from the destination table."""
    hook = PostgresHook(postgres_conn_id='dwh_pg')
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(MAX(id), 0) FROM device_data;")
    max_id = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    logging.info(f"Max ID in DWH: {max_id}")
    context['ti'].xcom_push(key='max_id', value=max_id)
    return max_id


def fetch_new_data(**context):
    ti = context['ti']
    max_id = ti.xcom_pull(task_ids='get_max_id', key='max_id')
    if max_id is None:
        max_id = 0

    hook = PostgresHook(postgres_conn_id='crm_pg')
    conn = hook.get_conn()
    cursor = conn.cursor()
    select_query = """
        SELECT id, username, meter_id, device_data, created_at
        FROM device_data
        WHERE id > %s
        ORDER BY id ASC
        LIMIT 5;
    """
    cursor.execute(select_query, (max_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    columns = ['id', 'username', 'meter_id', 'device_data', 'created_at']
    data = [dict(zip(columns, row)) for row in rows]

    logging.info(f"Fetched {len(data)} rows from CRM. First ID: {data[0]['id'] if data else 'none'}")
    ti.xcom_push(key='new_rows', value=data)
    return data

def insert_into_dwh(**context):
    ti = context['ti']
    rows = ti.xcom_pull(task_ids='fetch_new_data', key='new_rows')
    if not rows:
        logging.info("No rows to insert.")
        return

    values = [(row['id'], row['username'], row['meter_id'], row['device_data'], row['created_at']) for row in rows]

    hook = PostgresHook(postgres_conn_id='dwh_pg')
    conn = hook.get_conn()
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO device_data (id, username, meter_id, device_data, created_at)
        VALUES %s
        ON CONFLICT (id) DO NOTHING;
    """
    execute_values(cursor, insert_query, values)
    conn.commit()
    cursor.close()
    conn.close()
    logging.info(f"Inserted {len(rows)} rows into DWH.")


with DAG(
    dag_id='crm_to_dwh_device_data_three_tasks',
    default_args=default_args,
    description='Incremental transfer CRM to DWH',
    schedule_interval='*/5 * * * *',
    catchup=False,
    tags=['crm', 'dwh', 'transfer'],
) as dag:
    task_get_max_id = PythonOperator(
        task_id='get_max_id',
        python_callable=get_max_id,
        provide_context=True,
    )

    task_fetch_new_data = PythonOperator(
        task_id='fetch_new_data',
        python_callable=fetch_new_data,
        provide_context=True,
    )

    task_insert_into_dwh = PythonOperator(
        task_id='insert_into_dwh',
        python_callable=insert_into_dwh,
        provide_context=True,
    )

    task_get_max_id >> task_fetch_new_data >> task_insert_into_dwh
