import datetime
import asyncio
import discord
from discord.ext import commands
import re
from lib import *
from sendBackup import *
import json

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
        try:
            listaUsuarios = carregarDados()
        except:
            log("Erro ao carregar dados. Verifique se há um arquivo \"usuarios.json\"")
            return None
        #valida o mês
        if (mes > 0 and mes <= 12):
            diasEmCadaMes = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            #valida o dia
            if (dia > 0 and dia <= diasEmCadaMes[mes -1]):
                #procura o nome do usuário na lista de usuários
                for usuario in listaUsuarios:
                    if (usuario["id"] == id):
                        log(f"Atualizando dados do usuário {id}")
                        #se o usuário for encontrado, atualiza a data de aniversário
                        usuario["dia"] = dia
                        usuario["mes"] = mes
                        usuario["id"] = id
                        
                        try:
                            salvarDados(listaUsuarios)
                            log("Dados atualizados")
                            return True
                        except:
                            log("Erro ao atualizar dados. Verifique se há um arquivo \"usuarios.json\"")
                            return False

                else:   #caso não encontre o usuário na lista, adicioná-lo
                    log("Criando novo usuário")
                    #cria uma nova instância da classe Usuario
                    novoUsuario = Usuario(id, dia, mes)
                    #transforma a instância em um dicionário temporário
                    novoUsuario = novoUsuario.dict()
                    #adiciona o dicionário na array
                    listaUsuarios.append(novoUsuario)
                    try:
                        salvarDados(listaUsuarios)
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
            listaUsuarios = carregarDados()
            for i in range(len(listaUsuarios)):
                if listaUsuarios[i]["id"] == id:
                    listaUsuarios.pop(i)
                    salvarDados(listaUsuarios)
                    log(f"Usuário {id} removido")
                    return "Usuário removido"
            else:
                log(f"Usuário {id} não encontrado")
                return "Usuário não encontrado"
        except:
            log(f"Algo deu errado ao remover o usuário {id}")
            return "Erro ao remover usuário"

async def parabens():
    global bot
    try:
        listaUsuarios = carregarDados()
    except:
        log("Erro ao carregar dados. Verifique se há um arquivo \"usuarios.json\"")
        return
    hoje = datetime.datetime.now()
    aniversariantes = []

    for usuario in listaUsuarios:
        if (usuario["dia"] == hoje.day and usuario["mes"] == hoje.month):
            aniversariantes.append(usuario["id"])
            await darCargo(usuario["id"], "Aniversariante")

    if len(aniversariantes) > 0:
        mensagem = f"Feliz aniversário"
        for usuario in aniversariantes:
            try:
                usuario = await bot.fetch_user(usuario)
                mensagem += ", " + usuario.mention
            except:
                continue
        
        mensagem += " 🎂"

        canal = bot.get_channel(sala)
        if canal:
            await canal.send(mensagem)
            log("Mensagem de parabéns enviada")
    else:
        log("Nenhum aniversariante hoje")

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
        await asyncio.sleep(60)

@bot.command(name = "concedeCargo")
async def concedeCargo(ctx):
    try:
        listaUsuarios = carregarDados()
    except:
        log("Erro ao carregar dados. Verifique se há um arquivo \"usuarios.json\"")
        return
    hoje = datetime.datetime.now()

    for usuario in listaUsuarios:
        if (usuario["dia"] == hoje.day and usuario["mes"] == hoje.month):
            await darCargo(usuario["id"], "Aniversariante")
        

@bot.command(name = "resetaCargos")
async def resetaCargos(ctx):
    await removerCargo("Aniversariante")

@bot.command(name = "parabens")
async def asyncParabens(ctx):
    log("Função parabens chamada por usuário")
    await parabens()

@bot.command(name = "backup")
async def mostraLista(ctx):
    lista = carregarDados()
    log(lista)
    resultado = await enviaBackup(json.dumps(lista))
    if (resultado):
        log("Email enviado com sucesso")
    else:
        log("Erro ao enviar o email")

@bot.command(name = "hora")
async def mostraHora(ctx):
    print(datetime.datetime.now())

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
    if message.author.id == 1210010399135502346:
        await message.add_reaction("🍅")
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



