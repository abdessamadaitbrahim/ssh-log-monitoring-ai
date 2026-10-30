#!/usr/bin/env python3
import subprocess
import datetime

def run_tests():
    test_file = 'tests/test_log_monitor.py'
    command = ['python', '-m', 'unittest', test_file]

    # ici pour executer la commande
    with open('tests/test_log_monitor.log', 'a') as log_file:
        log_file.write(f"Running tests at {datetime.datetime.now()}\n")
        result = subprocess.run(command, stdout=log_file, stderr=subprocess.STDOUT)

        if result.returncode == 0:
            log_file.write("Tests completed successfully.\n")
        else:
            log_file.write("Tests failed.\n")

if __name__ == "__main__":
    run_tests()
