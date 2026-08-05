---
title: "Výdrž baterie pro low-power projekty..."
date: 2026-06-19T23:16:00Z
url: "/posts/2025/12/vydrz-z-baterie/"
tags: ["Bastlení"]
aliases:
  - "/2025/12/vydrz-z-baterie.html"
---

<div id="vydrz-kalkulacka">
    <style>
        #vydrz-kalkulacka {
            --bg-color: #f4f6f9;
            --surface-color: #ffffff;
            --text-color: #333333;
            --primary-color: #00994d;
            --accent-color: #d32f2f;
            --border-color: #e0e0e0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            padding: 15px;
            width: 100%;
            box-sizing: border-box;
        }
        #vydrz-kalkulacka * {
            box-sizing: border-box;
        }
        #vydrz-kalkulacka .container {
            width: 100%;
            display: grid;
            grid-template-columns: 1fr;
            gap: 20px;
        }
        #vydrz-kalkulacka .card {
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        #vydrz-kalkulacka h1 {
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 0;
            font-size: 2rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            line-height: 1.2;
        }
        #vydrz-kalkulacka h2 {
            font-size: 1.2rem;
            margin-top: 0;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
            color: var(--text-color);
            margin-bottom: 15px;
        }
        #vydrz-kalkulacka .form-group {
            margin-bottom: 15px;
        }
        #vydrz-kalkulacka label {
            display: block;
            margin-bottom: 5px;
            font-size: 0.9rem;
            color: #555;
            font-weight: 500;
        }
        #vydrz-kalkulacka input[type="number"], 
        #vydrz-kalkulacka input[type="text"],
        #vydrz-kalkulacka select {
            width: 100%;
            padding: 8px;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            background-color: #fff;
            color: var(--text-color);
            font-size: 0.95rem;
            transition: border-color 0.2s;
        }
        #vydrz-kalkulacka input:focus,
        #vydrz-kalkulacka select:focus {
            outline: none;
            border-color: var(--primary-color);
        }
        #vydrz-kalkulacka .action-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        #vydrz-kalkulacka .btn-action {
            flex: 1;
            min-width: 140px;
            padding: 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            color: white;
            transition: opacity 0.2s;
            font-size: 0.9rem;
            text-align: center;
        }
        #vydrz-kalkulacka .btn-action:hover { opacity: 0.85; }
        #vydrz-kalkulacka .btn-save { background-color: #0288d1; }
        #vydrz-kalkulacka .btn-load { background-color: #f57c00; }
        #vydrz-kalkulacka .tasks-section {
            background: #f8f9fa;
            border: 1px solid var(--border-color);
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            overflow-x: auto;
        }
        #vydrz-kalkulacka .tasks-header {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1.2fr 40px;
            gap: 8px;
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 5px;
            font-weight: bold;
            min-width: 400px;
        }
        #vydrz-kalkulacka .task-row {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1.2fr 40px;
            gap: 8px;
            margin-bottom: 10px;
            align-items: center;
            min-width: 400px;
        }
        #vydrz-kalkulacka .btn-add {
            background-color: #e8f5e9;
            color: var(--primary-color);
            border: 1px dashed var(--primary-color);
            padding: 10px;
            width: 100%;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.2s;
        }
        #vydrz-kalkulacka .btn-add:hover { background-color: #c8e6c9; }
        #vydrz-kalkulacka .btn-remove {
            background-color: #ffeeee;
            color: var(--accent-color);
            border: 1px solid #ffcdd2;
            padding: 8px 0;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            width: 100%;
        }
        #vydrz-kalkulacka .btn-remove:hover { background-color: #ffcdd2; }
        #vydrz-kalkulacka .result-box {
            background-color: #f8f9fa;
            border: 1px solid var(--border-color);
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            text-align: center;
        }
        #vydrz-kalkulacka .result-title { font-size: 0.9rem; color: #555; }
        #vydrz-kalkulacka .result-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--primary-color);
            margin: 10px 0;
            line-height: 1.2;
        }
        #vydrz-kalkulacka .result-stats {
            font-size: 0.85rem;
            color: #666;
            display: flex;
            justify-content: space-between;
            margin-top: 15px;
        }
        #vydrz-kalkulacka .chart-container {
            position: relative;
            height: 350px;
            width: 100%;
        }
    </style>

    <div class="container">
        <h1>VYDRŽ!</h1>
        <div class="card">
            <div class="action-buttons">
                <button class="btn-action btn-save" onclick="saveConfig()">💾 Uložit nastavení</button>
                <button class="btn-action btn-load" onclick="document.getElementById('fileLoader').click()">📂 Načíst nastavení</button>
                <input accept=".json" id="fileLoader" onchange="loadConfig(event)" style="display: none;" type="file" />
            </div>

            <h2>Základní parametry</h2>
            
            <div class="form-group">
                <label>Typ baterie (Chemie)</label>
                <select id="batteryType">
                    <option value="liion">Li-Ion / Li-Po</option>
                    <option value="lifepo4">LiFePO4</option>
                </select>
            </div>
            <div class="form-group">
                <label>Kapacita baterie (mAh)</label>
                <input id="capacity" type="number" value="2500" />
            </div>
            <div class="form-group">
                <label>Vypínací napětí (V)</label>
                <input id="cutoff" max="4.2" type="number" value="3.4" />
            </div>
            <div class="form-group">
                <label>Odběr v hlubokém spánku (µA)</label>
                <input id="sleepCurrent" type="number" value="50" />
            </div>
            <div class="form-group">
                <label>Samovybíjení baterie (% za měsíc)</label>
                <input id="selfDischarge" type="number" value="2" />
            </div>

            <h2>Aktivní stavy (Probuzení)</h2>
            <div class="tasks-section">
                <div class="tasks-header">
                    <div>Název úkonu</div>
                    <div>Odběr (mA)</div>
                    <div>Čas (s)</div>
                    <div>Každých (min)</div>
                    <div></div>
                </div>
                <div id="tasksList">
                    <!--Dynamické řádky se vloží sem-->
                </div>
                <button class="btn-add" onclick="addTask('', 100, 5, 15)" type="button">+ Přidat další aktivitu</button>
            </div>
        </div>

        <div class="card">
            <h2>Výsledky simulace</h2>
            <div class="result-box">
                <div class="result-title">Odhadovaná výdrž</div>
                <div class="result-value" id="lifeText">Počítám...</div>
                <div class="result-stats">
                    <span id="avgCurrentText">Průměrný odběr: 0 mA</span>
                    <span id="usableCapText">Využitelná kap: 0 mAh</span>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="dischargeChart"></canvas>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    let chartInstance = null;

    function saveConfig() {
        const config = {
            batteryType: document.getElementById('batteryType').value,
            capacity: document.getElementById('capacity').value,
            cutoff: document.getElementById('cutoff').value,
            sleepCurrent: document.getElementById('sleepCurrent').value,
            selfDischarge: document.getElementById('selfDischarge').value,
            tasks: []
        };

        document.querySelectorAll('.task-row').forEach(row => {
            config.tasks.push({
                name: row.querySelector('.task-name').value,
                ma: row.querySelector('.task-ma').value,
                sec: row.querySelector('.task-sec').value,
                min: row.querySelector('.task-min').value
            });
        });

        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(config, null, 2));
        const downloadAnchorNode = document.createElement('a');
        downloadAnchorNode.setAttribute("href", dataStr);
        downloadAnchorNode.setAttribute("download", "vydrz_nastaveni.json");
        document.body.appendChild(downloadAnchorNode);
        downloadAnchorNode.click();
        downloadAnchorNode.remove();
    }

    function loadConfig(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const config = JSON.parse(e.target.result);

                if (config.batteryType) document.getElementById('batteryType').value = config.batteryType;
                if (config.capacity) document.getElementById('capacity').value = config.capacity;
                if (config.cutoff) document.getElementById('cutoff').value = config.cutoff;
                if (config.sleepCurrent) document.getElementById('sleepCurrent').value = config.sleepCurrent;
                if (config.selfDischarge) document.getElementById('selfDischarge').value = config.selfDischarge;

                document.getElementById('tasksList').innerHTML = '';
                if (config.tasks && Array.isArray(config.tasks)) {
                    config.tasks.forEach(task => {
                        addTask(task.name, task.ma, task.sec, task.min);
                    });
                }

                updateCalculations();
            } catch (err) {
                alert("Chyba při čtení souboru: Soubor není platný JSON formát.");
            }
            event.target.value = '';
        };
        reader.readAsText(file);
    }

    function getUsedFractionByVoltage(v, chem) {
        if (chem === 'lifepo4') {
            if (v >= 3.65) return 0;
            if (v <= 2.5) return 1.0;
            // 0-10% (3.65V -> 3.3V)
            if (v > 3.3) return (3.65 - v) * (0.10 / 0.35);
            // 10-90% (3.3V -> 3.1V)
            if (v > 3.1) return 0.10 + (3.3 - v) * (0.80 / 0.20);
            // 90-100% (3.1V -> 2.5V)
            return 0.90 + (3.1 - v) * (0.10 / 0.60);
        } else {
            if (v >= 4.2) return 0;
            if (v <= 3.0) return 1.0;
            if (v > 4.0) return (4.2 - v) * (0.15 / 0.2);
            if (v > 3.6) return 0.15 + (4.0 - v) * (0.70 / 0.4);
            return 0.85 + (3.6 - v) * (0.15 / 0.6);
        }
    }

    function getVoltageByUsedFraction(fraction, chem) {
        if (chem === 'lifepo4') {
            if (fraction <= 0.10) return 3.65 - fraction * (0.35 / 0.10);
            if (fraction <= 0.90) return 3.3 - (fraction - 0.10) * (0.20 / 0.80);
            if (fraction <= 1.00) return 3.1 - (fraction - 0.90) * (0.60 / 0.10);
            return 2.5;
        } else {
            if (fraction <= 0.15) return 4.2 - fraction * (0.2 / 0.15);
            if (fraction <= 0.85) return 4.0 - (fraction - 0.15) * (0.4 / 0.70);
            if (fraction <= 1.00) return 3.6 - (fraction - 0.85) * (0.6 / 0.15);
            return 3.0;
        }
    }

    function formatTime(hours) {
        if (!isFinite(hours)) return "Nekonečno (?)";
        if (hours < 24) return `${Math.floor(hours)} hodin`;
        let days = hours / 24;
        if (days < 30) return `${Math.floor(days)} dní, ${Math.floor((days % 1) * 24)} hod`;
        let months = days / 30.44;
        if (months < 12) return `${Math.floor(months)} měsíců, ${Math.floor((months % 1) * 30.44)} dní`;
        let years = months / 12;
        return `${Math.floor(years)} let, ${Math.floor((years % 1) * 12)} měsíců`;
    }

    function addTask(name = "", ma = 0, sec = 0, min = 0) {
        const list = document.getElementById('tasksList');
        const row = document.createElement('div');
        row.className = 'task-row';
        row.innerHTML = `
            <input type="text" placeholder="Např. Senzor" class="task-name" value="${name}">
            <input type="number" placeholder="mA" class="task-ma" value="${ma || ''}" step="1" min="0">
            <input type="number" placeholder="s" class="task-sec" value="${sec || ''}" step="0.1" min="0">
            <input type="number" placeholder="min" class="task-min" value="${min || ''}" step="0.5" min="0">
            <button type="button" class="btn-remove" onclick="this.parentElement.remove(); updateCalculations();" title="Smazat">✖</button>
        `;
        list.appendChild(row);
        updateCalculations();
    }

    function updateCalculations() {
        const chem = document.getElementById('batteryType').value;
        const cap = parseFloat(document.getElementById('capacity').value) || 0;
        const cutoff = parseFloat(document.getElementById('cutoff').value) || 3.0; // Odstraněn override přes chemii
        const sleepUa = parseFloat(document.getElementById('sleepCurrent').value) || 0;
        const selfDischargePct = parseFloat(document.getElementById('selfDischarge').value) || 0;

        if (cap <= 0) return;

        let totalActiveAvgMa = 0;
        let totalDutyCycle = 0;

        document.querySelectorAll('.task-row').forEach(row => {
            const ma = parseFloat(row.querySelector('.task-ma').value) || 0;
            const sec = parseFloat(row.querySelector('.task-sec').value) || 0;
            const min = parseFloat(row.querySelector('.task-min').value) || 0;

            if (min > 0 && sec > 0) {
                const dutyCycle = sec / (min * 60);
                totalDutyCycle += dutyCycle;
                totalActiveAvgMa += ma * dutyCycle;
            }
        });

        const sleepDutyCycle = Math.max(0, 1 - totalDutyCycle);
        const sleepMa = (sleepUa / 1000) * sleepDutyCycle;
        const selfDischargeMa = (cap * (selfDischargePct / 100)) / (30.44 * 24);

        const totalAvgMa = totalActiveAvgMa + sleepMa + selfDischargeMa;
        const usedFractionAtCutoff = getUsedFractionByVoltage(cutoff, chem);
        const usableCap = cap * usedFractionAtCutoff;

        const lifeHours = usableCap / totalAvgMa;
        const lifeDays = lifeHours / 24;

        document.getElementById('lifeText').innerText = formatTime(lifeHours);

        let currentDisplay = totalAvgMa < 1 ? `${(totalAvgMa * 1000).toFixed(1)} µA` : `${totalAvgMa.toFixed(3)} mA`;
        document.getElementById('avgCurrentText').innerText = `Průměrný odběr: ${currentDisplay}`;
        document.getElementById('usableCapText').innerText = `Využitelná kap: ${Math.round(usableCap)} mAh (${Math.round(usedFractionAtCutoff * 100)}%)`;

        const points = 50;
        let labels = [];
        let dataVoltage = [];

        for (let i = 0; i <= points; i++) {
            let tDays = (i / points) * lifeDays;
            labels.push(tDays.toFixed(1));
            let consumedCapacity = (tDays * 24) * totalAvgMa;
            let currentFraction = consumedCapacity / cap;
            dataVoltage.push(getVoltageByUsedFraction(currentFraction, chem));
        }

        drawChart(labels, dataVoltage, cutoff, lifeDays, chem);
    }

    function drawChart(labels, dataVoltage, cutoff, maxDays, chem) {
        const ctx = document.getElementById('dischargeChart').getContext('2d');

        let unit = 'Dny';
        if (maxDays > 90) {
            unit = 'Měsíce';
            labels = labels.map(day => (parseFloat(day) / 30.44).toFixed(1));
        }

        const cutoffData = labels.map(() => cutoff);

        // Rozsah y se stále dynamicky mění pro lepší zobrazení grafu
        const yMin = chem === 'lifepo4' ? 2.4 : 2.8;
        const yMax = chem === 'lifepo4' ? 3.8 : 4.3;

        if (chartInstance) {
            chartInstance.destroy();
        }

        chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Napětí baterie (V)',
                        data: dataVoltage,
                        borderColor: '#00994d',
                        backgroundColor: 'rgba(0, 153, 77, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 0,
                        tension: 0.3
                    },
                    {
                        label: 'Vypínací napětí (Cutoff)',
                        data: cutoffData,
                        borderColor: '#d32f2f',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: 'index' },
                scales: {
                    y: { 
                        min: yMin, 
                        max: yMax, 
                        title: { display: true, text: 'Napětí (V)', color: '#555' }, 
                        grid: { color: '#e0e0e0' }, 
                        ticks: { color: '#666' } 
                    },
                    x: { 
                        title: { display: true, text: `Čas (${unit})`, color: '#555' }, 
                        grid: { color: '#e0e0e0' }, 
                        ticks: { color: '#666', maxTicksLimit: 10 } 
                    }
                },
                plugins: { legend: { labels: { color: '#555' } } }
            }
        });
    }

    setTimeout(() => {
        addTask("Rychlé měření (Senzor)", 20, 1, 5);
        addTask("Odeslání dat (WiFi)", 150, 3, 60);
        document.getElementById('vydrz-kalkulacka').addEventListener('input', updateCalculations);
        document.getElementById('batteryType').addEventListener('change', updateCalculations); // Pouze přepočítej, nepřepisuj cutoff
    }, 500);
</script>