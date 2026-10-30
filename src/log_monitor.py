import pandas as pd
import time
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import joblib
import logging
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class LogMonitor:
    def __init__(self):
        log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        logging.basicConfig(
            filename=os.path.join(log_dir, 'ssh_activity.log'),
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.model = joblib.load(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'ssh_ai_model.pkl'))
        self.blocked_ips = set()
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.receiver_email = os.getenv("RECEIVER_EMAIL")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        if not all([self.sender_email, self.receiver_email, self.email_password]):
            raise ValueError("Variables SENDER_EMAIL, RECEIVER_EMAIL et EMAIL_PASSWORD manquantes (voir .env.example)")

    def monitor_logs(self):
        with open("/var/log/auth.log", "r") as log_file:
            log_file.seek(0, 2)
            logging.info("Démarrage de la surveillance des logs SSH.")
            while True:
                line = log_file.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                self.process_log_line(line)

    def process_log_line(self, line):
        parts = line.split()
        if len(parts) < 11:
            return

        user = parts[8]
        ip = parts[10]
        status = 'accepted' if 'Accepted' in line else 'failed'
        logging.info(f"Connexion {status} pour l'utilisateur {user} depuis l'IP {ip}")

        features = pd.DataFrame([{
            'is_private': 0,
            'is_root': 1 if user == 'root' else 0,
            'is_valid': 1,
            'ip_failure': 1 if status == 'failed' else 0,
            'ip_success': 1 if status == 'accepted' else 0,
            'no_failure': 0
        }])

        prediction = self.model.predict(features)[0]
        if prediction == -1:
            logging.warning(f"Anomalie détectée pour l'IP : {ip}")
            self.block_ip(ip)
            self.send_alert(ip)

    def block_ip(self, ip):
        if ip not in self.blocked_ips:
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
            self.blocked_ips.add(ip)
            logging.info(f"IP bloquée : {ip}")

    def send_alert(self, ip):
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = self.receiver_email
        message['Subject'] = "Alerte : Anomalie détectée"
        body = f"Une anomalie a été détectée pour l'IP : {ip}. Elle a été bloquée."
        message.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(self.sender_email, self.email_password)
                server.send_message(message)
                logging.info(f"Alerte envoyée pour l'IP : {ip}")
        except Exception as e:
            logging.error(f"Erreur lors de l'envoi de l'alerte : {e}")

if __name__ == "__main__":
    monitor = LogMonitor()
    monitor.monitor_logs()
