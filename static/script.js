function toggleInstructions() {
    const details = document.getElementById('instructions-details');
    const toggleText = document.getElementById('toggle-text');
    if (details.style.display === 'none' || details.style.display === '') {
        details.style.display = 'block';
        toggleText.innerHTML = '<b>[Verberg]</b>';
    } else {
        details.style.display = 'none';
        toggleText.innerHTML = '<b>[Toon]</b>';
    }
}

document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Serverfout: ${errorText}`);
        }

        const result = await response.json();

        // Vul de tabel met maandelijkse samenvatting
        const summaryTableBody = document.querySelector('#monthlySummaryTable tbody');
        summaryTableBody.innerHTML = ""; // Reset de tabel
        result.monthly_summary.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${row.month}</td><td>${row.duration.toFixed(2)}</td>`;
            summaryTableBody.appendChild(tr);
        });

        // Vul de tabel met gedetailleerde afspraken
        const tableBody = document.querySelector('#detailedTable tbody');
        tableBody.innerHTML = ""; // Reset de tabel
        result.detailed_table.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${row.title}</td><td>${row.date}</td><td>${row.duration.toFixed(2)}</td>`;
            tableBody.appendChild(tr);
        });
    } catch (error) {
        alert(`Er is een fout opgetreden: ${error.message}`);
    }
});
