export async function loadExchangeInfo() {
    const body = document.getElementById('info-body');
    try {
        const res = await fetch('/market/exchange-info?symbol=QRLUSDT');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const info = data.data || {};
        const symbols = info.symbols || [];
        if (!symbols.length) {
            body.innerHTML = '<tr><td colspan="4" class="hint">無資料</td></tr>';
            return;
        }
        const s = symbols[0];
        const lot = s?.filters?.find?.(f => f.filterType === 'LOT_SIZE');
        const minQty = lot?.minQty || '--';
        const notional = s?.filters?.find?.(f => f.filterType === 'NOTIONAL');
        const minNotional = notional?.minNotional || '--';
        body.innerHTML = `<tr><td>${s.symbol}</td><td>${s.status || '--'}</td><td>${minQty}</td><td>${minNotional}</td></tr>`;
    } catch (err) {
        body.innerHTML = '<tr><td colspan="4" class="error">載入失敗</td></tr>';
        console.error('Exchange info failed', err);
    }
}
