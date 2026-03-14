#!/usr/bin/env bash
set -e

echo 'clickhouse password set'
cat > olap-db/users.xml <<EOL
<yandex>
    <users>
        <default>
            <password>default123</password>
            <networks>
                <ip>::/0</ip>
            </networks>
            <profile>default</profile>
            <quota>default</quota>
        </default>
    </users>
</yandex>
EOL

echo 'airflow connection creation'
docker exec pprod_playground-airflow-webserver-1 airflow connections add 'crm_postgres' \
    --conn-type 'postgres' \
    --conn-login 'crm_user' \
    --conn-password 'crm_password' \
    --conn-host 'crm_db' \
    --conn-port '5432' \
    --conn-schema 'crm_db'

docker exec pprod_playground-airflow-webserver-1 airflow connections add 'olap_clickhouse' \
    --conn-type 'http' \
    --conn-login 'default' \
    --conn-password 'default123' \
    --conn-host 'olap_db' \
    --conn-port '8123' \
    --conn-schema 'default'

echo 'keycloak user sync'
cd keycloak_pgsync
/usr/bin/env bash pgsync.sh
cd ..

