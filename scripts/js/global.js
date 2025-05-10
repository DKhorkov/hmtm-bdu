document.addEventListener('DOMContentLoaded', () => {
    const errorPopup = document.querySelector('.error-popup');
    const closeBtn = document.querySelector('.close-btn');
    const ERROR_POPUP_TIMEOUT= 5000;
    const FADE_EFFECT_TIMEOUT = 50;

    const fadeOut = (element) => {
        element.style.opacity = 1;
        const fadeEffect = setInterval(() => {
            if (element.style.opacity > 0) {
                element.style.opacity -= 0.1;
            } else {
                clearInterval(fadeEffect);
                element.remove();
            }
        }, FADE_EFFECT_TIMEOUT);
    };

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            fadeOut(errorPopup);
        });
    }

    if (errorPopup) {
        setTimeout(() => {
            fadeOut(errorPopup);
        }, ERROR_POPUP_TIMEOUT);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const messagePopup = document.querySelector('.message-popup');
    const closeBtn = document.querySelector('.close-btn');

    const fadeOut = (element) => {
        element.style.opacity = 1;
        const fadeEffect = setInterval(() => {
            if (element.style.opacity > 0) {
                element.style.opacity -= 0.1;
            } else {
                clearInterval(fadeEffect);
                element.remove();
            }
        }, 50);
    };

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            fadeOut(messagePopup);
        });
    }

    if (messagePopup) {
        setTimeout(() => {
            fadeOut(messagePopup);
        }, 5000);
    }
});

// Burger-Menu
const burger = document.querySelector('.burger');
const sidebar = document.querySelector('.sidebar-menu');
const overlay = document.querySelector('.overlay');

// Открытие/закрытие меню через бургер
burger.addEventListener('click', () => {
  burger.classList.toggle('active');
  sidebar.classList.toggle('active');
  overlay.classList.toggle('active');
});

// Закрытие через клик на оверлей
overlay.addEventListener('click', () => {
  burger.classList.remove('active');
  sidebar.classList.remove('active');
  overlay.classList.remove('active');
});

// Закрытие меню при клике на иконку мишки
document.querySelector('.nav-icon').addEventListener('click', (e) => {
  if (sidebar.classList.contains('active')) {
    e.preventDefault();
    burger.classList.remove('active');
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
  }
});
