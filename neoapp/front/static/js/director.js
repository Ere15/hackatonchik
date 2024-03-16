document.addEventListener("DOMContentLoaded", function() {
    var filterBtn = document.getElementById("filter-btn");
    var dropdownContent = document.querySelector(".dropdown-content");
    var searchBtn = document.getElementById("search-btn");
    var searchInput = document.getElementById("search");
    var notFoundMessage = document.getElementById("not-found");
    var reviewingBtn = document.getElementById("reviewing-btn");
    var reviewedBtn = document.getElementById("reviewed-btn");
    var makeRequestBtn = document.getElementById("make-request"); // Новая переменная для кнопки "Создать запрос"

    var currentFilterBtn = null; // Переменная для хранения текущей активной кнопки фильтрации

    // Показываем/скрываем выпадающее меню при клике на кнопку "Фильтр"
    filterBtn.addEventListener("click", function() {
        dropdownContent.classList.toggle("show");
    });

    // Обработчик для фильтрации по выбранным меткам
    var labels = document.querySelectorAll(".dropdown-content input[type='checkbox']");
    labels.forEach(function(label) {
        label.addEventListener("change", filterRows);
    });

    // Обработчик для поиска при нажатии на кнопку лупы
    searchBtn.addEventListener("click", filterRows);

    // Обработчик для поиска при вводе в поле поиска
    searchInput.addEventListener("input", filterRows);

    // Обработчик для кнопки "На рассмотрении"
    reviewingBtn.addEventListener("click", function() {
        toggleFilter(reviewingBtn);
    });

    // Обработчик для кнопки "Рассмотрено"
    reviewedBtn.addEventListener("click", function() {
        toggleFilter(reviewedBtn);
    });

    

    // Функция для добавления обработчиков клика на строки таблицы
    function addRowClickListeners() {
        var requestRows = document.querySelectorAll(".requests-table tbody tr");
        requestRows.forEach(function(row) {
            row.addEventListener("click", function() {
                // Получаем номер запроса из первой ячейки строки
                var requestId = row.cells[0].textContent;
                // Переходим на страницу деталей запроса с передачей номера запроса в параметрах запроса
                window.location.href = "direc_req.html?id=" + requestId;
            });
        });
    }

    // Вызываем функцию для добавления обработчиков клика на строки таблицы
    addRowClickListeners();

    function toggleFilter(btn) {
        if (btn === currentFilterBtn) {
            currentFilterBtn.classList.remove("active");
            currentFilterBtn = null;
        } else {
            if (currentFilterBtn) {
                currentFilterBtn.classList.remove("active");
            }
            currentFilterBtn = btn;
            currentFilterBtn.classList.add("active");
        }
        filterRows();
    }

    function filterRows() {
        var searchText = searchInput.value.toLowerCase();
        var statusFilter = null;

        // Проверяем, какая кнопка фильтрации активна
        if (currentFilterBtn === reviewingBtn) {
            statusFilter = ["в обработке", "новый"];
        } else if (currentFilterBtn === reviewedBtn) {
            statusFilter = ["одобрено", "отказано"];
        }

        var rows = document.querySelectorAll(".requests-table tbody tr");
        var found = false;

        rows.forEach(function(row) {
            var rowText = row.textContent.toLowerCase();
            var status = row.cells[3].textContent.toLowerCase(); // Получаем текст статуса из четвёртой ячейки
            var isMatch = rowText.includes(searchText); // Проверяем наличие текста в строке
            var statusMatch = !statusFilter || statusFilter.includes(status); // Проверяем соответствие статуса выбранному фильтру

            if (isMatch && statusMatch) {
                row.style.display = "";
                found = true;
            } else {
                row.style.display = "none";
            }
        });

        // Показываем или скрываем сообщение об отсутствии результатов
        if (found) {
            notFoundMessage.style.display = "none";
        } else {
            notFoundMessage.style.display = "block";
        }
    }
});
