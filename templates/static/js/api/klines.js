import { formatTime } from '../utils.js';

export async function loadKlines() {
    const body = document.getElementById('kline-body');
    try {
        const res = await fetch('/market/klines/QRLUSDT?interval=1m&limit=5');
        if (res.status === 404) {
            body.innerHTML = '<tr><td colspan="5" class="hint">僅支援 QRLUSDT</td></tr>';
            return;
        }
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const klines = data.data || [];
        if (!klines.length) {
            body.innerHTML = '<tr><td colspan="5" class="hint">無K線資料</td></tr>';
            return;
        }
        body.innerHTML = klines.slice(-5).map(k => {
            return `<tr><td>${formatTime(k[0])}</td><td>${k[1]}</td><td>${k[2]}</td><td>${k[3]}</td><td>${k[4]}</td></tr>`;
        }).join('');
    } catch (err) {
        body.innerHTML = '<tr><td colspan="5" class="hint">無K線資料</td></tr>';
        console.error('Klines failed', err);
    }
}
