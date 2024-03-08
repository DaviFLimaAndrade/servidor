import mysql.connector

def conectar():
    try:
        print("conexão estabelecida")
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="senai",
            database="pwbe_escola"
        )
        
    except mysql.connector.Error as err:
        print("Erro ao conectar ao banco de dados:", err)
        return None
    