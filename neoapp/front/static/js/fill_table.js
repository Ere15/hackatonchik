document.addEventListener("DOMContentLoaded", function() {
    console.log('Скрипт был успешно выполнен!');
    // Отправляем GET-запрос на эндпоинт для получения данных
    fetch('/owner/requests/pending')
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при получении данных');
            }
            return response.json();
        })
        .then(data => {
            // Выводим данные в консоль
            console.log('Данные от сервера:', data);
            
            // Обновляем таблицу с данными
            updateTable(data);
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });

    function updateTable(data) {
        const tbody = document.querySelector('.requests-table tbody');
        tbody.innerHTML = ''; // Очищаем содержимое tbody

        // Проходим по данным и добавляем строки в таблицу
        data.forEach(request => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${request.id_запроса}</td>
                <td>${request.Дата_запроса}</td>
                <td>${request.Метки}</td>
                <td>${request.Статус}</td>
                <td>${request.Тема}</td>
            `;
            tbody.appendChild(row);
        });
    }
});
