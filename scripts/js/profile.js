document.addEventListener('DOMContentLoaded', function () {
    const passwordForm = document.querySelector('.password-form');
    const forgotPasswordForm = document.querySelector('.forgot-password-form');
    const changePasswordBtn = document.getElementById('change-password-btn');
    const forgotPasswordBtn = document.getElementById('forgot-password-btn');
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
    const masterForm = document.getElementById('master-form');
    const editMasterBtn = document.getElementById('edit-master-btn');
    const saveMasterBtn = document.getElementById('save-master-btn');
    const masterField = document.querySelector('.profile-field[data-field="master-info"]');

    // Начальное состояние: скрываем поля
    if (avatarUploadField) avatarUploadField.style.display = 'none';
    if (avatarField) avatarField.style.display = 'none';
    if (passwordForm) passwordForm.style.display = 'none';
    if (forgotPasswordForm) forgotPasswordForm.style.display = 'none';

    let isEditingProfile = false;
    let isEditingMaster = false;

    const resetForms = () => {
        if (passwordForm) passwordForm.style.display = 'none';
        if (forgotPasswordForm) forgotPasswordForm.style.display = 'none';
        if (changePasswordBtn) changePasswordBtn.textContent = 'Сменить пароль';
        if (forgotPasswordBtn) forgotPasswordBtn.textContent = 'Забыли пароль';
    };

    const resetProfileForm = () => {
        if (isEditingProfile) {
            profileFields.forEach(field => {
                const fieldValue = field.querySelector('.field-value');
                const editField = field.querySelector('.edit-field');
                const status = field.querySelector('.edit-status');

                if (fieldValue) fieldValue.style.display = 'inline';
                if (status) status.style.display = 'inline';
                editField.style.display = 'none';

                if (field.dataset.field === 'avatar') {
                    field.classList.remove('edit-mode');
                    field.style.display = 'none';
                    if (fileUploadText) fileUploadText.textContent = 'Выберите или перетащите изображение';
                    if (avatarInput) avatarInput.value = '';
                }
            });
            editProfileBtn.textContent = 'Редактировать профиль';
            saveProfileBtn.style.display = 'none';
            editProfileBtn.style.display = 'block';
            staticFields.style.order = '0';
            editableFields.style.order = '1';
            isEditingProfile = false;
            avatarUploadField.style.display = 'none';
        }
    };

    const resetMasterForm = () => {
        if (isEditingMaster && masterField) {
            const fieldValue = masterField.querySelector('.field-value');
            const editField = masterField.querySelector('.edit-field');
            if (fieldValue) fieldValue.style.display = 'inline';
            if (editField) editField.style.display = 'none';
            editMasterBtn.textContent = 'Редактировать мастера';
            saveMasterBtn.style.display = 'none';
            editMasterBtn.style.display = 'block';
            isEditingMaster = false;
        }
    };

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            resetForms();
            resetProfileForm();
            resetMasterForm();
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
        });
    });

    if (changePasswordBtn && passwordForm) {
        changePasswordBtn.addEventListener('click', function() {
            const isVisible = passwordForm.style.display === 'block';
            resetForms();
            passwordForm.style.display = isVisible ? 'none' : 'block';
            this.textContent = isVisible ? 'Сменить пароль' : 'Скрыть форму';
        });
    }

    if (forgotPasswordBtn && forgotPasswordForm) {
        forgotPasswordBtn.addEventListener('click', function() {
            const isVisible = forgotPasswordForm.style.display === 'block';
            resetForms();
            forgotPasswordForm.style.display = isVisible ? 'none' : 'block';
            this.textContent = isVisible ? 'Забыли пароль' : 'Скрыть форму';
        });
    }

    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', function() {
            if (!isEditingProfile) {
                profileFields.forEach(field => {
                    const fieldValue = field.querySelector('.field-value');
                    const editField = field.querySelector('.edit-field');
                    const status = field.querySelector('.edit-status');

                    if (fieldValue) fieldValue.style.display = 'none';
                    if (status) status.style.display = 'none';
                    editField.style.display = 'inline-block';

                    if (field.dataset.field === 'avatar') {
                        field.classList.add('edit-mode');
                        field.style.display = 'block';
                        avatarUploadField.style.display = 'inline-block';
                    }
                });
                this.textContent = 'Отменить редактирование';
                saveProfileBtn.style.display = 'block';
                staticFields.style.order = '-1';
                editableFields.style.order = '0';
                isEditingProfile = true;
            } else {
                resetProfileForm();
            }
        });
    }

    if (saveProfileBtn) {
        saveProfileBtn.addEventListener('click', () => profileForm.submit());
    }

    // Обработчики для мастера
    if (editMasterBtn) {
        editMasterBtn.addEventListener('click', function() {
            if (!isEditingMaster) {
                const fieldValue = masterField.querySelector('.field-value');
                const editField = masterField.querySelector('.edit-field');
                if (fieldValue) fieldValue.style.display = 'none';
                if (editField) editField.style.display = 'inline-block';
                this.textContent = 'Отменить редактирование';
                saveMasterBtn.style.display = 'block';
                isEditingMaster = true;
            } else {
                resetMasterForm();
            }
        });
    }

    if (saveMasterBtn) {
        saveMasterBtn.addEventListener('click', () => masterForm.submit());
    }

    // Drag-and-drop обработчики
    if (fileUploadArea) {
        fileUploadArea.addEventListener('click', () => isEditingProfile && avatarInput.click());
        fileUploadArea.addEventListener('dragover', e => {
            e.preventDefault();
            if (isEditingProfile) fileUploadArea.classList.add('dragging');
        });
        fileUploadArea.addEventListener('dragleave', e => {
            e.preventDefault();
            fileUploadArea.classList.remove('dragging');
        });
        fileUploadArea.addEventListener('drop', e => {
            e.preventDefault();
            fileUploadArea.classList.remove('dragging');
            if (isEditingProfile && e.dataTransfer.files[0]?.type.startsWith('image/')) {
                avatarInput.files = e.dataTransfer.files;
                fileUploadText.textContent = 'Файл загружен';
            }
        });
    }

    if (avatarInput) {
        avatarInput.addEventListener('change', () => {
            fileUploadText.textContent = avatarInput.files.length
                ? 'Файл загружен'
                : 'Выберите или перетащите изображение';
        });
    }

    // Инициализация
    resetProfileForm();
    resetMasterForm();
});
