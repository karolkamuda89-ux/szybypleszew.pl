/*
 * Skrypty strony: cień headera, menu mobilne i podświetlanie aktywnej pozycji menu.
 * Całość w funkcji wywoływanej od razu (IIFE), żeby zmienne nie trafiały do zasięgu globalnego.
 */
(function () {
    var header = document.querySelector('.site-header');
    var toggle = document.querySelector('.nav-toggle');   // przycisk "hamburger" (widoczny na telefonie)
    var nav = document.getElementById('main-nav');

    // --- Cień pod headerem po przewinięciu --------------------------------
    // Klasa is-scrolled dodaje w CSS ciemniejsze tło i cień, gdy strona jest przewinięta.
    function onScroll() {
        header.classList.toggle('is-scrolled', window.scrollY > 10);
    }
    onScroll();  // od razu, gdy strona otworzy się już przewinięta (np. po odświeżeniu)
    window.addEventListener('scroll', onScroll, { passive: true });

    // --- Menu mobilne -----------------------------------------------------
    // Otwiera/zamyka menu i aktualizuje atrybuty dla czytników ekranu.
    function setMenu(open) {
        nav.classList.toggle('is-open', open);
        toggle.setAttribute('aria-expanded', String(open));
        toggle.setAttribute('aria-label', open ? 'Zamknij menu' : 'Otwórz menu');
    }
    toggle.addEventListener('click', function () {
        setMenu(!nav.classList.contains('is-open'));
    });
    // Kliknięcie w link (np. "Oferta") przewija do sekcji, więc menu ma się zamknąć
    nav.addEventListener('click', function (e) {
        if (e.target.closest('a')) setMenu(false);
    });
    // Klawisz Esc też zamyka menu
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') setMenu(false);
    });

    // --- Podświetlanie aktywnej sekcji w menu -----------------------------
    // Linki z atrybutem data-section wskazują sekcje strony głównej (np. data-section="oferta").
    // Na podstronach (np. blog) tych sekcji nie ma, więc skrypt kończy działanie.
    var links = nav.querySelectorAll('a[data-section]');
    var sections = [];
    links.forEach(function (link) {
        var section = document.getElementById(link.dataset.section);
        if (section) sections.push(section);
    });
    if (!sections.length || !('IntersectionObserver' in window)) return;

    // IntersectionObserver zgłasza, która sekcja jest na środku ekranu.
    // rootMargin zawęża "okno obserwacji" do wąskiego paska w połowie wysokości ekranu,
    // więc aktywna jest zawsze ta sekcja, którą użytkownik akurat czyta.
    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            links.forEach(function (link) {
                link.classList.toggle('is-active', link.dataset.section === entry.target.id);
            });
        });
    }, { rootMargin: '-45% 0px -50% 0px' });

    sections.forEach(function (section) { observer.observe(section); });
})();

/*
 * Galeria: przycisk "Pokaż więcej zdjęć" i powiększanie zdjęć (lightbox).
 * Osobna funkcja, bo powyższa kończy działanie na podstronach bez sekcji (return).
 */
(function () {
    var gallery = document.getElementById('gallery');
    if (!gallery) return;  // galerii nie ma na tej stronie (np. blog)

    // --- "Pokaż więcej zdjęć": odkrywa zdjęcia z atrybutem hidden -----------
    var moreBtn = document.getElementById('gallery-more');
    if (moreBtn) {
        moreBtn.addEventListener('click', function () {
            gallery.querySelectorAll('.gallery-item[hidden]').forEach(function (item) {
                item.hidden = false;
            });
            moreBtn.parentElement.remove();  // przycisk nie jest już potrzebny
        });
    }

    // --- Lightbox -----------------------------------------------------------
    var dialog = document.getElementById('lightbox');
    // Bez obsługi <dialog> (bardzo stare przeglądarki) linki po prostu otworzą zdjęcie w karcie
    if (!dialog || typeof dialog.showModal !== 'function') return;

    var img = dialog.querySelector('img');
    var caption = dialog.querySelector('figcaption');
    var current = 0;

    // Lista widocznych zdjęć liczona za każdym razem, bo "Pokaż więcej" dokłada nowe
    function visibleLinks() {
        return Array.prototype.filter.call(gallery.querySelectorAll('.gallery-link'), function (a) {
            return !a.closest('.gallery-item').hidden;
        });
    }

    function show(index) {
        var links = visibleLinks();
        // Zapętlenie: za ostatnim zdjęciem jest pierwsze i odwrotnie
        current = (index + links.length) % links.length;
        var link = links[current];
        img.src = link.href;
        img.alt = link.dataset.caption;
        caption.textContent = link.dataset.caption;
    }

    gallery.addEventListener('click', function (e) {
        var link = e.target.closest('.gallery-link');
        if (!link) return;
        e.preventDefault();  // zamiast otwierać plik, pokazujemy go w oknie
        show(visibleLinks().indexOf(link));
        dialog.showModal();
    });

    dialog.querySelector('.lightbox-close').addEventListener('click', function () { dialog.close(); });
    dialog.querySelector('.lightbox-prev').addEventListener('click', function () { show(current - 1); });
    dialog.querySelector('.lightbox-next').addEventListener('click', function () { show(current + 1); });

    // Kliknięcie w ciemne tło (poza zdjęciem i przyciskami) zamyka okno
    dialog.addEventListener('click', function (e) {
        if (e.target === dialog) dialog.close();
    });

    // Strzałki na klawiaturze przełączają zdjęcia (Esc zamyka okno sam <dialog>)
    dialog.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowLeft') show(current - 1);
        if (e.key === 'ArrowRight') show(current + 1);
    });

    // Po zamknięciu czyścimy obrazek, żeby przy następnym otwarciu nie mignęło stare zdjęcie
    dialog.addEventListener('close', function () { img.removeAttribute('src'); });
})();
