// Add smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        // Only prevent default if it's strictly a hash link on the current page
        const href = this.getAttribute('href');
        if (href.startsWith('#')) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        }
    });
});

// Navbar background on scroll
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(15, 23, 42, 0.95)';
            navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(15, 23, 42, 0.8)';
            navbar.style.boxShadow = 'none';
        }
    }
});

// Active nav links on scroll
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.nav-links a');

    let current = '';

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (pageYOffset >= (sectionTop - sectionHeight / 3)) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// Home Page Detect Location
const homeDetectBtn = document.getElementById('home-detect-btn');
if (homeDetectBtn) {
    homeDetectBtn.addEventListener('click', () => {
        if ("geolocation" in navigator) {
            const originalText = homeDetectBtn.innerHTML;
            homeDetectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Locating...';
            homeDetectBtn.disabled = true;

            navigator.geolocation.getCurrentPosition(async (position) => {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                try {
                    const res = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
                    const data = await res.json();
                    const city = data.city || data.locality || data.principalSubdivision || 'Unknown';

                    if (city !== 'Unknown') {
                        document.getElementById('home-city-input').value = city;
                    } else {
                        alert("Could not determine your exact city name.");
                    }
                } catch (e) {
                    alert("Location service unavailable.");
                } finally {
                    homeDetectBtn.innerHTML = originalText;
                    homeDetectBtn.disabled = false;
                }
            }, () => {
                alert("Location access denied.");
                homeDetectBtn.innerHTML = originalText;
                homeDetectBtn.disabled = false;
            });
        } else {
            alert("Geolocation is not supported by your browser.");
        }
    });
}

