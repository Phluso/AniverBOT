from email.message import EmailMessage
import ssl
import smtplib

remetente = "aniver.bot.backup@gmail.com"
senha = "pokn xvni ouft hxam"
destinatario = "pedrolusocosta@gmail.com"

assunto = "Backup AniverBOT"

email = EmailMessage()
email["From"] = remetente
email["To"] = destinatario
email["Subject"] = assunto
email.set_content("teste")

context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
    smtp.login(remetente, senha)
    smtp.sendmail(remetente, destinatario, email.as_string())
    


'''
@bot.command(name = "backup")
async def mostraLista(ctx):
    lista = carregarDados()
    log(lista)
    resultado = await enviaBackup(json.dumps(lista))
    if (resultado):
        log("Email enviado com sucesso")
    else:
        log("Erro ao enviar o email")

'''