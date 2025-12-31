import { setText, formatNumber } from "../../shared/time.js";

export async function loadPrice() {
    try {
        const res = await fetch("/market/ticker/QRLUSDT");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const ticker = data.data || {};
        const price = parseFloat(ticker.lastPrice || ticker.price || "0");
        const change = parseFloat(ticker.priceChangePercent || "0");
        setText("price", formatNumber(price, 6));
        setText(
            "change",
            `${formatNumber(change, 2)}%`,
            change >= 0 ? "var(--success)" : "var(--danger)"
        );
        setText("updated", new Date().toLocaleString("zh-TW"));
    } catch (err) {
        setText("price", "ERROR", "var(--danger)");
        setText("change", "--");
        setText("updated", "");
        console.error("Price load failed", err);
    }
}

export default loadPrice;
