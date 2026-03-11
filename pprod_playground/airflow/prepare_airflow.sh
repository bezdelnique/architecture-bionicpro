#!/usr/bin/env bash

docker exec airflow_playground-airflow-webserver-1 airflow connections add 'crm_postgres' \
    --conn-type 'postgres' \
    --conn-login 'airflow' \
    --conn-password 'airflow' \
    --conn-host 'postgres' \
    --conn-port '5432' \
    --conn-schema 'crm' \

docker exec airflow_playground-airflow-webserver-1 airflow connections add 'olap_clickhouse' \
    --conn-type 'clickhouse' \
    --conn-login 'default' \
    --conn-password '' \
    --conn-host 'postgres' \
    --conn-port '9000' \
    --conn-schema 'default' \

