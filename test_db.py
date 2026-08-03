import psycopg

try:
    conn = psycopg.connect(
        host="127.0.0.1",
        port="5432",
        dbname="db",
        user="my_user",
        password="my_secretpass_word",
    )
    print("Підключення успішне!")
    conn.close()
except Exception as e:
    print("Помилка:", e)