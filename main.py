from flask import Flask
import sqlite3

app = Flask(__name__)
app.secret_key = '12345'  # Necessário para flash messages

def conectar_db():
    conectar = sqlite3.connect('agendamento.db')
    return conectar

def criar_tabela():
    conectar = conectar_db()
    cursor = conectar.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL
        )
    ''')
    conectar.commit()
    conectar.close()

criar_tabela()

from routes import *

if __name__ == "__main__":
    app.run(debug=True)