// Read existing public counters only. Never sends an analytics hit or delays navigation.
(async function loadDownloadClicks() {
  const counters = [
    ['download-tvbox-2-5-6', 'tvbox-current-clicks'],
    ['download-tvboxhome-1-2-0', 'home-current-clicks']
  ];
  await Promise.allSettled(counters.map(async ([event, id]) => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch(`https://tvbox.goatcounter.com/counter/${event}.json`, { signal: controller.signal });
      if (!response.ok) return;
      const data = await response.json();
      const raw = String(data.count ?? '').replace(/[\s,]/g, '');
      if (!/^\d+$/.test(raw)) return;
      const count = Number(raw);
      if (!Number.isSafeInteger(count)) return;
      const el = document.getElementById(id);
      if (el) el.textContent = new Intl.NumberFormat('ru-RU').format(count);
    } catch (_) {
      // Keep “нет данных”; an unavailable counter is not zero.
    } finally {
      clearTimeout(timeout);
    }
  }));
})();
