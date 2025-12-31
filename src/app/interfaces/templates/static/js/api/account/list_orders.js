import { formatTime } from "../../shared/time.js";

export async function loadOrders() {
    const body = document.getElementById("orders-body");
    try {
        const res = await fetch("/account/orders");
        if (res.status === 503) {
            body.innerHTML =
                '<tr><td colspan="6" class="hint">需要 API key 才能讀取</td></tr>';
            return;
        }
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const orders = data.orders || [];
        if (!orders.length) {
            body.innerHTML = '<tr><td colspan="6" class="hint">目前沒有訂單</td></tr>';
            return;
        }
        body.innerHTML = orders
            .map((o) => {
                const side = (o.side || "").toUpperCase();
                const ts = o.time || o.updateTime || o.transactTime;
                return `<tr><td>${formatTime(ts)}</td><td><span class="tag">${side || "--"}</span></td><td>${o.price || "--"}</td><td>${o.origQty || "--"}</td><td>${o.executedQty || "--"}</td><td>${o.status || "--"}</td></tr>`;
            })
            .join("");
    } catch (err) {
        body.innerHTML = `<tr><td colspan="6" class="error">訂單載入失敗</td></tr>`;
        console.error("Orders load failed", err);
    }
}

export default loadOrders;
