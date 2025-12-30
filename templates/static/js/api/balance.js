import { setText, formatNumber } from '../utils.js';

export async function loadBalances() {
    try {
        const res = await fetch('/account/balance');
        if (res.status === 503) {
            setText('qrl-total', 'NEED API KEY', 'var(--warning)');
            setText('usdt-total', 'NEED API KEY', 'var(--warning)');
            return;
        }
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const balances = data.balances || {};
        const qrl = balances.QRL || { free: '0', locked: '0' };
        const usdt = balances.USDT || { free: '0', locked: '0' };
        const qrlFree = parseFloat(qrl.free);
        const qrlLocked = parseFloat(qrl.locked);
        const qrlTotal = parseFloat(qrl.total ?? (qrlFree + qrlLocked));
        const qrlValue = parseFloat(qrl.value_usdt ?? '0');
        const usdtFree = parseFloat(usdt.free);
        const usdtLocked = parseFloat(usdt.locked);
        const usdtTotal = parseFloat(usdt.total ?? (usdtFree + usdtLocked));

        setText('qrl-total', formatNumber(qrlTotal));
        setText('qrl-value', formatNumber(qrlValue, 2));
        setText('qrl-free', formatNumber(qrlFree));
        setText('qrl-locked', formatNumber(qrlLocked));
        setText('usdt-total', formatNumber(usdtTotal, 2));
        setText('usdt-free', formatNumber(usdtFree, 2));
        setText('usdt-locked', formatNumber(usdtLocked, 2));
    } catch (err) {
        setText('qrl-total', 'ERROR', 'var(--danger)');
        setText('usdt-total', 'ERROR', 'var(--danger)');
        console.error('Balance load failed', err);
    }
}
