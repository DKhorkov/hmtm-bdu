document.addEventListener('DOMContentLoaded', () => {
    const errorPopup = document.querySelector('.error-popup');
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
            fadeOut(errorPopup);
        });
    }

    if (errorPopup) {
        setTimeout(() => {
            fadeOut(errorPopup);
        }, 5000);
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
