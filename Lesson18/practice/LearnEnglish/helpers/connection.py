from pathlib import Path
import sqlite3


class Connect:
    """
    Класс для подключения к базе данных SQLite,
    поддерживающий использование с оператором 'with'.
    """

    def __init__(self, db_name: Path, foreign_key=True):
        """
        Инициализирует объект Connect.

        Args:
            db_name: Имя файла базы данных SQLite.
        """
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.foreign_key = foreign_key

    def __enter__(self) -> sqlite3.Cursor:
        """
        Метод, вызываемый при входе в контекстный менеджер 'with'.
        Устанавливает соединение с базой данных и создает курсор.

        Returns:
            sqlite3.Cursor: Объект курсора для выполнения SQL-запросов.
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            return self.cursor
        except sqlite3.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            # Возможно, стоит перебросить исключение или выполнить другую обработку ошибки
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Метод, вызываемый при выходе из контекстного менеджера 'with'.
        Закрывает соединение с базой данных.

        Args:
            exc_type: Тип исключения (если оно было).
            exc_val: Значение исключения.
            exc_tb: Объект трассировки исключения.
        """
        if self.conn:
            if exc_type is None:
                # Если исключений не было, сохраняем изменения
                self.conn.commit()
            else:
                # Если было исключение, откатываем изменения
                self.conn.rollback()
                print(f"Произошла ошибка: {exc_val}. Изменения откачены.")
            self.conn.close()
