import { setText } from '../utils.js';

export async function loadBookTicker() {
    try {
        const res = await fetch('/market/book-ticker/QRLUSDT');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const book = data.data || {};
        setText('best-bid', `${book.bidPrice || '--'} / ${book.bidQty || '--'}`);
        setText('best-ask', `${book.askPrice || '--'} / ${book.askQty || '--'}`);
    } catch (err) {
        setText('best-bid', 'ERROR', 'var(--danger)');
        setText('best-ask', 'ERROR', 'var(--danger)');
        console.error('Book ticker failed', err);
    }
}
