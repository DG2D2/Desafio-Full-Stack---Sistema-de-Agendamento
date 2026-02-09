from main import app, conectar_db
from flask import render_template, request, redirect, flash
import requests
from datetime import datetime, time

def obter_feriados():
    url = "https://date.nager.at/api/v3/PublicHolidays/2026/BR"
    resposta = requests.get(url)
    feriados = resposta.json()
    return [f["date"] for f in feriados]

def eh_fim_de_semana(data):
    return data.weekday() >= 5

def horario_valido(hora):
    inicio = time(8, 0)
    fim = time(18, 0)
    return inicio <= hora < fim

def horario_ocupado(data, hora):
    conexao = conectar_db()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT * FROM agendamentos WHERE data = ? AND hora = ?",
        (data, hora)
    )
    resultado = cursor.fetchone()
    conexao.close()
    return resultado is not None


@app.route("/")
def politicas_agendamento():
    return render_template("politicas_agendamento.html")

@app.route("/agendamento")
def agendamento():
    return render_template("agendamento.html")

    
@app.route("/agendar_consulta", methods=['POST'])
def agendar_consulta():
    nome = request.form["nome"]
    data_str = request.form["data"]
    hora_str = request.form["hora"]

    data_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
    hora_obj = datetime.strptime(hora_str, "%H:%M").time()

    # 1️ Final de semana
    if eh_fim_de_semana(data_obj):
        flash('''Não é possível agendar aos sábados ou domingos.
                Favor verifiar os dias e horários disponíveis.''')
        return redirect("/agendamento")

    # 2️ Feriado
    feriados = obter_feriados()
    if data_str in feriados:
        flash('''Não é possível agendar em feriados.
                Favor verifiar os dias e horários disponíveis.''')
        return redirect("/agendamento")

    # 3️ Horário inválido
    if not horario_valido(hora_obj):
        flash('''Horário permitido apenas entre 08:00 e 18:00.
                Favor verifiar os horários disponíveis.''')
        return redirect("/agendamento")

    # 4️ Horário ocupado
    if horario_ocupado(data_str, hora_str):
        flash('''Este horário e data já estão ocupados.
                Favor verifiar os dias e horários disponíveis.''')
        return redirect("/agendamento")

    # 5️ Salva no banco
    conexao = conectar_db()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO agendamentos (nome, data, hora) VALUES (?, ?, ?)",
        (nome, data_str, hora_str)
    )
    conexao.commit()
    conexao.close()

    flash("Consulta agendada com sucesso!")
    return redirect("/agendamento")
