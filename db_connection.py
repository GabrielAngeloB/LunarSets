import mysql.connector
from mysql.connector import Error
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='db_lunar',
            port=3306  # Especifica a porta 3307
        )
        if connection.is_connected():
            return connection
    except Error as erro:
        print(f"erro ai olha: {erro}")
        return None
    else:
        print("conectado fio")

def close_connection(connection):
    if connection.is_connected():
        connection.close()
