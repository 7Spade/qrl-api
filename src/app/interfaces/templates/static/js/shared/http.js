export async function fetchJson(path, options = {}) {
    const res = await fetch(path, options);
    if (!res.ok) {
        const err = new Error(`HTTP ${res.status}`);
        err.status = res.status;
        throw err;
    }
    return res.json();
}
