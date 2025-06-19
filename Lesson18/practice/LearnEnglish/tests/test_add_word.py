import pytest
import sqlite3
from database import init_db, add_word


@pytest.fixture
def in_memory_db():
    """
    Фикстура Pytest, которая создает и инициализирует
    соединение с базой данных SQLite в памяти,
    и возвращает соединение и курсор.
    Гарантирует, что таблица 'words' существует и соединение
    корректно закрывается после теста.
    """
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    init_db(cursor)
    try:
        yield conn, cursor
    finally:
        if conn:
            conn.close()


def test_init_db_creates_table(in_memory_db):
    """
    Тест: Проверка, что init_db создает таблицу 'words'.
    """
    _, cursor = in_memory_db
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='words';")
    assert cursor.fetchone() is not None, "Таблица 'words' не создана"


def test_add_word_success(in_memory_db):
    """
    Тест: Успешное добавление нового слова в БД.
    """
    conn, cursor = in_memory_db
    cursor.execute("SELECT COUNT(*) FROM words")
    initial_count = cursor.fetchone()[0]

    english = "apple"
    russian = "яблоко"
    add_word(cursor, english, russian)
    conn.commit()

    cursor.execute("SELECT russian_translation FROM words WHERE english_word = ?", (english,))
    retrieved_translation = cursor.fetchone()
    assert retrieved_translation is not None and retrieved_translation[0] == russian, \
        f"Перевод для '{english}' не соответствует ожидаемому '{russian}'"

    cursor.execute("SELECT COUNT(*) FROM words")
    assert cursor.fetchone()[0] == initial_count + 1, "Количество слов не увеличилось"


def test_add_word_duplicate_entry_raises_error(in_memory_db):
    """
    Тест: Попытка добавить дубликат слова должна вызвать ValueError.
    Предполагается, что add_word явно проверяет дубликаты и выбрасывает ValueError.
    """
    conn, cursor = in_memory_db
    english = "banana"
    russian = "банан"
    add_word(cursor, english, russian)
    conn.commit()

    with pytest.raises(ValueError):
        add_word(cursor, english, "фрукт")

    cursor.execute("SELECT COUNT(*) FROM words")
    assert cursor.fetchone()[0] == 1, "Добавилась лишняя запись"


def test_add_word_empty_english_word_raises_error(in_memory_db):
    """
    Тест: Добавление слова с пустым английским словом должно вызвать ValueError.
    """
    conn, cursor = in_memory_db
    with pytest.raises(ValueError):
        add_word(cursor, "", "пустой")

    cursor.execute("SELECT * FROM words")
    assert cursor.fetchall() == [], "Таблица не осталась пустой"


def test_add_word_empty_russian_translation_raises_error(in_memory_db):
    """
    Тест: Добавление слова с пустым русским переводом должно вызвать ValueError.
    """
    conn, cursor = in_memory_db
    with pytest.raises(ValueError):
        add_word(cursor, "empty", "")

    cursor.execute("SELECT * FROM words")
    assert cursor.fetchall() == [], "Таблица не осталась пустой"