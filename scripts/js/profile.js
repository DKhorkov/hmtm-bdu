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

    // Начальное состояние: скрываем поле "Аватар" при загрузке страницы + поле для загрузке файла
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
                if (fieldValue) fieldValue.style.display = 'inline';
                editField.style.display = 'none';
                if (field.dataset.field === 'avatar') {
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
                if (fieldValue) fieldValue.style.display = 'none';
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

    saveProfileBtn.addEventListener('click', function () {
        profileForm.submit();
    });

    // Применяем начальное состояние формы
    resetEditForm();
});
