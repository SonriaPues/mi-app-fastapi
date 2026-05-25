// ═══ main.js — Funcionalidad global ═══

// Toggle dropdown de usuario y menú de hamburguesa
document.addEventListener('DOMContentLoaded', () => {
    const userMenu = document.getElementById('nav-user-menu');
    const menuBtn = document.getElementById('user-menu-btn');
    if (menuBtn && userMenu) {
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userMenu.classList.toggle('active');
        });
        document.addEventListener('click', () => userMenu.classList.remove('active'));
    }

    // Hamburger Menu Mobile
    const hamburger = document.getElementById('nav-hamburger');
    const navMenu = document.getElementById('nav-menu');
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', (e) => {
            e.stopPropagation();
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });

        // Cerrar menú al hacer click en el contenido principal
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        }
    }

    // Toggle password visibility
    document.querySelectorAll('.toggle-password').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.parentElement.querySelector('input');
            input.type = input.type === 'password' ? 'text' : 'password';
            btn.textContent = input.type === 'password' ? '👁️' : '🙈';
        });
    });

    // Favoritos toggle (AJAX)
    document.querySelectorAll('.fav-btn, .btn-fav-detail').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            const bookId = btn.dataset.bookId;
            try {
                const res = await fetch(`/api/v1/books/${bookId}/favorite`, { method: 'POST' });
                if (res.status === 401) { window.location.href = '/login'; return; }
                const data = await res.json();
                if (data.action === 'added') {
                    btn.classList.add('active');
                    btn.innerHTML = btn.classList.contains('btn-fav-detail') ?
                        '<span class="fav-icon">❤️</span><span class="fav-text">En favoritos</span>' : '❤️';
                } else {
                    btn.classList.remove('active');
                    btn.innerHTML = btn.classList.contains('btn-fav-detail') ?
                        '<span class="fav-icon">🤍</span><span class="fav-text">Agregar a favoritos</span>' : '🤍';
                }
                showToast(data.message, 'success');
            } catch { showToast('Error al actualizar favorito', 'error'); }
        });
    });

    // Auto-hide alerts
    document.querySelectorAll('.alert').forEach(a => {
        setTimeout(() => { a.style.opacity = '0'; setTimeout(() => a.remove(), 300); }, 4000);
    });
});

// Toast notifications
function showToast(msg, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 300); }, 3000);
}
