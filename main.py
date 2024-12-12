import tkinter as tk
from database import Database
from parsing import Parser
from interface import ParserApp

def main():
    # Инициализация базы данных и парсера
    db = Database()
    parser = Parser(db.cursor, update_parsings_func=None)

    root = tk.Tk()
    app = ParserApp(root, parser)  # Передаем парсер в интерфейс
    root.mainloop()

if __name__ == "__main__":
    main()
