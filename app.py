from flask import Flask, render_template, jsonify
import os
import subprocess

app = Flask(__name__)
LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs', 'app.log')
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/logs')
def logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as file:
            log_content = file.readlines()
    else:
        log_content = ["Aucun log disponible."]
    return render_template('logs.html', logs=log_content)
@app.route('/run_tests', methods=['POST'])
def run_tests():
    result = subprocess.run(['python3', '-m', 'unittest', 'discover', 'tests'], capture_output=True, text=True)
    return jsonify({'output': result.stdout})

if __name__ == '__main__':
    app.run(debug=True)
