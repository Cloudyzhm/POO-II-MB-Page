AOS.init({ duration: 800, once: true, offset: 50 });

const nav = document.getElementById('main-nav');
window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
        nav.classList.remove('bg-brand-black', 'border-transparent');
        nav.classList.add('bg-brand-black/95', 'backdrop-blur-md', 'border-white/10', 'shadow-md');
    } else {
        nav.classList.add('bg-brand-black', 'border-transparent');
        nav.classList.remove('bg-brand-black/95', 'backdrop-blur-md', 'border-white/10', 'shadow-md');
    }
});

document.getElementById('mobile-menu-btn')?.addEventListener('click', function() {
    document.getElementById('mobile-menu').classList.toggle('hidden');
});

const tabsData = {
    'compra': { btn: 'tab-compra', panel: 'panel-compra' },
    'anula': { btn: 'tab-anula', panel: 'panel-anula' },
};

function activateTab(selectedKey) {
    Object.keys(tabsData).forEach(key => {
        const btn = document.getElementById(tabsData[key].btn);
        const panel = document.getElementById(tabsData[key].panel);
        if (key === selectedKey) {
            panel.classList.remove('hidden');
            panel.classList.add('block');
            btn.className = "flex-1 py-3 px-4 bg-white text-brand-red border-b-[3px] border-brand-red shadow-sm rounded-xl flex items-center justify-center gap-2 transition-all outline-none transform scale-100";
        } else {
            panel.classList.add('hidden');
            panel.classList.remove('block');
            btn.className = "flex-1 py-3 px-4 text-gray-500 hover:text-brand-black border-b-[3px] border-transparent rounded-xl flex items-center justify-center gap-2 transition-all outline-none";
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    const dateInputCompra = document.getElementById('fecha-compra');
    if(dateInputCompra) dateInputCompra.value = today;
});

function swapDestinations(origenId, destinoId, btnElement) {
    const origenSelect = document.getElementById(origenId);
    const destinoSelect = document.getElementById(destinoId);
    const origenVal = origenSelect.value;
    const destinoVal = destinoSelect.value;
    if (!origenVal || !destinoVal) {
        triggerShakeAnimation(btnElement);
        return;
    }
    const canSwapToOrigen = Array.from(origenSelect.options).some(opt => opt.value === destinoVal);
    const canSwapToDestino = Array.from(destinoSelect.options).some(opt => opt.value === origenVal);
    if (canSwapToOrigen && canSwapToDestino) {
        origenSelect.value = destinoVal;
        destinoSelect.value = origenVal;
        const icon = btnElement.querySelector('i');
        if (icon) {
            icon.style.transition = 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            let currentRot = parseInt(icon.getAttribute('data-rot') || '0');
            currentRot += 180;
            icon.style.transform = `rotate(${currentRot}deg)`;
            icon.setAttribute('data-rot', currentRot);
        }
    } else {
        triggerShakeAnimation(btnElement);
    }
}

function triggerShakeAnimation(element) {
    element.classList.remove('animate-shake');
    void element.offsetWidth;
    element.classList.add('animate-shake');
}

function openMapModal(title, url) {
    const modal = document.getElementById('map-modal');
    const content = document.getElementById('map-modal-content');
    const iframe = document.getElementById('map-iframe');
    document.getElementById('map-modal-title-text').innerText = title;
    iframe.src = url;
    modal.classList.remove('hidden');
    void modal.offsetWidth;
    content.classList.remove('scale-95', 'opacity-0');
    content.classList.add('scale-100', 'opacity-100');
    document.body.style.overflow = 'hidden';
}

function closeMapModal() {
    const modal = document.getElementById('map-modal');
    const content = document.getElementById('map-modal-content');
    const iframe = document.getElementById('map-iframe');
    content.classList.remove('scale-100', 'opacity-100');
    content.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        modal.classList.add('hidden');
        iframe.src = '';
        document.body.style.overflow = '';
    }, 300);
}

document.addEventListener('keydown', function(event) {
    if (event.key === "Escape") {
        const mapModal = document.getElementById('map-modal');
        if (!mapModal.classList.contains('hidden')) {
            closeMapModal();
        }
    }
});