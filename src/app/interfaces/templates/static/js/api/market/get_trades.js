import { formatTime } from "../../shared/time.js";
import { logError } from "../../shared/errors.js";

export async function loadAggTrades() {
    const body = document.getElementById("agg-body");
    try {
        const res = await fetch("/market/agg-trades/QRLUSDT?limit=10");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const trades = data.data || [];
        if (!trades.length) {
            body.innerHTML = '<tr><td colspan="4" class="hint">無成交</td></tr>';
            return;
        }
        body.innerHTML = trades.slice(0, 10).map((t) => {
            const side = t.isBuyerMaker ? "SELL" : "BUY";
            return `<tr><td>${formatTime(t.T || t.time)}</td><td><span class="tag">${side}</span></td><td>${t.p || "--"}</td><td>${t.q || "--"}</td></tr>`;
        }).join("");
    } catch (err) {
        body.innerHTML = '<tr><td colspan="4" class="error">Agg trades 載入失敗</td></tr>';
        logError("Agg trades failed", err);
    }
}

export default loadAggTrades;
