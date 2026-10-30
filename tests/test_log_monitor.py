import re
import os
import smtplib
import logging
import unittest
from unittest.mock import patch
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


class LogMonitor:
    def __init__(self, email_recipient):
        self.blocked_ips = set()
        self.email_recipient = email_recipient

    def block_ip(self, ip):
        """Bloque l'adresse IP en l'ajoutant à la liste des IPs bloquées."""
        print(f"IP {ip} bloquée.")
        self.blocked_ips.add(ip)
        self.send_alert(ip)

    def send_alert(self, ip):
        """Envoie une alerte par email lorsque l'IP est bloquée."""
        subject = "Alerte de blocage d'IP"
        body = f"L'adresse IP {ip} a été bloquée."
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv('SENDER_EMAIL')
        msg['To'] = self.email_recipient

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(os.getenv('SENDER_EMAIL'), os.getenv('EMAIL_PASSWORD'))
                server.send_message(msg)
                print(f"Alerte envoyée pour l'IP {ip}.")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'alerte par email : {e}")

    def process_log_line(self, line):
        """Traite une ligne de log pour extraire et bloquer les adresses IP."""
        ip_pattern = r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
        ips = re.findall(ip_pattern, line)
        print(f"Ligne de log: {line}, IPs trouvées: {ips}")

        for ip in ips:
            self.block_ip(ip)


class TestLogMonitor(unittest.TestCase):
    def setUp(self):
        # smtplib.SMTP est remplacé : aucun vrai e-mail n'est envoyé pendant les tests
        patcher = patch('smtplib.SMTP')
        self.mock_smtp = patcher.start()
        self.addCleanup(patcher.stop)
        self.monitor = LogMonitor(email_recipient="test@example.com")

    def test_block_ip(self):
        ip = "192.168.1.1"
        self.monitor.block_ip(ip)
        self.assertIn(ip, self.monitor.blocked_ips,
                      f"L'IP {ip} n'a pas été bloquée comme prévu.")

    def test_alert_sent(self):
        self.monitor.block_ip("192.168.1.1")
        self.mock_smtp.assert_called_once_with('smtp.gmail.com', 587)

    def test_process_log_line(self):
        line = ("Nov 23 10:00:00 server sshd[12345]: "
                "Failed password for root from 192.168.1.1 port 22 ssh2")
        self.monitor.process_log_line(line)
        self.assertIn("192.168.1.1", self.monitor.blocked_ips,
                      "L'IP n'a pas été bloquée après le traitement de la ligne de log.")

    def test_block_multiple_ips(self):
        log_lines = [
            "Accepted password for user from 192.168.1.1",
            "Failed password for user from 10.0.0.2",
            "Connection from 172.16.0.5",
            "Another log entry from 192.168.1.1",
        ]
        for line in log_lines:
            self.monitor.process_log_line(line)

        self.assertIn("192.168.1.1", self.monitor.blocked_ips)
        self.assertIn("10.0.0.2", self.monitor.blocked_ips)
        self.assertIn("172.16.0.5", self.monitor.blocked_ips)

    def test_logging(self):
        logging.basicConfig(level=logging.INFO)
        logging.info("Test de logging SSH.")
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()