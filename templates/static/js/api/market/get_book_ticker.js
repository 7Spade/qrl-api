import { setText } from "../../shared/time.js";
import { logError } from "../../shared/errors.js";

export async function loadBookTicker() {
    try {
        const res = await fetch("/market/book-ticker/QRLUSDT");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const book = data.data || {};
        setText("best-bid", `${book.bidPrice || "--"} / ${book.bidQty || "--"}`);
        setText("best-ask", `${book.askPrice || "--"} / ${book.askQty || "--"}`);
    } catch (err) {
        setText("best-bid", "ERROR", "var(--danger)");
        setText("best-ask", "ERROR", "var(--danger)");
        logError("Book ticker failed", err);
    }
}

export default loadBookTicker;
