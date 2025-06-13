from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# HTML шаблоны
BASE_HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Библиотечный учет - {title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; color: #333; }}
        header {{ background: #35424a; color: #ffffff; padding: 20px 0; text-align: center; }}
        header h1 {{ margin: 0; }}
        nav a {{ color: #ffffff; text-decoration: none; margin: 0 10px; }}
        main {{ padding: 20px; max-width: 1200px; margin: 0 auto; padding-bottom: 60px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        table, th, td {{ border: 1px solid #ddd; }}
        th, td {{ padding: 12px; text-align: left; }}
        th {{ background-color: #f4f4f4; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        form div {{ margin-bottom: 15px; }}
        label {{ display: inline-block; width: 100px; }}
        input, select {{ padding: 8px; width: 200px; }}
        button {{ padding: 10px 15px; background: #35424a; color: #fff; border: none; cursor: pointer; }}
        button:hover {{ background: #3e4e58; }}
        footer {{ text-align: center; padding: 20px; background: #35424a; color: #ffffff; position: fixed; bottom: 0; width: 100%; }}
        .actions a {{ margin-right: 10px; }}
    </style>
</head>
<body>
    <header>
        <h1>Библиотечный учет</h1>
        <nav>
            <a href="/">Главная</a>
            <a href="/add">Добавить книгу</a>
            <a href="/search">Поиск</a>
        </nav>
    </header>
    <main>
        {content}
    </main>
    <footer>
        <p>Библиотечная система &copy; 2023</p>
    </footer>
</body>
</html>
'''

INDEX_HTML = '''
<h2>Список всех книг</h2>
<table>
    <thead>
        <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Автор</th>
            <th>Жанр</th>
            <th>Номер</th>
            <th>Действия</th>
        </tr>
    </thead>
    <tbody>
        {books_rows}
    </tbody>
</table>
'''

ADD_BOOK_HTML = '''
<h2>Добавить новую книгу</h2>
<form method="POST">
    <div>
        <label for="title">Название:</label>
        <input type="text" id="title" name="title" required>
    </div>
    <div>
        <label for="author">Автор:</label>
        <input type="text" id="author" name="author" required>
    </div>
    <div>
        <label for="genre">Жанр:</label>
        <input type="text" id="genre" name="genre" required>
    </div>
    <div>
        <label for="number">Номер:</label>
        <input type="text" id="number" name="number" required>
    </div>
    <button type="submit">Добавить</button>
</form>
'''

EDIT_BOOK_HTML = '''
<h2>Редактировать книгу</h2>
<form method="POST">
    <div>
        <label for="title">Название:</label>
        <input type="text" id="title" name="title" value="{book_title}" required>
    </div>
    <div>
        <label for="author">Автор:</label>
        <input type="text" id="author" name="author" value="{book_author}" required>
    </div>
    <div>
        <label for="genre">Жанр:</label>
        <input type="text" id="genre" name="genre" value="{book_genre}" required>
    </div>
    <div>
        <label for="number">Номер:</label>
        <input type="text" id="number" name="number" value="{book_number}" required>
    </div>
    <button type="submit">Сохранить</button>
</form>
'''

SEARCH_HTML = '''
<h2>Поиск книг</h2>
<form method="POST">
    <div>
        <label for="search_term">Поиск:</label>
        <input type="text" id="search_term" name="search_term" value="{search_term}">
    </div>
    <div>
        <label for="search_by">Искать по:</label>
        <select id="search_by" name="search_by">
            <option value="title">Названию</option>
            <option value="author">Автору</option>
            <option value="genre">Жанру</option>
            <option value="number">Номеру</option>
        </select>
    </div>
    <button type="submit">Найти</button>
</form>

{search_results}
'''


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            number TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Главная страница - список всех книг
@app.route('/')
def index():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM books')
    books = cursor.fetchall()
    conn.close()

    books_rows = ''
    for book in books:
        books_rows += f'''
        <tr>
            <td>{book[0]}</td>
            <td>{book[1]}</td>
            <td>{book[2]}</td>
            <td>{book[3]}</td>
            <td>{book[4]}</td>
            <td class="actions">
                <a href="/edit/{book[0]}">Редактировать</a>
                <a href="/delete/{book[0]}" onclick="return confirm('Вы уверены?')">Удалить</a>
            </td>
        </tr>
        '''

    content = INDEX_HTML.format(books_rows=books_rows)
    return BASE_HTML.format(title='Все книги', content=content)


# Добавление новой книги
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        number = request.form['number']

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO books (title, author, genre, number) VALUES (?, ?, ?, ?)',
                       (title, author, genre, number))
        conn.commit()
        conn.close()
        return redirect('/')

    return BASE_HTML.format(title='Добавить книгу', content=ADD_BOOK_HTML)


# Редактирование книги
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        number = request.form['number']

        cursor.execute('''
            UPDATE books 
            SET title=?, author=?, genre=?, number=?
            WHERE id=?
        ''', (title, author, genre, number, book_id))
        conn.commit()
        conn.close()
        return redirect('/')

    cursor.execute('SELECT * FROM books WHERE id=?', (book_id,))
    book = cursor.fetchone()
    conn.close()

    content = EDIT_BOOK_HTML.format(
        book_title=book[1],
        book_author=book[2],
        book_genre=book[3],
        book_number=book[4]
    )
    return BASE_HTML.format(title='Редактировать книгу', content=content)


# Удаление книги
@app.route('/delete/<int:book_id>')
def delete_book(book_id):
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM books WHERE id=?', (book_id,))
    conn.commit()
    conn.close()
    return redirect('/')


# Поиск книг
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search_term']
        search_by = request.form['search_by']

        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()

        if search_by == 'title':
            cursor.execute('SELECT * FROM books WHERE title LIKE ?', ('%' + search_term + '%',))
        elif search_by == 'author':
            cursor.execute('SELECT * FROM books WHERE author LIKE ?', ('%' + search_term + '%',))
        elif search_by == 'genre':
            cursor.execute('SELECT * FROM books WHERE genre LIKE ?', ('%' + search_term + '%',))
        elif search_by == 'number':
            cursor.execute('SELECT * FROM books WHERE number LIKE ?', ('%' + search_term + '%',))

        results = cursor.fetchall()
        conn.close()

        search_results = ''
        if results:
            search_results = '<h3>Результаты поиска:</h3><table><thead><tr><th>ID</th><th>Название</th><th>Автор</th><th>Жанр</th><th>Номер</th><th>Действия</th></tr></thead><tbody>'
            for book in results:
                search_results += f'''
                <tr>
                    <td>{book[0]}</td>
                    <td>{book[1]}</td>
                    <td>{book[2]}</td>
                    <td>{book[3]}</td>
                    <td>{book[4]}</td>
                    <td class="actions">
                        <a href="/edit/{book[0]}">Редактировать</a>
                        <a href="/delete/{book[0]}" onclick="return confirm('Вы уверены?')">Удалить</a>
                    </td>
                </tr>
                '''
            search_results += '</tbody></table>'

        content = SEARCH_HTML.format(
            search_term=search_term,
            search_results=search_results
        )
        return BASE_HTML.format(title='Поиск книг', content=content)

    return BASE_HTML.format(
        title='Поиск книг',
        content=SEARCH_HTML.format(search_term='', search_results='')
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True)