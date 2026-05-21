import argparse
import smtplib
import os
import sys
import mimetypes
import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def log_error(msg):
    sys.stderr.write(f"ERR_SMTP: {msg}\n")
    with open('mailVantec_error.log', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERR_SMTP - {msg}\n")

def log_success(msg):
    with open('mailVantec_success.log', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - EXITOSO - {msg}\n")

def main():
    parser = argparse.ArgumentParser(description="MailVantec v2.0 - SMTP CLI")
    parser.add_argument('-s', dest='subject', required=True)
    parser.add_argument('-f', dest='from_email', required=True)
    parser.add_argument('-t', dest='to_email', required=True)
    parser.add_argument('-u', dest='username', required=True)
    parser.add_argument('-y', dest='password', required=True)
    parser.add_argument('-z', dest='smtp_host', required=True)
    parser.add_argument('-p', dest='port', type=int, required=True)
    parser.add_argument('-l', dest='use_tls', action='store_true')
    parser.add_argument('archivos', nargs='*')
    args = parser.parse_args()

    if len(args.archivos) < 1: 
        log_error("No se proporcionó el archivo body.html")
        sys.exit(1)
        
    msg = MIMEMultipart()
    msg['Subject'] = args.subject
    msg['From'] = args.from_email
    msg['To'] = args.to_email
    
    # El primer archivo es siempre el cuerpo HTML
    with open(args.archivos[0], 'r', encoding='utf-8') as f:
        msg.attach(MIMEText(f.read(), 'html'))
        
    # El resto son adjuntos posicionales (Lógica Multi-PDF L6 Inyectada)
    for argumento_archivo in args.archivos[1:]:
        # Rompemos la cadena por si vienen múltiples archivos separados por '|'
        rutas_individuales = [r.strip() for r in argumento_archivo.split('|') if r.strip()]
        
        for archivo in rutas_individuales:
            if os.path.exists(archivo):
                with open(archivo, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(archivo))
                msg.attach(part)
            else:
                log_error(f"Adjunto no localizado físicamente: {archivo}")

    try:
        server = smtplib.SMTP(args.smtp_host, args.port)
        if args.use_tls or args.port == 587: server.starttls()
        server.login(args.username, args.password)
        server.sendmail(args.from_email, args.to_email.split(','), msg.as_string())
        server.quit()
        log_success(f"Enviado a {args.to_email}")
        sys.exit(0)
    except Exception as e:
        log_error(str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()