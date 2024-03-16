// Получаем ссылку на форму входа
const loginForm = document.getElementById('login-form');

// Добавляем обработчик события на отправку формы
loginForm.addEventListener('submit', function(event) {
    // Предотвращаем стандартное поведение формы (перезагрузка страницы)
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Отправляем запрос на аутентификацию
    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => {
        if (response.ok) {
            // Парсим ответ сервера в формат JSON
            return response.json();
        } else {
            throw new Error('Логин или пароль неверны');
        }
    })
    .then(data => {
        // Получаем токен доступа из ответа сервера
        const accessToken = data.access_token;
        // Сохраняем токен в localStorage
        //localStorage.setItem('accessToken', accessToken);
        // Переходим на страницу работника компании
        window.location.href = '/employee?token=' + accessToken;
    })
    .catch(error => {
        console.error('Ошибка при проверке логина:', error);
    });
});
