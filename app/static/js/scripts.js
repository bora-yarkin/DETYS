document.addEventListener('DOMContentLoaded', () => {
    // Navbar Indicator Yönetimi
    const nav = document.querySelector('.navigation');
    const list = document.querySelectorAll('.navigation ul li');
    const indicator = document.querySelector('.navigation .indicator');

    function moveIndicator(element) {
        const navRect = nav.getBoundingClientRect();
        const itemRect = element.getBoundingClientRect();
        const leftPosition = itemRect.left - navRect.left;
        const itemWidth = itemRect.width;

        // Indicator pozisyonunu ve genişliğini güncelle
        indicator.style.left = `${leftPosition}px`;
        indicator.style.width = `${itemWidth}px`;
    }

    list.forEach((item) => {
        item.addEventListener('click', (event) => {
            // Tüm liste elemanlarından 'active' sınıfını kaldır
            list.forEach(li => li.classList.remove('active'));

            // Tıklanan elemana 'active' sınıfını ekle
            item.classList.add('active');

            // Indicator'ü güncelle
            moveIndicator(item);
        });
    });

    // Sayfa yüklendiğinde aktif olan öğeyi veya varsayılan olarak ilk öğeyi belirle
    const activeItem = document.querySelector('.navigation ul li.active');
    if (activeItem) {
        moveIndicator(activeItem);
    } else if (list.length > 0) {
        // Hiç aktif öğe yoksa, ilk öğeyi varsayılan olarak kullan
        moveIndicator(list[0]);
    }

    // Form Geçiş Yönetimi
    const signUpButton = document.getElementById('signUp');
    const signInButton = document.getElementById('signIn');
    const container = document.getElementById('container');

    if (signUpButton && signInButton && container) {
        signUpButton.addEventListener('click', () => {
            container.classList.add('active');
        });

        signInButton.addEventListener('click', () => {
            container.classList.remove('active');
        });
    }

    // Dark Mode Toggle
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const currentTheme = localStorage.getItem('theme') || 'light';

    if (currentTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
    }

    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        let theme = 'light';
        if (document.body.classList.contains('dark-theme')) {
            theme = 'dark';
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        } else {
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        }
        localStorage.setItem('theme', theme);
    });
});