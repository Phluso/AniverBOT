import datetime
import json

def log(text):
    hora = datetime.datetime.now()
    print(f"{hora.hour}:{hora.minute}:{hora.second}: {text}")

#carregar lista de usuário
def carregarDados():
    try:
        with open("usuarios.json", "r") as j:
            return json.load(j)
    except:
        raise ValueError()

def salvarDados(lista):
    try:
        with open("usuarios.json", "w") as j:
            json.dump(lista, j)
    except:
        raise ValueError()
    
def carregar():
    #carregar token
    user = ""
    try:
        with open("user", "r") as _user:
            user = _user.read()
    except:
        log("Falha ao carregar o token. Verifique se há um arquivo \"user\" com o user do bot")
        exit()

    #carregar servidor
    servidorId = 0
    try:
        with open("server", "r") as _servidor:
            servidorId = _servidor.read()
    except:
        log("Falha ao carregar o servidor. Verifique se há um arquivo \"server\" com o ID do servidor")
        exit()

    #carregar sala
    sala = 0
    try:
        with open("channel", "r") as f:
            sala = int(f.read())
    except:
        log("Falha ao carregar o ID da sala. Verifique se há um arquivo \"channel\" com o ID da sala")
        exit()
    
    return user, servidorId, sala