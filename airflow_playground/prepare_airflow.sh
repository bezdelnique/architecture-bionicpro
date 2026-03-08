#!/usr/bin/env bash

docker exec airflow_playground-airflow-webserver-1 airflow connections add 'crm_pg' \
    --conn-type 'postgres' \
    --conn-login 'airflow' \
    --conn-password 'airflow' \
    --conn-host 'postgres' \
    --conn-port '5432' \
    --conn-schema 'crm' \

docker exec airflow_playground-airflow-webserver-1 airflow connections add 'dwh_pg' \
    --conn-type 'postgres' \
    --conn-login 'airflow' \
    --conn-password 'airflow' \
    --conn-host 'postgres' \
    --conn-port '5432' \
    --conn-schema ' dwh' \

