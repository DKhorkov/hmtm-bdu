document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Удаляем активный класс у всех вкладок и контента
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Активируем выбранную вкладку и контент
            const targetTab = tab.dataset.tab;
            tab.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
});
