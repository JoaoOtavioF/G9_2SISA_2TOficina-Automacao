import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configura logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

def get_smtp_config():
    class ConfigEmail:
        """Configurações de email"""
        def __init__(self):
            self.smtp_server = "smtp.gmail.com"
            self.smtp_port = 587
            self.email_remetente = "2toficinasptech@gmail.com"
            self.senha = "spgdqpqqiwtezvnb"  # Senha de app sem espaços
            self.nome_oficina = "2T Oficina"

    return ConfigEmail()

app = Flask(__name__)
CORS(app)


def send_email_smtp(to_email: str, subject: str, html_body: str) -> None:
    cfg = get_smtp_config()

    if not cfg.email_remetente or not cfg.senha:
        raise RuntimeError("Credenciais SMTP não configuradas. Verifique ConfigEmail.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{cfg.nome_oficina} <{cfg.email_remetente}>"
    msg["To"] = to_email
    part_html = MIMEText(html_body, "html", "utf-8")
    msg.attach(part_html)

    logger.info("Conectando ao servidor SMTP %s:%s", cfg.smtp_server, cfg.smtp_port)
    with smtplib.SMTP(cfg.smtp_server, cfg.smtp_port) as server:
        server.starttls()
        server.login(cfg.email_remetente, cfg.senha)
        server.send_message(msg)


@app.route("/send-verification", methods=["POST"])
def send_verification():
    """Recebe JSON com `email` e `code` e envia o código por e-mail.

    JSON esperado: { "email": "destino@ex.com", "code": "123456", "name": "Nome (opcional)", "subject": "Assunto (opcional)" }
    """
    raw = request.get_data(as_text=True)
    logger.info("Request headers: %s", dict(request.headers))
    logger.info("Request raw body: %s", raw)

    if not request.is_json:
        return jsonify({"success": False, "error": "Requisição não contém JSON. Use header 'Content-Type: application/json' e envie body JSON."}), 400

    data = request.get_json(silent=False) or {}
    email = data.get("email")
    code = data.get("code")
    name = data.get("name", "")
    subject = data.get("subject")

    if not email or code is None:
        return jsonify({"success": False, "error": "Campos 'email' e 'code' são obrigatórios."}), 400

    if "@" not in email:
        return jsonify({"success": False, "error": "Formato de email inválido."}), 400

    cfg = get_smtp_config()
    if not cfg.email_remetente or not cfg.senha:
        return jsonify({"success": False, "error": "Servidor SMTP não configurado (ver ConfigEmail)."}), 500

    saudacao = f"Olá {name}," if name else "Olá," 
    subject = subject or f"Código de verificação - {cfg.nome_oficina}"

    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <p>{saudacao}</p>
        <p>Seu código de verificação é:</p>
        <h2 style="letter-spacing:6px;">{code}</h2>
        <p style="font-size: 0.9em; color: #666;">Esse código expira em alguns minutos. Não o compartilhe com ninguém.</p>
        <p>Atenciosamente,<br>{cfg.nome_oficina}</p>
      </body>
    </html>
    """

    try:
        send_email_smtp(email, subject, html)
        logger.info("Código enviado para %s", email)
        return jsonify({"success": True, "message": f"Código enviado para {email}"}), 200
    except Exception as e:
        logger.exception("Erro ao enviar email")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    logger.info("Iniciando API de verificação na porta %s", port)
    app.run(host="0.0.0.0", port=port, debug=True)
