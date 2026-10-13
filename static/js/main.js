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
 * Galeria realizacji:
 *  - kafelki z kilkoma zdjęciami: strzałki ‹ ›, licznik "2 / 5" i przesuwanie palcem,
 *  - przycisk "Pokaż więcej realizacji",
 *  - powiększenie (lightbox) ze zdjęciami klikniętej realizacji.
 * Osobna funkcja, bo powyższa kończy działanie na podstronach bez sekcji (return).
 */
(function () {
    var gallery = document.getElementById('gallery');
    if (!gallery) return;  // galerii nie ma na tej stronie (np. blog)

    // --- Przewijanie zdjęć w kafelku --------------------------------------
    // Zdjęcia kafelka leżą jedno na drugim; widoczne jest to z klasą is-active.
    function setSlide(tile, index) {
        var slides = tile.querySelectorAll('.gallery-link');
        var count = slides.length;
        index = (index + count) % count;  // zapętlenie: za ostatnim jest pierwsze
        slides.forEach(function (slide, i) { slide.classList.toggle('is-active', i === index); });
        tile.dataset.index = index;

        var counter = tile.querySelector('.gallery-counter');
        if (counter) counter.textContent = (index + 1) + ' / ' + count;

        // Opis etapu (np. "Demontaż starej szyby") pod tytułem kafelka
        var step = tile.querySelector('.gallery-step');
        var text = slides[index].dataset.caption;
        step.textContent = text;
        step.hidden = !text;
    }

    function currentSlide(tile) { return parseInt(tile.dataset.index || '0', 10); }

    gallery.addEventListener('click', function (e) {
        var nav = e.target.closest('.gallery-nav');
        if (!nav) return;
        var tile = nav.closest('.gallery-item');
        setSlide(tile, currentSlide(tile) + (nav.classList.contains('gallery-next') ? 1 : -1));
    });

    // Przesuwanie palcem na telefonie: ruch w poziomie o min. 40 px zmienia zdjęcie
    var touchX = null;
    var swiped = false;
    gallery.addEventListener('touchstart', function (e) {
        touchX = e.touches[0].clientX;
        swiped = false;
    }, { passive: true });
    gallery.addEventListener('touchend', function (e) {
        if (touchX === null) return;
        var tile = e.target.closest('.gallery-item');
        var dx = e.changedTouches[0].clientX - touchX;
        touchX = null;
        if (!tile || tile.querySelectorAll('.gallery-link').length < 2 || Math.abs(dx) < 40) return;
        swiped = true;  // żeby przesunięcie nie zostało potraktowane jak kliknięcie (otwarcie powiększenia)
        setSlide(tile, currentSlide(tile) + (dx < 0 ? 1 : -1));
    });

    // --- "Pokaż więcej realizacji": odkrywa kafelki z atrybutem hidden ------
    var moreBtn = document.getElementById('gallery-more');
    if (moreBtn) {
        moreBtn.addEventListener('click', function () {
            gallery.querySelectorAll('.gallery-item[hidden]').forEach(function (item) {
                item.hidden = false;
            });
            moreBtn.parentElement.remove();  // przycisk nie jest już potrzebny
        });
    }

    // --- Lightbox: powiększenie zdjęć jednej realizacji ---------------------
    var dialog = document.getElementById('lightbox');
    // Bez obsługi <dialog> (bardzo stare przeglądarki) linki po prostu otworzą zdjęcie w karcie
    if (!dialog || typeof dialog.showModal !== 'function') return;

    var img = dialog.querySelector('img');
    var caption = dialog.querySelector('figcaption');
    var navButtons = dialog.querySelectorAll('.lightbox-nav');
    var openTile = null;   // kafelek, którego zdjęcia oglądamy
    var current = 0;

    function show(index) {
        var slides = openTile.querySelectorAll('.gallery-link');
        current = (index + slides.length) % slides.length;
        var slide = slides[current];
        img.src = slide.href;
        // Podpis: tytuł realizacji + opis etapu + numer zdjęcia, jeśli jest ich kilka
        var parts = [openTile.dataset.title];
        if (slide.dataset.caption) parts.push(slide.dataset.caption);
        if (slides.length > 1) parts.push((current + 1) + ' / ' + slides.length);
        caption.textContent = parts.join(' · ');
        img.alt = parts.slice(0, 2).join(' – ');
        // Kafelek przewija się razem z powiększeniem, więc po zamknięciu widać ostatnie oglądane zdjęcie
        setSlide(openTile, current);
    }

    gallery.addEventListener('click', function (e) {
        var link = e.target.closest('.gallery-link');
        if (!link) return;
        e.preventDefault();  // zamiast otwierać plik, pokazujemy go w oknie
        if (swiped) { swiped = false; return; }
        openTile = link.closest('.gallery-item');
        var many = openTile.querySelectorAll('.gallery-link').length > 1;
        navButtons.forEach(function (b) { b.hidden = !many; });  // strzałki tylko przy kilku zdjęciach
        show(currentSlide(openTile));
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
        if (navButtons[0].hidden) return;
        if (e.key === 'ArrowLeft') show(current - 1);
        if (e.key === 'ArrowRight') show(current + 1);
    });

    // Po zamknięciu czyścimy obrazek, żeby przy następnym otwarciu nie mignęło stare zdjęcie
    dialog.addEventListener('close', function () { img.removeAttribute('src'); });
})();
