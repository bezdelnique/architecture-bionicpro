import requests
import psycopg2

KEYCLOAK_URL = "http://localhost:8080"
REALM = "reports-realm"
ADMIN_REALM = "master"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin"

PG_HOST = "localhost"
PG_PORT = 5444
PG_DB = "crm_db"
PG_USER = "crm_user"
PG_PASSWORD = "crm_password"


def get_admin_token():
    resp = requests.post(
        f"{KEYCLOAK_URL}/realms/{ADMIN_REALM}/protocol/openid-connect/token",
        data={
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": ADMIN_USER,
            "password": ADMIN_PASSWORD,
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def user_exists(headers, username):
    r = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
        headers=headers,
        params={"username": username, "exact": "true"},
    )
    r.raise_for_status()
    return len(r.json()) > 0


def create_user(headers, customer):
    customer_id, name, email = customer
    username = f"cprothetic{customer_id}"
    password = f"cprothetic{customer_id}"

    if user_exists(headers, username):
        print(f"Skip existing user: {username}")
        return

    payload = {
        "username": username,
        "enabled": True,
        "email": email,
        "firstName": name or username,
        "attributes": {
            "crm_user_id": [str(customer_id)]
        },
    }

    r = requests.post(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
        headers=headers,
        json=payload,
    )

    if r.status_code not in (201, 204):
        raise Exception(f"Create user failed for {username}: {r.status_code} {r.text}")

    # read created user id
    r = requests.get(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users",
        headers=headers,
        params={"username": username, "exact": "true"},
    )
    r.raise_for_status()
    users = r.json()
    if not users:
        raise Exception(f"User created but not found: {username}")

    user_id = users[0]["id"]

    # set password
    r = requests.put(
        f"{KEYCLOAK_URL}/admin/realms/{REALM}/users/{user_id}/reset-password",
        headers=headers,
        json={
            "type": "password",
            "value": password,
            "temporary": False
        },
    )
    if r.status_code not in (204,):
        raise Exception(f"Password set failed for {username}: {r.status_code} {r.text}")

    print(f"Created user {username} with password {password}")


def main():
    token = get_admin_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
    )

    with conn, conn.cursor() as cur:
        cur.execute("SELECT id, name, email FROM public.customers ORDER BY id LIMIT 10")
        for row in cur.fetchall():
            create_user(headers, row)


if __name__ == "__main__":
    main()


