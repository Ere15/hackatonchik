// script.js

// Получаем ссылку на форму входа
const loginForm = document.getElementById('login-form');

// Добавляем обработчик события на отправку формы
loginForm.addEventListener('submit', function(event) {
    // Предотвращаем стандартное поведение формы (перезагрузка страницы)
    event.preventDefault();

    //перед переходом должна быть проверка введеной почты и от нее зависит окно перехода в окно работника
    // Переходим на страницу работника компании
    window.location.href = 'employee.html';
});
