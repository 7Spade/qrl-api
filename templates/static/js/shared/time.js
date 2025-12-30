export const setText = (id, text, color) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = text;
    el.style.color = color || "";
};

export const formatNumber = (num, digits = 4) =>
    Number.isNaN(num) ? "--" : num.toFixed(digits);

export const formatTime = (ts) => {
    if (!ts) return "--";
    const d = new Date(ts);
    return Number.isNaN(d.getTime()) ? "--" : d.toLocaleString("zh-TW");
};
