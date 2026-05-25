// ═══ auth.js — Password strength indicator ═══
document.addEventListener('DOMContentLoaded', () => {
    const pw = document.getElementById('password');
    const fill = document.getElementById('strength-fill');
    const label = document.getElementById('strength-label');
    if (!pw || !fill) return;
    pw.addEventListener('input', () => {
        const v = pw.value;
        let score = 0;
        if (v.length >= 8) score++;
        if (/[A-Z]/.test(v)) score++;
        if (/[0-9]/.test(v)) score++;
        if (/[^A-Za-z0-9]/.test(v)) score++;
        const colors = ['#EF4444','#F59E0B','#06B6D4','#10B981'];
        const labels = ['Débil','Regular','Buena','Fuerte'];
        fill.style.width = (score * 25) + '%';
        fill.style.background = colors[score - 1] || '#362c54';
        label.textContent = v.length === 0 ? 'Escribe una contraseña' : labels[score - 1] || 'Muy débil';
    });
});
