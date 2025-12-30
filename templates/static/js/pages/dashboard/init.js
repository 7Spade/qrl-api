import { startAutoRefresh } from "../../refresh.js";

export function initDashboard() {
    const refreshBtn = document.getElementById("refresh-btn");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", startAutoRefresh);
    }
    startAutoRefresh();
}

export default initDashboard;
