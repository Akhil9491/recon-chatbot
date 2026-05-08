import psycopg2

def get_connection():
    return psycopg2.connect(
        host="34.30.6.95",
        port=5432,           # optional, 5432 is the default
        database="postgres",
        user="ctcengine",
        password="Qwerty12345"
    )