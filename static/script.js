document.getElementById('run-tests').addEventListener('click', () => {
    fetch('/run_tests', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            document.getElementById('test-output').innerText = data.output;
        })
        .catch(error => {
            console.error('Erreur lors de l\'exécution des tests :', error);
        });
});
