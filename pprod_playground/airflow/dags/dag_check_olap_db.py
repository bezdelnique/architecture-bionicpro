from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
from datetime import datetime
import logging
import clickhouse_connect

# Замените на имя вашего подключения в Airflow (Connections)
CLICKHOUSE_CONN_ID = 'olap_clickhouse'
# Имя таблицы для проверки (должна существовать и содержать поле id)
CLICKHOUSE_TABLE = 'customers'

def check_clickhouse_connection():
    # 1. Получаем параметры подключения из Airflow
    conn = BaseHook.get_connection(CLICKHOUSE_CONN_ID)

    # 2. Создаём клиента ClickHouse
    client = clickhouse_connect.get_client(
        host=conn.host,
        port=conn.port,
        username=conn.login,
        password=conn.password,
        database=conn.schema or 'default'
    )

    try:
        logging.info("Подключение к ClickHouse установлено")

        # 3. Выполняем простой запрос (здесь — получение максимального id)
        query = f"SELECT COALESCE(MAX(id), 0) FROM {CLICKHOUSE_TABLE}"
        result = client.query(query)
        max_id = result.result_rows[0][0]

        logging.info(f"Максимальный id в таблице {CLICKHOUSE_TABLE}: {max_id}")

    except Exception as e:
        logging.error(f"Ошибка при работе с ClickHouse: {e}")
        raise
    finally:
        client.close()

# Определяем DAG
with DAG(
    dag_id='clickhouse_connection_test',
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,  # Только ручной запуск
    catchup=False,
    tags=['example', 'clickhouse'],
) as dag:

    test_task = PythonOperator(
        task_id='test_clickhouse_conn',
        python_callable=check_clickhouse_connection
    )

    test_task
