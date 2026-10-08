import sqlite3

def execute_db(command, params=()):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute(command, params)
    result = cur.fetchone()
    conn.commit()
    conn.close()
    return result

def init_db():
    execute_db(
        "CREATE TABLE IF NOT EXISTS cities_user_data("
        "chatid INTEGER PRIMARY KEY, score INTEGER, cities TEXT)"
    )