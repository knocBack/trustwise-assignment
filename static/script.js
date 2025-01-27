const scoreForm = document.getElementById('score-form');
const scoresContainer = document.getElementById('scores-container');
const historyContainer = document.getElementById('history-container');
const graphContainer = document.getElementById('graph-container');

// Keep track of the chart instances
let currentScoreChart = null;
let historyChart = null;

// Initialize empty dashboard
function initializeDashboard() {
    displayEmptyState();
    // Fetch initial data
    fetchScores();
}

function displayEmptyState() {
    scoresContainer.innerHTML = '<p>No analysis results yet. Enter text above to analyze.</p>';
    historyContainer.innerHTML = '<p>No analysis history available.</p>';
    graphContainer.innerHTML = '<p>Submit text for analysis to see visualizations.</p>';
}

async function fetchScores() {
    try {
        const response = await fetch('/scores');
        if (!response.ok) throw new Error('Failed to fetch scores');
        const data = await response.json();
        if (data.logs && data.logs.length > 0) {
            // console.log("Data:", data.logs);
            displayHistory(data.logs);
            // console.log("Displaying history")
            displayHistoryGraph(data.logs);
            // console.log("Displaying history graph")
            displayScores([data.logs[0]]); // Display latest score
            return data.logs;
        } else {
            displayEmptyState();
            // console.log("No data found");
            return [];
        }
    } catch (err) {
        console.error('Error fetching scores:', err);
        displayEmptyState();
        return [];
    }
}

async function fetchScoreById(id) {
    try {
        const response = await fetch(`/scores/${id}`);
        if (!response.ok) throw new Error('Failed to fetch score');
        const data = await response.json();
        if (data.log) {
            displayScores([data.log]);
            return data.log;
        }
    } catch (error) {
        console.error('Error fetching score:', error);
        alert('Failed to fetch the selected score.');
    }
}

async function deleteScore(id) {
    try {
        const response = await fetch(`/scores/${id}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error('Failed to delete score');
        await fetchScores(); // Refresh the list after deletion
        return true;
    } catch (error) {
        console.error('Error deleting score:', error);
        alert('Failed to delete the score.');
        return false;
    }
}

scoreForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    
    const submitButton = scoreForm.querySelector('button');
    const originalButtonText = submitButton.textContent;
    
    // Show loading states
    submitButton.innerHTML = '<span class="spinner"></span> Analyzing...';
    submitButton.disabled = true;
    document.querySelectorAll('.card').forEach(card => card.classList.add('loading'));

    try {
        const inputString = document.getElementById('input-string').value;
        const response = await fetch('/scores', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: inputString })
        });

        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        // Fetch updated data after successful submission
        const scores = await fetchScores();
        if (scores.length > 0) {
            // Display the latest score
            displayScores([scores[0]]);
            displayHistoryGraph(scores);
        }
        
        document.getElementById('input-string').value = '';
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while analyzing the text. Please try again.');
    } finally {
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
        document.querySelectorAll('.card').forEach(card => card.classList.remove('loading'));
    }
});

function formatScore(score, type) {
    if (score === null || score === undefined) return 'N/A';
    
    if (typeof score === 'number') {
        return score.toFixed(3);
    }
    
    if (typeof score === 'object') {
        if (type === 'emotion' || type === 'gibberish') {
            return `${score.label} (${score.score.toFixed(3)})`;
        }
        return JSON.stringify(score);
    }
    
    try {
        const parsed = JSON.parse(score);
        if (parsed.label && parsed.score) {
            return `${parsed.label} (${parsed.score.toFixed(3)})`;
        }
        return JSON.stringify(parsed);
    } catch {
        return score;
    }
}

function displayScores(scores) {
    scoresContainer.innerHTML = '';
    if (!scores || scores.length === 0) {
        scoresContainer.innerHTML = '<p>No scores available</p>';
        return;
    }

    const scoresTable = document.createElement('table');
    scoresTable.innerHTML = `
        <thead>
            <tr>
                <th>Metric</th>
                <th>Score</th>
                <th>Interpretation</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;

    const score = scores[0];
    const tbody = scoresTable.querySelector('tbody');
    
    const scoreRows = [
        {
            metric: 'Vectara Score',
            score: score.vectara_score,
            interpretation: 'Measures text consistency and reliability',
            type: 'vectara'
        },
        {
            metric: 'Toxicity Score',
            score: score.toxicity_score,
            interpretation: 'Indicates level of toxic content',
            type: 'toxicity'
        },
        {
            metric: 'Emotion Analysis',
            score: score.emotion_score,
            interpretation: 'Detects emotional content and intensity',
            type: 'emotion'
        },
        {
            metric: 'Gibberish Detection',
            score: score.gibberish_score,
            interpretation: 'Identifies meaningless or nonsensical text',
            type: 'gibberish'
        },
        {
            metric: 'Education Score',
            score: score.education_score,
            interpretation: 'Evaluates educational content quality',
            type: 'education'
        }
    ];

    scoreRows.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${row.metric}</strong></td>
            <td>${formatScore(row.score, row.type)}</td>
            <td><em>${row.interpretation}</em></td>
        `;
        tbody.appendChild(tr);
    });

    scoresContainer.appendChild(scoresTable);
    
    // Display the radar chart for the score
    displayRadarChart(score);
}

function displayHistory(history) {
    historyContainer.innerHTML = '';
    if (!history || history.length === 0) {
        historyContainer.innerHTML = '<p>No history available</p>';
        return;
    }

    const historyTable = document.createElement('table');
    historyTable.innerHTML = `
        <thead>
            <tr>
                <th>Time</th>
                <th>Input Text</th>
                <th>Scores Summary</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody></tbody>
    `;
    // console.log("History table template");
    const tbody = historyTable.querySelector('tbody');
    history.slice(0, 10).forEach((log) => { // Show last 10 entries
        const tr = document.createElement('tr');
        tr.style.cursor = 'pointer';
        
        tr.innerHTML = `
            <td>${new Date(log.timestamp).toLocaleString()}</td>
            <td>${log.input_string}</td>
            <td>
                <strong>Vectara:</strong> ${formatScore(log.vectara_score, 'vectara')}<br>
                <strong>Toxicity:</strong> ${formatScore(log.toxicity_score, 'toxicity')}<br>
                <strong>Education:</strong> ${formatScore(log.education_score, 'education')}<br>
                <strong>Emotion:</strong> ${formatScore(log.emotion_score, 'emotion')}<br>
                <strong>Gibberish:</strong> ${formatScore(log.gibberish_score, 'gibberish')}
            </td>
            <td>
                <button class="delete-btn">Delete</button>
            </td>
        `;

        // Add event listeners
        const deleteBtn = tr.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', async (event) => {
            event.stopPropagation();
            if (await deleteScore(log.id)) {
                await fetchScores(); // Refresh the entire list to keep it in sync
            }
        });

        tr.addEventListener('click', async () => {
            const score = await fetchScoreById(log.id);
            if (score) {
                displayScores([score]);
                tbody.querySelectorAll('tr').forEach(row => row.classList.remove('selected'));
                tr.classList.add('selected');
            }
        });

        tbody.appendChild(tr);
    });

    historyContainer.appendChild(historyTable);
}


function displayRadarChart(score) {
    // Only clear the radar chart
    if (currentScoreChart) {
        currentScoreChart.destroy();
    }
    
    // Create or clear the radar chart canvas
    const radarContainer = document.createElement('div');
    radarContainer.innerHTML = '<canvas id="analysisChart"></canvas>';
    
    // Replace existing radar chart or add as first child
    const existingRadar = graphContainer.querySelector('#analysisChart');
    if (existingRadar) {
        existingRadar.parentElement.replaceWith(radarContainer);
    } else {
        graphContainer.insertBefore(radarContainer, graphContainer.firstChild);
    }
    const ctx = document.getElementById('analysisChart').getContext('2d');
    
    const data = {
        labels: ['Vectara', 'Toxicity', 'Education', 'Emotion', 'Gibberish'],
        datasets: [{
            label: 'Score Analysis',
            data: [
                score.vectara_score,
                score.toxicity_score,
                score.education_score,
                typeof score.emotion_score === 'object' ? score.emotion_score.score : 0,
                typeof score.gibberish_score === 'object' ? score.gibberish_score.score : 0
            ],
            backgroundColor: 'rgba(52, 152, 219, 0.2)',
            borderColor: 'rgba(52, 152, 219, 1)',
            borderWidth: 2,
            pointBackgroundColor: 'rgba(52, 152, 219, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(52, 152, 219, 1)'
        }]
    };

    currentScoreChart = new Chart(ctx, {
        type: 'radar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        stepSize: 0.2
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: `Analysis Results for: "${score.input_string}"`,
                    padding: 20
                },
                legend: {
                    display: false
                }
            }
        }
    });
}

function displayHistoryGraph(history) {
    // Only update history graph if we're displaying the full history
    if (history.length <= 1) return;

    // Create or clear the history chart canvas
    let historyGraphContainer = graphContainer.querySelector('#historyChart')?.parentElement;
    if (!historyGraphContainer) {
        historyGraphContainer = document.createElement('div');
        historyGraphContainer.innerHTML = '<canvas id="historyChart"></canvas>';
        graphContainer.appendChild(historyGraphContainer);
    }

    // Clear previous chart
    if (historyChart) {
        historyChart.destroy();
    }

    const ctx = document.getElementById('historyChart').getContext('2d');
    
    // Process last 10 entries in reverse order (oldest to newest)
    const lastEntries = history.slice(0, 10).reverse();
    
    const data = {
        labels: lastEntries.map(log => new Date(log.timestamp).toLocaleTimeString()),
        datasets: [
            {
                label: 'Vectara Score',
                data: lastEntries.map(log => log.vectara_score),
                borderColor: 'rgba(52, 152, 219, 1)',
                fill: false
            },
            {
                label: 'Toxicity Score',
                data: lastEntries.map(log => log.toxicity_score),
                borderColor: 'rgba(231, 76, 60, 1)',
                fill: false
            },
            {
                label: 'Education Score',
                data: lastEntries.map(log => log.education_score),
                borderColor: 'rgba(46, 204, 113, 1)',
                fill: false
            }
        ]
    };

    historyChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Score History Trends',
                    padding: 20
                }
            }
        }
    });
}

// Initialize the dashboard when the page loads
initializeDashboard();
