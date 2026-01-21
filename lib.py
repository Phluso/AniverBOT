import datetime
import json

def log(text):
    hora = datetime.datetime.now()
    print(f"{hora.hour}:{hora.minute}:{hora.second}: {text}")
    
#não é mais usado  
def carregar():
    user, servidorId, sala = "", 0, 0
    try:
        with open("config.json", "r") as config:
            data = json.load(config)
            user = data["user"]
            servidorId = data["server"]
            sala = data["channel"]
            return user, int(servidorId), int(sala)
    except:
        log("Erro ao configurar o bot. Verifique se há um arquivo 'config.json' contendo os atributos 'user', 'server' e 'channel'")
        exit()