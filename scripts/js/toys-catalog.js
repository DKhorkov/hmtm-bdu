document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.filters-form');
    const minPriceInput = document.querySelector('input[name="min_price"]');
    const maxPriceInput = document.querySelector('input[name="max_price"]');
    const pageInput = document.getElementById('page-input');
    const goToPageBtn = document.getElementById('go-to-page-btn');
    const categorySearch = document.querySelector('.category-search');
    const tagSearch = document.querySelector('.tag-search');
    const categoryList = document.querySelector('.category-list');
    const tagList = document.querySelector('.tag-list');
    const filterToggleBtn = document.getElementById('filter-toggle-btn');
    const filtersSection = document.querySelector('.filters-section');
    const accordionToggles = document.querySelectorAll('.accordion-toggle');

    const urlParams = new URLSearchParams(window.location.search);
    const hasFilters = (urlParams.has('search') && urlParams.get('search').trim()) ||
                      (urlParams.has('quantity_floor') && urlParams.get('quantity_floor').trim()) ||
                      (urlParams.has('min_price') && urlParams.get('min_price').trim()) ||
                      (urlParams.has('max_price') && urlParams.get('max_price').trim()) ||
                      urlParams.has('categories') ||
                      urlParams.has('tags') ||
                      (urlParams.get('sort_order') && urlParams.get('sort_order') !== 'newest');

    if (!hasFilters) {
        form.reset();
    }

    form.addEventListener('submit', function(event) {
        // Удаляем пустые поля перед отправкой
        const inputs = form.querySelectorAll('input[name="min_price"], input[name="max_price"], input[name="quantity_floor"]');
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.name = ''; // Удаляем имя поля, чтобы оно не отправлялось
            }
        });

        const minPrice = parseFloat(minPriceInput.value);
        const maxPrice = parseFloat(maxPriceInput.value);

        if (minPrice && maxPrice && maxPrice < minPrice) {
            event.preventDefault();
            alert('Максимальная цена не может быть меньше минимальной!');
            maxPriceInput.focus();
        }
    });

    goToPageBtn.addEventListener('click', function() {
        const page = parseInt(pageInput.value);
        const totalPages = parseInt(pageInput.max);
        if (page && page >= 1 && page <= totalPages) {
            const currentParams = new URLSearchParams(window.location.search);
            currentParams.set('page', page);
            window.location.href = `?${currentParams.toString()}`;
        } else {
            alert(`Введите число от 1 до ${totalPages}!`);
            pageInput.focus();
        }
    });

    pageInput.addEventListener('focus', function() {
        this.value = '';
    });

    categorySearch.addEventListener('input', function() {
        const searchText = this.value.toLowerCase();
        const categoryItems = categoryList.querySelectorAll('.custom-checkbox');

        categoryItems.forEach(item => {
            const categoryName = item.querySelector('.checkbox-label').textContent.toLowerCase();
            if (categoryName.includes(searchText)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });

    tagSearch.addEventListener('input', function() {
        const searchText = this.value.toLowerCase();
        const tagItems = tagList.querySelectorAll('.custom-checkbox');

        tagItems.forEach(item => {
            const tagName = item.querySelector('.checkbox-label').textContent.toLowerCase();
            if (tagName.includes(searchText)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    });

    accordionToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetContainer = document.querySelector(`.${targetId}-container`);
            const isActive = this.classList.contains('active');

            accordionToggles.forEach(t => {
                if (t !== this) {
                    t.classList.remove('active');
                    const otherTargetId = t.getAttribute('data-target');
                    const otherTargetContainer = document.querySelector(`.${otherTargetId}-container`);
                    if (otherTargetContainer) {
                        otherTargetContainer.classList.remove('active');
                    }
                }
            });

            if (isActive) {
                this.classList.remove('active');
                targetContainer.classList.remove('active');
            } else {
                this.classList.add('active');
                targetContainer.classList.add('active');
            }
        });
    });

    filterToggleBtn.addEventListener('click', function() {
        filtersSection.classList.toggle('active');
        this.textContent = filtersSection.classList.contains('active') ? 'Скрыть фильтры' : 'Показать фильтры';
    });
});
