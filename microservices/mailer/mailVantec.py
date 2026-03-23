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
    with open('mailVantec_error.log', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERR_SMTP - {msg}\n")

def log_success(msg):
    with open('mailVantec_success.log', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - EXITOSO - {msg}\n")

def main():
    parser = argparse.ArgumentParser(description="MailVantec v2.3 - Universal SMTP CLI")
    parser.add_argument('-s', dest='subject', required=True)
    parser.add_argument('-f', dest='from_email', required=True)
    parser.add_argument('-t', dest='to_email', required=True)
    parser.add_argument('-u', dest='username', required=True)
    parser.add_argument('-y', dest='password', required=True)
    parser.add_argument('-z', dest='smtp_host', required=True)
    parser.add_argument('-p', dest='port', type=int, required=True)
    parser.add_argument('-l', dest='use_tls', action='store_true')
    parser.add_argument('-v', dest='verbose', action='store_true')
    parser.add_argument('archivos', nargs='*')
    args = parser.parse_args()

    if len(args.archivos) < 1: 
        log_error("No se proporcionó el archivo body.html")
        sys.exit(1)
        
    # Crear contenedor de correo multipart/mixed (Requerido para adjuntos múltiples estándar)
    msg = MIMEMultipart('mixed')
    msg['Subject'] = args.subject
    msg['From'] = args.from_email
    msg['To'] = args.to_email
    
    cuerpo_html = args.archivos[0]
    if os.path.exists(cuerpo_html):
        with open(cuerpo_html, 'r', encoding='utf-8') as f: 
            html_part = MIMEText(f.read(), 'html', 'utf-8')
            msg.attach(html_part)
    else:
        log_error(f"No se encontro el archivo HTML: {cuerpo_html}")
        sys.exit(1)
        
    adjuntos = args.archivos[1:]
    adjuntos_procesados = 0
    nombres_adjuntos = [] 
    
    for archivo in adjuntos:
        if os.path.exists(archivo):
            ctype, _ = mimetypes.guess_type(archivo)
            if ctype is None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            
            with open(archivo, 'rb') as f:
                part = MIMEBase(maintype, subtype)
                part.set_payload(f.read())
                
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(archivo))
            msg.attach(part)
            
            adjuntos_procesados += 1
            nombres_adjuntos.append(os.path.basename(archivo))
        else:
            log_error(f"Adjunto no encontrado: {archivo}")
            sys.exit(1)

    try:
        server = smtplib.SMTP(args.smtp_host, args.port)
        server.ehlo()
        if args.use_tls or args.port == 587:
            server.starttls()
            server.ehlo()
        server.login(args.username, args.password)
        to_list = [t.strip() for t in args.to_email.split(',')]
        
        # Enviar usando as_string() para mayor compatibilidad
        server.sendmail(args.from_email, to_list, msg.as_string())
        server.quit()
        
        if args.verbose:
            detalle_archivos = ", ".join(nombres_adjuntos)
            log_success(f"[{args.subject}] -> Enviado a: {args.to_email} | Archivos ({adjuntos_procesados}): {detalle_archivos}")
            print(f"Correo enviado con {adjuntos_procesados} adjuntos.")
            
        sys.exit(0)
    except Exception as e:
        log_error(str(e))
        print(f"Error SMTP: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
