document.addEventListener('DOMContentLoaded', function () {
    const passwordForm = document.querySelector('.password-form');
    const changePasswordBtn = document.getElementById('change-password-btn');
    const profileForm = document.getElementById('profile-form');
    const editProfileBtn = document.getElementById('edit-profile-btn');
    const saveProfileBtn = document.getElementById('save-profile-btn');
    const profileFields = document.querySelectorAll('.profile-field');
    const staticFields = document.querySelector('.static-fields');
    const editableFields = document.querySelector('.editable-fields');
    const avatarUploadField = document.getElementById('avatar-upload-field');
    const avatarField = document.querySelector('.profile-field[data-field="avatar"]');
    const fileUploadArea = document.querySelector('.file-upload');
    const fileUploadText = document.querySelector('.file-upload-text');
    const avatarInput = document.querySelector('input[name="avatar"]');

    // Начальное состояние: скрываем поле "Аватар" при загрузке страницы + поле для загрузки файла
    if (avatarUploadField) {
        avatarUploadField.style.display = 'none';
    }

    if (avatarField) {
        avatarField.style.display = 'none';
    }

    let isEditing = false;

    const resetPasswordForm = () => {
        passwordForm.style.display = 'none';
        changePasswordBtn.textContent = 'Сменить пароль';
        passwordForm.querySelector('form').reset();
    };

    const resetEditForm = () => {
        if (isEditing) {
            profileFields.forEach(field => {
                const fieldValue = field.querySelector('.field-value');
                const editField = field.querySelector('.edit-field');
                const status = field.querySelector('.edit-status');

                if (fieldValue) fieldValue.style.display = 'inline';
                if (status) status.style.display = 'inline';

                editField.style.display = 'none';
                if (field.dataset.field === 'avatar') {
                    if (fileUploadText) fileUploadText.textContent = 'Выберите или перетащите изображение';
                    if (avatarInput) avatarInput.value = '';

                    field.classList.remove('edit-mode'); // Убираем метку
                    field.style.display = 'none';
                }
            });
            editProfileBtn.textContent = 'Редактировать профиль';
            saveProfileBtn.style.display = 'none';
            editProfileBtn.style.display = 'block';
            // Возвращаем порядок полей
            staticFields.style.order = '0';
            editableFields.style.order = '1';
            isEditing = false;

            avatarUploadField.style.display = 'none'
        }
    };

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            resetPasswordForm();
            if (btn.dataset.tab !== 'main' && isEditing) {
                resetEditForm();
            }
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
        });
    });

    changePasswordBtn.addEventListener('click', function () {
        const isVisible = passwordForm.style.display === 'block';
        passwordForm.style.display = isVisible ? 'none' : 'block';
        this.textContent = isVisible ? 'Сменить пароль' : 'Скрыть форму';
    });

    editProfileBtn.addEventListener('click', function () {
        if (!isEditing) {
            // Включаем режим редактирования
            profileFields.forEach(field => {
                const fieldValue = field.querySelector('.field-value');
                const editField = field.querySelector('.edit-field');
                const status = field.querySelector('.edit-status');

                if (fieldValue) fieldValue.style.display = 'none';
                if (status) status.style.display = 'none';

                editField.style.display = 'inline-block';
                if (field.dataset.field === 'avatar') {
                    field.classList.add('edit-mode'); // Добавляем метку
                    field.style.display = 'block';
                }
            });
            this.textContent = 'Отменить редактирование';
            saveProfileBtn.style.display = 'block';
            this.style.display = 'block';
            // Перемещаем неизменяемые поля наверх
            staticFields.style.order = '-1';
            editableFields.style.order = '0';
            isEditing = true;

            avatarUploadField.style.display = 'inline-block'
        } else {
            // Отменяем редактирование
            resetEditForm();
        }
    });

    // Открытие файлового менеджера при клике на область загрузки
    fileUploadArea?.addEventListener('click', () => {
        if (isEditing) {
            avatarInput.click();
        }
    });

    // Обработка событий drag-and-drop
    fileUploadArea?.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (isEditing) {
            fileUploadArea.classList.add('dragging');
        }
    });

    fileUploadArea?.addEventListener('dragleave', (e) => {
        e.preventDefault();
        fileUploadArea.classList.remove('dragging');
    });

    fileUploadArea?.addEventListener('drop', (e) => {
        e.preventDefault();
        fileUploadArea.classList.remove('dragging');
        if (isEditing) {
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type.startsWith('image/')) {
                avatarInput.files = files;
                fileUploadText.textContent = 'Файл загружен';
            }
        }
    });

    // Обновление текста при выборе файла через файловый менеджер
    avatarInput?.addEventListener('change', () => {
        if (avatarInput.files.length > 0) {
            fileUploadText.textContent = 'Файл загружен';
        } else {
            fileUploadText.textContent = 'Выберите или перетащите изображение';
        }
    });

    saveProfileBtn.addEventListener('click', function () {
        profileForm.submit();
    });

    // Применяем начальное состояние формы
    resetEditForm();
});
