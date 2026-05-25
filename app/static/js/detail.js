// ═══ detail.js — Funcionalidad de la página de detalle del libro ═══

document.addEventListener('DOMContentLoaded', () => {
    // Star picker interactivo
    document.querySelectorAll('.star-picker').forEach(picker => {
        const stars = picker.querySelectorAll('.star-pick');
        stars.forEach((star, idx) => {
            star.addEventListener('mouseenter', () => {
                stars.forEach((s, i) => s.classList.toggle('active', i <= idx));
            });
            star.addEventListener('click', () => {
                picker.dataset.value = idx + 1;
            });
        });
        picker.addEventListener('mouseleave', () => {
            const val = parseInt(picker.dataset.value || '5');
            stars.forEach((s, i) => s.classList.toggle('active', i < val));
        });
    });

    // Crear reseña
    const createForm = document.getElementById('create-review-form');
    if (createForm) {
        createForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const bookId = createForm.dataset.bookId;
            const rating = parseInt(document.querySelector('#star-picker-new').dataset.value || '5');
            const comment = document.getElementById('new-comment').value;
            try {
                const res = await fetch(`/api/v1/books/${bookId}/reviews`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ rating, comment })
                });
                if (res.ok) { location.reload(); }
                else {
                    const data = await res.json();
                    showToast(data.detail || 'Error al crear reseña', 'error');
                }
            } catch { showToast('Error de conexión', 'error'); }
        });
    }

    // Editar reseña
    const editForm = document.getElementById('edit-review-form');
    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const reviewId = editForm.dataset.reviewId;
            const rating = parseInt(document.querySelector('#star-picker-edit').dataset.value || '5');
            const comment = document.getElementById('edit-comment').value;
            try {
                const res = await fetch(`/api/v1/reviews/${reviewId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ rating, comment })
                });
                if (res.ok) { showToast('Reseña actualizada', 'success'); }
                else { showToast('Error al actualizar', 'error'); }
            } catch { showToast('Error de conexión', 'error'); }
        });
    }

    // Eliminar reseña propia
    const deleteBtn = document.getElementById('delete-review-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', async () => {
            if (!confirm('¿Eliminar tu reseña?')) return;
            const reviewId = deleteBtn.dataset.reviewId;
            try {
                const res = await fetch(`/api/v1/reviews/${reviewId}`, { method: 'DELETE' });
                if (res.ok) { location.reload(); }
                else { showToast('Error al eliminar', 'error'); }
            } catch { showToast('Error de conexión', 'error'); }
        });
    }
});

// Admin delete review
async function deleteReviewAdmin(reviewId) {
    if (!confirm('¿Eliminar esta reseña?')) return;
    try {
        const res = await fetch(`/api/v1/reviews/${reviewId}`, { method: 'DELETE' });
        if (res.ok) { document.getElementById(`review-card-${reviewId}`)?.remove(); showToast('Reseña eliminada'); }
        else { showToast('Error', 'error'); }
    } catch { showToast('Error de conexión', 'error'); }
}
