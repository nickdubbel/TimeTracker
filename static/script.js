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

document.getElementById('uploadForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Serverfout: ${errorText}`);
        }

        const result = await response.json();

        // Controleer of result de verwachte structuur heeft
        if (result && result.summary) {
            // Vul de maandelijkse samenvattingstabel
            const summaryTableBody = document.querySelector('#monthlySummaryTable tbody');
            summaryTableBody.innerHTML = ''; // Reset de tabel
            if (Array.isArray(result.summary.monthly_summary)) {
                result.summary.monthly_summary.forEach((row) => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `<td>${row.month}</td><td>${row.duration.toFixed(2)}</td>`;
                    summaryTableBody.appendChild(tr);
                });
            }

            // Vul de gedetailleerde afspraken tabel
            const tableBody = document.querySelector('#detailedTable tbody');
            tableBody.innerHTML = ''; // Reset de tabel
            if (Array.isArray(result.summary.detailed_table)) {
                result.summary.detailed_table.forEach((row) => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `<td>${row.title}</td><td>${row.date}</td><td>${row.duration.toFixed(
                        2
                    )}</td>`;
                    tableBody.appendChild(tr);
                });
            }
        } else {
            throw new Error('Ongeldige API-response structuur');
        }
    } catch (error) {
        alert(`Er is een fout opgetreden: ${error.message}`);
    }
});

// document.getElementById('uploadForm2').addEventListener('submit', async function (e) {
//     e.preventDefault(); // Voorkomt standaardformulierverzending
//     const formData = new FormData(this);
//     const eventName = formData.get('event_name');

//     try {
//         const response = await fetch('/list-events', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({ event_name: eventName }),
//         });

//         if (!response.ok) {
//             throw new Error(`Serverfout: ${response.statusText}`);
//         }

//         const result = await response.json();
//         console.log('Resultaat ontvangen:', result);

//         // Verwerk het resultaat en vul de tabellen in
//         if (result && result.raw_events) {
//             const events = result.raw_events;

//             // Vul de maandelijkse samenvatting (optioneel aanpassen aan de structuur)
//             const monthlySummaryTable = document.querySelector('#monthlySummaryTable tbody');
//             monthlySummaryTable.innerHTML = ''; // Reset tabel
//             const eventMap = {}; // Tijdelijke opslag voor het samenvatten van duur per maand

//             events.forEach((event) => {
//                 const start = new Date(event.start.dateTime || event.start.date);
//                 const monthKey = `${start.getFullYear()}-${(start.getMonth() + 1)
//                     .toString()
//                     .padStart(2, '0')}`;
//                 const duration = (new Date(event.end.dateTime || event.end.date) - start) / (1000 * 3600);

//                 if (!eventMap[monthKey]) {
//                     eventMap[monthKey] = 0;
//                 }
//                 eventMap[monthKey] += duration;
//             });

//             Object.entries(eventMap).forEach(([month, duration]) => {
//                 const row = document.createElement('tr');
//                 row.innerHTML = `<td>${month}</td><td>${duration.toFixed(2)}</td>`;
//                 monthlySummaryTable.appendChild(row);
//             });

//             // Vul de gedetailleerde afspraken
//             const detailedTable = document.querySelector('#detailedTable tbody');
//             detailedTable.innerHTML = ''; // Reset tabel

//             events.forEach((event) => {
//                 const start = new Date(event.start.dateTime || event.start.date);
//                 const duration = (new Date(event.end.dateTime || event.end.date) - start) / (1000 * 3600);

//                 const row = document.createElement('tr');
//                 row.innerHTML = `
//                     <td>${event.summary}</td>
//                     <td>${start.toISOString().split('T')[0]}</td>
//                     <td>${duration.toFixed(2)}</td>`;
//                 detailedTable.appendChild(row);
//             });
//         } else {
//             alert('Geen evenementen gevonden');
//         }
//     } catch (error) {
//         console.error('Fout:', error);
//         alert(`Er is een fout opgetreden: ${error.message}`);
//     }
// });
