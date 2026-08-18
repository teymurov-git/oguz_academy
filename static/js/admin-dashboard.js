/* ============================================
   OĞUZ TƏDRİS MƏRKƏZİ — Admin Dashboard JS
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    // Fade-in animations
    const cards = document.querySelectorAll('.otm-stat-card, .otm-stat-card-sm, .otm-chart-card, .otm-table-card, .otm-qa-btn');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                entry.target.style.animationDelay = (i * 0.05) + 's';
                entry.target.classList.add('otm-visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => observer.observe(card));

    // Auto-refresh stats every 5 minutes
    setTimeout(() => location.reload(), 300000);
});
