async function fetchLogs() {
    const response = await fetch('/logs');
    const logs = await response.json();

    const logsDiv = document.getElementById('logs');
    logsDiv.innerHTML = '';

    logs.forEach(log => {
        const entry = document.createElement('div');
        entry.className = 'entry';
        entry.innerHTML = `
            <p><strong>${log.person_name}</strong> at ${log.timestamp}<br>
            Image: ${log.image_name}</p>
            <img src="${log.image_url}" alt="Face image" width="200">
        `;
        logsDiv.appendChild(entry);
    });
}

fetchLogs();
setInterval(fetchLogs, 10000);
