import { loadBalances } from './api/balance.js';
import { loadPrice } from './api/price.js';
import { loadBookTicker } from './api/bookTicker.js';
import { loadExchangeInfo } from './api/exchangeInfo.js';
import { loadDepth } from './api/depth.js';
import { loadAggTrades } from './api/aggTrades.js';
import { loadKlines } from './api/klines.js';
import { loadOrders } from './api/orders.js';
import { loadTrades } from './api/trades.js';

export async function refreshAll() {
    await Promise.all([
        loadBalances(),
        loadPrice(),
        loadBookTicker(),
        loadExchangeInfo(),
        loadDepth(),
        loadAggTrades(),
        loadKlines(),
        loadOrders(),
        loadTrades(),
    ]);
}

export function startAutoRefresh(interval = 30000) {
    refreshAll();
    setInterval(refreshAll, interval);
}
