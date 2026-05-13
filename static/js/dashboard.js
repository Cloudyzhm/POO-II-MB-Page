function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-btn').forEach(el => {
        el.classList.remove('text-brand-red', 'border-brand-red');
        el.classList.add('text-gray-500', 'border-transparent');
    });
    const panel = document.getElementById('panel-' + tab);
    if (panel) panel.classList.remove('hidden');
    const btn = document.getElementById('tab-' + tab);
    if (btn) {
        btn.classList.remove('text-gray-500', 'border-transparent');
        btn.classList.add('text-brand-red', 'border-brand-red');
    }
    const url = new URL(window.location);
    url.searchParams.set('tab', tab);
    window.history.replaceState({}, '', url);
}

document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab') || 'pasajes';
    const tabBtn = document.getElementById('tab-' + tab);
    if (tabBtn) switchTab(tab);
});