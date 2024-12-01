$(document).ready(function () {
    const API_BASE = "http://127.0.0.1:8000/api/";

    // Загрузка закладок с возможностью фильтрации, поиска и избранного
    function loadBookmarks(searchQuery = '', category = '', favoriteOnly = false) {
        let url = `${API_BASE}bookmarks/`;
        let params = new URLSearchParams();

        if (searchQuery) {
            params.append('searchQuery', searchQuery);
        }
        if (category) {
            params.append('category', category);
        }
        if (favoriteOnly) {
            params.append('favorite', 'true');
        }

        if (params.toString()) {
            url += '?' + params.toString();
        }

        $.ajax({
            url: url,
            method: 'GET',
            success: function (data) {
                $('#bookmarks-list').empty();
                const categories = {};

                // Группировка закладок по категориям
                data.forEach(function (bookmark) {
                    const categoryName = bookmark.category && bookmark.category.name ? bookmark.category.name : 'No category assigned';
                    if (!categories[categoryName]) {
                        categories[categoryName] = [];
                    }
                    categories[categoryName].push(bookmark);
                });

                // Отображение закладок по категориям
                for (const category in categories) {
                    $('#bookmarks-list').append(`<h3>${category}</h3>`);
                    categories[category].forEach(function (bookmark) {
                        $('#bookmarks-list').append(`
                        <div class="card mb-3" data-id="${bookmark.id}">
                            <div class="card-body">
                                <h2>${bookmark.title || 'No Title'}</h2>
                                <a href="${bookmark.url}" target="_blank">${bookmark.url}</a>
                                <p>Category: ${bookmark.category && bookmark.category.name ? bookmark.category.name : 'No Category'}</p>
                                <button class="view-btn btn btn-primary">View</button>
                                <button class="edit-btn btn btn-warning">Edit</button>
                                <button class="delete-btn btn btn-danger">Delete</button>
                                <button class="favorite-btn btn ${bookmark.favorite ? 'btn-success' : 'btn-outline-secondary'}">
                                    ${bookmark.favorite ? 'Unfavorite' : 'Favorite'}
                                </button>
                            </div>
                        </div>
                    `);
                    });
                }
            },
            error: function (error) {
                console.error('Error fetching bookmarks:', error);
            }
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        headers: { 'X-CSRFToken': csrftoken }
    });


    // Обработчик для поиска закладок
    $('#search-input').on('input', function () {
        const searchQuery = $(this).val();
        loadBookmarks(searchQuery, $('#category-filter').val(), $('#favorite-filter').is(':checked'));
    });

    // Загрузка списка категорий для фильтрации
    function loadCategories() {
        $.ajax({
            url: `${API_BASE}categories/`,
            method: 'GET',
            success: function (data) {
                $('#bookmark-category').html('<option value="">Select a Category</option>');
                $('#category-filter').html('<option value="">All Categories</option>');
                data.forEach(function (category) {
                    $('#bookmark-category').append(`<option value="${category.id}">${category.name}</option>`);
                    $('#category-filter').append(`<option value="${category.id}">${category.name}</option>`);
                });
            },
            error: function (error) {
                console.error('Error fetching categories:', error);
            }
        });
    }

    // Проверка корректности URL
    function isValidUrl(url) {
        const pattern = new RegExp('^(https?:\\/\\/)?' +
            '((([a-zA-Z0-9\\-]+\\.)+[a-zA-Z]{2,})|' +
            '((\\d{1,3}\\.){3}\\d{1,3}))' +
            '(\\:\\d+)?(\\/[-a-zA-Z0-9@:%._\\+~#=]*)*' +
            '(\\?[;&a-zA-Z0-9@:%_\\+.~#?&/=]*)?$', 'i');
        return !!pattern.test(url);
    }

    // Обработчик для добавления новой закладки
    $('#bookmark-form').on('submit', function (event) {
        event.preventDefault();

        const bookmarkUrl = $('#bookmark-url').val();
        const bookmarkTitle = $('#bookmark-title').val();
        const categoryId = $('#bookmark-category').val();

        if (!isValidUrl(bookmarkUrl)) {
            alert('Please enter a valid URL!');
            return;
        }

        const bookmarkData = {
            url: bookmarkUrl,
            title: bookmarkTitle,
            category_id: categoryId ? parseInt(categoryId) : null
        };

        $.ajax({
            url: `${API_BASE}bookmarks/`,
            method: 'POST',
            data: JSON.stringify(bookmarkData),
            contentType: 'application/json',
            success: function (response) {
                $('#bookmark-form')[0].reset();
                loadBookmarks();
            },
            error: function (error) {
                alert('Error: ' + error.responseText);
            }
        });
    });

    // Фильтрация закладок по категории и избранным
    $('#category-filter').on('change', function () {
        const selectedCategory = $(this).val();
        loadBookmarks('', selectedCategory, $('#favorite-filter').is(':checked'));
    });

    $('#favorite-filter').on('change', function () {
        loadBookmarks('', $('#category-filter').val(), $(this).is(':checked'));
    });

    // Функция для обновления избранного статуса
    function toggleFavorite(id, isFavorite) {
        $.ajax({
            url: `${API_BASE}bookmarks/${id}/`,
            method: 'PUT',
            data: JSON.stringify({ favorite: !isFavorite }),
            contentType: 'application/json',
            success: function () {
                loadBookmarks();
            },
            error: function (error) {
                console.error('Error updating favorite status:', error);
            }
        });
    }

    // Проверяем, если мы на странице деталей закладки
    if (window.location.pathname.endsWith('bookmark_detail.html')) {
        const params = new URLSearchParams(window.location.search);
        const bookmarkId = params.get('id');

        if (bookmarkId) {
            $.ajax({
                url: `${API_BASE}bookmarks/${bookmarkId}/`,
                method: 'GET',
                success: function (data) {
                    // Заполняем данные на странице
                    $('#title').text(data.title || 'No Title');
                    $('#url').text(data.url).attr('href', data.url);
                    $('#category').text(data.category?.name || 'No Category');
                    $('#favorite').text(data.favorite ? 'Yes' : 'No');
                },
                error: function (error) {
                    console.error('Error fetching bookmark:', error);
                    alert('Failed to load bookmark details.');
                }
            });
        } else {
            alert('Bookmark ID is missing in the URL.');
        }
    }

    // Функции для обновления и удаления закладок
    function updateBookmark(id, title, url, categoryId) {
        const bookmarkData = {
            url: url,
            title: title,
            category_id: categoryId ? parseInt(categoryId) : null
        };

        $.ajax({
            url: `${API_BASE}bookmarks/${id}/`,
            method: 'PUT',
            data: JSON.stringify(bookmarkData),
            contentType: 'application/json',
            success: function () {
                loadBookmarks();
            },
            error: function (error) {
                alert('Error updating bookmark: ' + error.responseText);
            }
        });
    }

    function deleteBookmark(id) {
        $.ajax({
            url: `${API_BASE}bookmarks/${id}/`,

            method: 'DELETE',
            success: function () {
                loadBookmarks();
            },
            error: function (error) {
                alert('Error deleting bookmark: ' + error.responseText);
            }
        });
    }

    // Делегирование событий для кнопок
    // $('#bookmarks-list').on('click', '.view-btn', function () {
    //     const bookmarkId = $(this).closest('.card').data('id');
    //     window.location.href = `/bookmarks/view/${bookmarkId}/`;
    // });

    $('#bookmarks-list').on('click', '.view-btn', function () {
        const bookmarkId = $(this).closest('.card').data('id');
        window.location.href = `/bookmark_detail.html?id=${bookmarkId}`;
    });

    $('#bookmarks-list').on('click', '.edit-btn', function () {
        const bookmarkId = $(this).closest('.card').data('id');
        const newTitle = prompt('Enter new title:');
        const newUrl = prompt('Enter new URL:');
        const newCategory = prompt('Enter new category ID:');
        if (newTitle && newUrl) {
            updateBookmark(bookmarkId, newTitle, newUrl, newCategory);
        }
    });

    $('#bookmarks-list').on('click', '.delete-btn', function () {
        const bookmarkId = $(this).closest('.card').data('id');
        if (confirm('Are you sure you want to delete this bookmark?')) {
            deleteBookmark(bookmarkId);
        }
    });

    $('#bookmarks-list').on('click', '.favorite-btn', function () {
        const bookmarkId = $(this).closest('.card').data('id');
        const isFavorite = $(this).hasClass('btn-success');
        toggleFavorite(bookmarkId, isFavorite);
    });

    // Инициализация загрузки категорий и закладок
    loadCategories();
    loadBookmarks();
});
