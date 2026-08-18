/* ============================================
   Oğuz Tədris Mərkəzi — Admin Theme JS
   ============================================ */
(function(){
    // --- Theme: apply saved or system preference immediately ---
    const saved = localStorage.getItem('otm-theme');
    if (saved) {
        document.documentElement.setAttribute('data-theme', saved);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
        document.documentElement.setAttribute('data-theme', 'light');
    }
})();

document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('main');
    const toggle = document.getElementById('sidebarToggle');
    const overlay = document.getElementById('sidebarOverlay');

    // --- Sidebar Toggle ---
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('active', sidebar.classList.contains('open'));
        });
    }

    // --- Close sidebar on overlay click ---
    if (overlay && sidebar) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }

    // --- Close sidebar on mobile when clicking nav links ---
    if (sidebar) {
        sidebar.querySelectorAll('.otm-nav-item').forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 1024) {
                    sidebar.classList.remove('open');
                    if (overlay) overlay.classList.remove('active');
                }
            });
        });
    }

    // --- User Menu Dropdown ---
    const userTrigger = document.getElementById('userMenuTrigger');
    const userDropdown = document.getElementById('userDropdown');
    if (userTrigger && userDropdown) {
        userTrigger.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('show');
        });
        document.addEventListener('click', () => {
            userDropdown.classList.remove('show');
        });
    }

    // --- Theme Toggle ---
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme');
            const next = current === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('otm-theme', next);

            // Re-init Lucide icons so new icons render correctly
            if (window.lucide) {
                window.lucide.createIcons();
            }
        });
    }

    // --- Lucide Icons ---
    if (window.lucide) {
        window.lucide.createIcons();
    }
});
