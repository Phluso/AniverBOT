import datetime
import asyncio
import discord
from discord.ext import commands
import re
from lib import *
import sqlite3

version = "1.1.0 beta (agora com SQL B^D) 21-01-2026"

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

#verifica se a tabela users existe antes de fazer qualquer coisa
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT, dia INT, mes INT)")
conn.commit()

user = ""
servidorId = 0
sala = 0
user, servidorId, sala = carregar()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

class Usuario:
    def __init__(self, id, dia, mes):
        self.id = id
        self.dia = dia
        self.mes = mes

    def dict(self):
        return {
            "id": self.id,
            "dia": self.dia,
            "mes": self.mes
        }

    def novoUsuario(id, dia, mes):

        #valida o mês
        if (mes > 0 and mes <= 12):
            diasEmCadaMes = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            #valida o dia
            if (dia > 0 and dia <= diasEmCadaMes[mes -1]):
                #procura o nome do usuário na lista de usuários
                if len(cursor.execute(f"SELECT * FROM users WHERE id = {id}").fetchall()):
                    #atualiza o dado
                    try:
                        cursor.execute(f"UPDATE users SET dia = {dia}, mes = {mes} WHERE id = {id}")
                        conn.commit()
                        log("Dados atualizados")
                        return True
                    except:
                        log("Erro ao atualizar dados. Verifique se há um arquivo \"usuarios.json\"")
                        return False

                else:   #caso não encontre o usuário na lista, adicioná-lo
                    log("Criando novo usuário")
                    #cria uma nova instância da classe Usuario
                    try:
                        cursor.execute(f"INSERT INTO users (id, dia, mes) VALUES ({id}, {dia}, {mes})")
                        conn.commit()
                        log(f"Usuário {id} criado")
                        return True
                    except:
                        log("Erro ao criar novo usuário")
                        return False
            log(f"Dia inserido ({dia}) inválido")
            return False
        log(f"Mês inserido ({mes}) inválido")
        return False

    def removeUsuario(id):
        try:
            cursor.execute(f"DELETE FROM users WHERE id = {id}")
            conn.commit()
            return f"Usuário {id} removido"
        except:
            log(f"Algo deu errado ao remover o usuário {id}")
            return "Erro ao remover usuário"

async def parabens():
    global bot
    canal = bot.get_channel(sala)
    if not canal:
        log("Erro ao buscar o canal")
        return False
    print(canal)
    mensagem = ""

    hoje = datetime.datetime.now()
    aniversariantes = []

    for usuario in cursor.execute(f"SELECT id FROM users WHERE dia = {hoje.day} AND mes = {hoje.month}").fetchall():
        aniversariantes.append(usuario[0])
        await darCargo(usuario[0], "Aniversariante")

    if len(aniversariantes) > 0:
        mensagem = f"Feliz aniversário"
        for usuario in aniversariantes:
            try:
                usuario = await bot.fetch_user(usuario)
                mensagem += ", " + usuario.mention
            except:
                continue
        
        mensagem += " 🎂"
    else:
        mensagem = "Nenhum aniversariante hoje.\nSe você quiser receber uma mensagem de parabéns no dia do seu aniversário, me marque e escreva a data no formato dia/mês."
        log("Nenhum aniversariante hoje")

    await canal.send(mensagem)
    log("Mensagem enviada")


async def darCargo(usuario, nomeDoCargo):
    try:
        try:
            servidor = bot.get_guild(servidorId)
            if (servidor == None):
                raise ValueError()
        except:
            log("Servidor não encontrado")
            return
        try:
            cargo = discord.utils.get(servidor.roles, name=nomeDoCargo)
        except:
            log("Cargo não encontrado")
            return
        try:
            membro = servidor.get_member(usuario)
        except:
            log("Usuário não encontrado")
            return
        if (cargo == None):
            log("Cargo não informado")
            return
        await membro.add_roles(cargo)
    except:
        log("Erro ao conceder cargo")
        return
    log("Cargo concedido")
    
async def removerCargo(nomeDoCargo):
    try:
        servidor = bot.get_guild(servidorId)
        cargo = discord.utils.get(servidor.roles, name=nomeDoCargo)
        if (cargo == None):
            log("Cargo não existe")
            return
        for membro in cargo.members:
            await membro.remove_roles(cargo)
        log("Cargos removidos")
    except:
        log("Erro ao remover cargos")

@bot.event
async def on_ready():
    log("Bot iniciado corretamente")
    while True:
        agora = datetime.datetime.now()
        if agora.hour == 7 and agora.minute == 0:
            await parabens()
        if agora.hour == 0 and agora.minute == 0:
            #remove o cargo de aniversariante de todos os usuários
            await removerCargo("Aniversariante")
            #envia mensagem de ano novo
            if agora.day == 1 and agora.month == 1:
                log("Mensagem de ano novo")
                await bot.get_channel(sala).send("Feliz ano-novo! 🥳🍾🎉")
        await asyncio.sleep(60)

@bot.command(name="version")
async def returnVersion(ctx):
    await ctx.send(version)

@bot.command(name="listaUsuarios")
async def listaUsuarios(ctx):
    for user in cursor.execute("SELECT * FROM users").fetchall():
        print(f"id= {user[0]} dia= {user[1]} mes= {user[2]}")
    await ctx.send(f"total: {cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]} usuários")

@bot.command(name = "resetaCargos")
async def resetaCargos(ctx):
    await removerCargo("Aniversariante")

@bot.command(name = "parabens")
async def asyncParabens(ctx):
    log("Função parabens chamada por usuário")
    await parabens()

@bot.command(name = "status")
async def status(ctx):
    await ctx.reply(f"Estou funcionando na sala {sala}")

@bot.command(name = "remove")
async def remove(ctx):
    resultado = Usuario.removeUsuario(ctx.author.id)
    await ctx.send(resultado)

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if bot.user in message.mentions:
        try:
            #procurar data
            match = re.search(r"(\d{1,2})/(\d{1,2})", message.content)
            if match:
                dia = int(match.group(1))
                mes = int(match.group(2))

                resultado = Usuario.novoUsuario(message.author.id, dia, mes)

                if (resultado == True):
                    await message.add_reaction("🎂")
                    await message.add_reaction("✅")
                elif resultado == False:
                    await message.add_reaction("❌")
                    await message.reply("Algo deu errado. Verifique a data informada")
                else:
                    await message.add_reaction("☠️")
                    await message.reply("Erro. Verifique mensagens de log")
            else:  
                raise ValueError()
        except:
            await message.reply("Algo deu errado. Para adicionar sua data de aniversário, tente marcar o AniverBot escrevendo a data no formato dia/mês")
            log("Usuário não informou a data corretamente")

bot.run(user)



