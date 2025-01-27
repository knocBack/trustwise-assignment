const scoreForm = document.getElementById('score-form');
const scoresContainer = document.getElementById('scores-container');
const historyContainer = document.getElementById('history-container');
const graphContainer = document.getElementById('graph-container');

scoreForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const inputString = document.getElementById('input-string').value;
    const response = await fetch('/scores', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: inputString })
    });
    const data = await response.json();
    displayScores(data.scores);
    displayHistory(data.history);
    displayGraph(data.scores);
});

async function displayScores(scores) {
    scoresContainer.innerHTML = '';
    const scoresTable = document.createElement('table');
    scoresTable.innerHTML = `
        <tr>
            <th>Input String</th>
            <th>Score 1</th>
            <th>Score 2</th>
            <th>Score 3</th>
            <th>Score 4</th>
            <th>Score 5</th>
        </tr>
    `;
    scores.forEach((score) => {
        const scoreRow = document.createElement('tr');
        scoreRow.innerHTML = `
            <td>${score.input_string}</td>
            <td>${score.vectara_score}</td>
            <td>${score.toxicity_score}</td>
            <td>${JSON.stringify(score.emotion_score)}</td>
            <td>${JSON.stringify(score.gibberish_score)}</td>
            <td>${score.education_score}</td>
        `;
        scoresTable.appendChild(scoreRow);
    });
    scoresContainer.appendChild(scoresTable);
}

async function displayHistory(history) {
    historyContainer.innerHTML = '';
    const historyTable = document.createElement('table');
    historyTable.innerHTML = `
        <tr>
            <th>Input String</th>
            <th>Result</th>
        </tr>
    `;
    history.forEach((log) => {
        const logRow = document.createElement('tr');
        logRow.innerHTML = `
            <td>${log.input_string}</td>
            <td>${JSON.stringify(log.scores)}</td>
        `;
        historyTable.appendChild(logRow);
    });
    historyContainer.appendChild(historyTable);
}

async function displayGraph(scores) {
    graphContainer.innerHTML = '';
    scores.forEach((score) => {
        const chartContainer = document.createElement('div');
        chartContainer.innerHTML = `
            <canvas id="chart-${score.id}"></canvas>
        `;
        graphContainer.appendChild(chartContainer);

        const ctx = document.getElementById(`chart-${score.id}`).getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Education', 'Emotion', 'Gibberish', 'Toxicity', 'Vectara'],
                datasets: [{
                    label: score.input_string,
                    data: [score.education_score, score.emotion_score.score, score.gibberish_score.score, score.toxicity_score, score.vectara_score],
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });
    });
}