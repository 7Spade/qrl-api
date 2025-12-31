import { formatTime } from "../../shared/time.js";

export async function loadTrades() {
    const body = document.getElementById("trades-body");
    try {
        const res = await fetch("/account/trades");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const trades = data.trades || [];
        if (!trades.length) {
            body.innerHTML = '<tr><td colspan="6" class="hint">目前沒有成交</td></tr>';
            return;
        }
        body.innerHTML = trades
            .map((t) => {
                const isBuyer = t.isBuyer || t.isBuyerMaker;
                const side = isBuyer ? "BUY" : "SELL";
                const amount =
                    t.quoteQty ||
                    (t.price && t.qty
                        ? (parseFloat(t.price) * parseFloat(t.qty)).toFixed(4)
                        : "--");
                return `<tr><td>${formatTime(t.time || t.transactTime)}</td><td><span class="tag">${side}</span></td><td>${t.price || "--"}</td><td>${t.qty || "--"}</td><td>${amount}</td><td>${t.commission || "--"} ${t.commissionAsset || ""}</td></tr>`;
            })
            .join("");
    } catch (err) {
        body.innerHTML = `<tr><td colspan="6" class="error">成交載入失敗</td></tr>`;
        console.error("Trades load failed", err);
    }
}

export default loadTrades;
