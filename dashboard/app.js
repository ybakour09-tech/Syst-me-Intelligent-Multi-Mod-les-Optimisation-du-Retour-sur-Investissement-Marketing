const API_URL = "http://localhost:8000";

// --- DOM Elements ---
const inputs = {
    tv: document.getElementById('tvBudget'),
    radio: document.getElementById('radioBudget'),
    social: document.getElementById('socialBudget')
};

const displays = {
    tv: document.getElementById('tvValue'),
    radio: document.getElementById('radioValue'),
    social: document.getElementById('socialValue')
};

const outputs = {
    sales: document.getElementById('salesValue'),
    roi: document.getElementById('roiValue'),
    perf: document.getElementById('perfValue'),
    baseRoi: document.getElementById('baseRoi')
};

const shapUI = {
    tv: { fill: document.getElementById('shapFillTv'), val: document.getElementById('shapValTv') },
    radio: { fill: document.getElementById('shapFillRadio'), val: document.getElementById('shapValRadio') },
    social: { fill: document.getElementById('shapFillSocial'), val: document.getElementById('shapValSocial') },
    perf: { fill: document.getElementById('shapFillPerf'), val: document.getElementById('shapValPerf') }
};

const btnSales = document.getElementById('btnSales');
const btnShap = document.getElementById('btnShap');

// --- Global Chart Setup ---
let variationChart;
let simulationCount = 0;
const chartLabels = [];
const roiData = [];
const salesData = [];

function initChart() {
    const ctx = document.getElementById('variationChart').getContext('2d');
    variationChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [
                {
                    label: 'ROI Estimé (%)',
                    data: roiData,
                    borderColor: '#4facfe',
                    backgroundColor: 'rgba(79, 172, 254, 0.2)',
                    yAxisID: 'y-roi',
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#4facfe',
                    pointRadius: 4,
                    borderWidth: 2
                },
                {
                    label: 'Ventes Estimées (K€)',
                    data: salesData,
                    borderColor: '#00f2fe',
                    backgroundColor: 'rgba(0, 242, 254, 0.1)',
                    yAxisID: 'y-sales',
                    tension: 0.3,
                    fill: false,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#00f2fe',
                    pointRadius: 4,
                    borderWidth: 2,
                    borderDash: [5, 5]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: { color: '#9ba1a6', font: { family: 'Inter' } }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#9ba1a6', font: { family: 'Inter' } }
                },
                'y-roi': {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'ROI (%)', color: '#4facfe', font: { family: 'Inter' } },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#4facfe', font: { family: 'Inter' } }
                },
                'y-sales': {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Ventes (K€)', color: '#00f2fe', font: { family: 'Inter' } },
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#00f2fe', font: { family: 'Inter' } }
                }
            }
        }
    });
}

function addDataToChart(roi, sales) {
    simulationCount++;
    chartLabels.push(`Sim ${simulationCount}`);
    roiData.push(roi);
    salesData.push(sales);
    
    // Garder les 10 dernières simulations pour que le graphe reste lisible
    if (chartLabels.length > 10) {
        chartLabels.shift();
        roiData.shift();
        salesData.shift();
    }
    variationChart.update();
}

// --- Event Listeners ---
Object.keys(inputs).forEach(key => {
    inputs[key].addEventListener('input', (e) => {
        displays[key].textContent = parseFloat(e.target.value).toFixed(1);
    });
});

btnSales.addEventListener('click', runSalesPrediction);
btnShap.addEventListener('click', runShapAnalysis);

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    runShapAnalysis();
});

// --- Core Logic ---

function getPayloadAndInvestment() {
    const tvBudget = parseFloat(inputs.tv.value);
    const radioBudget = parseFloat(inputs.radio.value);
    const socialBudget = parseFloat(inputs.social.value);
    const totalInvestment = tvBudget + radioBudget + socialBudget;
    
    const payload = {
        "TV": tvBudget,
        "Radio": radioBudget,
        "Social Media": socialBudget
    };
    return { payload, totalInvestment };
}

async function runSalesPrediction() {
    setLoadingState(btnSales, true);
    const { payload, totalInvestment } = getPayloadAndInvestment();

    try {
        const res = await fetch(`${API_URL}/predict/roi`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error("Erreur de communication API.");
        const data = await res.json();
        
        // Fetch performance to keep UI consistent
        const perfRes = await fetch(`${API_URL}/predict/performance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const perfData = await perfRes.json();
        outputs.perf.textContent = perfData.Performance_Prediction;
        
        const roiPredicted = data.ROI_Prediction_Percentage;
        animateValue(outputs.roi, parseFloat(outputs.roi.textContent) || 0, roiPredicted, 1000);
        
        const expectedSales = totalInvestment > 0 ? totalInvestment * (roiPredicted / 100 + 1) : 0;
        animateValue(outputs.sales, parseFloat(outputs.sales.textContent) || 0, expectedSales, 1000);

        addDataToChart(roiPredicted, expectedSales);

    } catch (error) {
        console.error(error);
    } finally {
        setLoadingState(btnSales, false, "Prédiction de Ventes & ROI");
    }
}

async function runShapAnalysis() {
    setLoadingState(btnShap, true);
    const { payload, totalInvestment } = getPayloadAndInvestment();

    try {
        const [perfRes, shapRes] = await Promise.all([
            fetch(`${API_URL}/predict/performance`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }),
            fetch(`${API_URL}/predict/shap_impact`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
        ]);

        if (!perfRes.ok || !shapRes.ok) throw new Error("Erreur API.");

        const perfData = await perfRes.json();
        const shapData = await shapRes.json();

        updateUI(perfData, shapData, totalInvestment);
        
        const expectedSales = totalInvestment > 0 ? totalInvestment * (shapData.Predicted_ROI / 100 + 1) : 0;
        addDataToChart(shapData.Predicted_ROI, expectedSales);

    } catch (error) {
        console.error(error);
    } finally {
        setLoadingState(btnShap, false, "Analyse SHAP Complète");
    }
}

// --- UI Updates ---

function updateUI(perfData, shapData, totalInvestment) {
    outputs.perf.textContent = perfData.Performance_Prediction;

    const roiPredicted = shapData.Predicted_ROI;
    animateValue(outputs.roi, parseFloat(outputs.roi.textContent) || 0, roiPredicted, 1000);
    outputs.baseRoi.textContent = `${shapData.Base_ROI_Average}%`;

    const expectedSales = totalInvestment > 0 ? totalInvestment * (roiPredicted / 100 + 1) : 0;
    animateValue(outputs.sales, parseFloat(outputs.sales.textContent) || 0, expectedSales, 1000);

    const maxShapRange = 40; 
    updateShapRow(shapUI.tv, shapData.SHAP_Impact_Breakdown["TV"], maxShapRange);
    updateShapRow(shapUI.radio, shapData.SHAP_Impact_Breakdown["Radio"], maxShapRange);
    updateShapRow(shapUI.social, shapData.SHAP_Impact_Breakdown["Social Media"], maxShapRange);
    updateShapRow(shapUI.perf, shapData.SHAP_Impact_Breakdown["Performance"], maxShapRange);
}

function updateShapRow(uiElements, value, maxRange) {
    const isPositive = value >= 0;
    const sign = isPositive ? "+" : "";
    uiElements.val.textContent = `${sign}${value.toFixed(1)}%`;
    uiElements.val.className = `shap-value ${isPositive ? 'pos' : 'neg'}`;

    let widthPercent = (Math.abs(value) / maxRange) * 50;
    if (widthPercent > 50) widthPercent = 50; 

    uiElements.fill.className = `shap-fill ${isPositive ? 'shap-positive' : 'shap-negative'}`;
    uiElements.fill.style.width = `${widthPercent}%`;
    
    if (isPositive) {
        uiElements.fill.style.left = "50%";
    } else {
        uiElements.fill.style.left = `${50 - widthPercent}%`;
    }
}

function setLoadingState(btn, isLoading, originalText = "") {
    if (isLoading) {
        btn.textContent = "Calcul...";
        btn.style.opacity = "0.7";
    } else {
        btn.textContent = originalText;
        btn.style.opacity = "1";
    }
}

// Simple counter animation
function animateValue(obj, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const current = start + progress * (end - start);
        obj.innerHTML = current.toFixed(1);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}
