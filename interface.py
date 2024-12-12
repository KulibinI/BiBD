import tkinter as tk
from tkinter import ttk, messagebox
from parsing import Parser
from database import Database
import asyncio
import pyperclip
from tkinter import Scrollbar

class Tooltip:
    """Класс для создания всплывающей подсказки"""
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.text = None

    def show(self, text, x, y):
        """Показать всплывающее окно"""
        if self.tipwindow or not text:
            return
        self.tipwindow = tk.Toplevel(self.widget)
        self.tipwindow.wm_overrideredirect(True)
        self.tipwindow.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tipwindow, text=text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide(self):
        """Скрыть всплывающее окно"""
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

class ParserApp:
    def __init__(self, root, parser):
        self.root = root
        self.parser = parser
        self.db = Database()
        self.create_interface()
        self.parser = Parser(self.db.cursor, self.update_parsings_treeview)
        self.tooltip = Tooltip(self.root)

    def create_interface(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.input_label = ttk.Label(self.input_frame, text="Введите данные:")
        self.input_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.input_entry = ttk.Entry(self.input_frame, width=50)
        self.input_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.input_entry.bind("<Return>", self.start_parsing)  # Запуск парсинга по нажатию Enter

        self.parsings_frame = ttk.Frame(self.root)
        self.parsings_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.parsings_frame.columnconfigure(0, weight=1)
        self.parsings_frame.rowconfigure(0, weight=1)

        self.names_frame = ttk.Frame(self.root)
        self.names_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.names_frame.columnconfigure(0, weight=1)
        self.names_frame.rowconfigure(0, weight=1)

        self.names_treeview = ttk.Treeview(self.names_frame, columns=("ParsingID", "ID", "Name", "Date", "Archive", "Fond", "Inventory", "Cases", "Page", "URL", "Viewed", "Favourites"), show="headings")
        self.names_treeview.heading("ParsingID", text="№ отбора", command=lambda: self.sort_column(self.names_treeview, "ParsingID"))
        self.names_treeview.heading("ID", text="№ п.", command=lambda: self.sort_column(self.names_treeview, "ID"))
        self.names_treeview.heading("Name", text="Наименование", command=lambda: self.sort_column(self.names_treeview, "Name"))
        self.names_treeview.heading("Date", text="Дата", command=lambda: self.sort_column(self.names_treeview, "Date"))
        self.names_treeview.heading("Archive", text="Архив", command=lambda: self.sort_column(self.names_treeview, "Archive"))
        self.names_treeview.heading("Fond", text="Фонд", command=lambda: self.sort_column(self.names_treeview, "Fond"))
        self.names_treeview.heading("Inventory", text="Опись", command=lambda: self.sort_column(self.names_treeview, "Inventory"))
        self.names_treeview.heading("Cases", text="Дело", command=lambda: self.sort_column(self.names_treeview, "Cases"))
        self.names_treeview.heading("Page", text="Страница", command=lambda: self.sort_column(self.names_treeview, "Page"))
        self.names_treeview.heading("URL", text="Ссылка", command=lambda: self.sort_column(self.names_treeview, "URL"))
        self.names_treeview.heading("Viewed", text="Просм.", command=lambda: self.sort_column(self.names_treeview, "Viewed"))
        self.names_treeview.heading("Favourites", text="Избр.", command=lambda: self.sort_column(self.names_treeview, "Favourites"))
        self.names_treeview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.names_scrollbar = tk.Scrollbar(self.names_frame, orient="vertical", command=self.names_treeview.yview)
        self.names_scrollbar.grid(row=0, column=1, sticky="ns")
        self.names_treeview.configure(yscrollcommand=self.names_scrollbar.set)

        self.parsings_treeview = ttk.Treeview(self.parsings_frame, columns=("ParsingID", "Date", "Request", "Volume"), show="headings")
        self.parsings_treeview.heading("ParsingID", text="№ отбора", command=lambda: self.sort_column(self.parsings_treeview, "ParsingID"))
        self.parsings_treeview.heading("Date", text="Дата", command=lambda: self.sort_column(self.parsings_treeview, "Date"))
        self.parsings_treeview.heading("Request", text="Запрос", command=lambda: self.sort_column(self.parsings_treeview, "Request"))
        self.parsings_treeview.heading("Volume", text="Число результатов", command=lambda: self.sort_column(self.parsings_treeview, "Volume"))
        
        self.parsings_treeview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.parsings_scrollbar = tk.Scrollbar(self.parsings_frame, orient="vertical", command=self.parsings_treeview.yview)
        self.parsings_scrollbar.grid(row=0, column=1, sticky="ns")
        self.parsings_treeview.configure(yscrollcommand=self.parsings_scrollbar.set)
    
        self.names_treeview.column("ParsingID", width=50)
        self.names_treeview.column("ID", width=50)
        self.names_treeview.column("Name", width=200)
        self.names_treeview.column("Date", width=50)
        self.names_treeview.column("Archive", width=50)
        self.names_treeview.column("Fond", width=50)
        self.names_treeview.column("Inventory", width=50)
        self.names_treeview.column("Cases", width=50)
        self.names_treeview.column("Page", width=50)
        self.names_treeview.column("URL", width=100)
        self.names_treeview.column("Viewed", width=40)
        self.names_treeview.column("Favourites", width=40)

        self.parsings_treeview.column("ParsingID", width=10)
        self.parsings_treeview.column("Date", width=40)
        self.parsings_treeview.column("Volume", width=40)
        self.parsings_treeview.column("Request", width=70)

        self.start_button = tk.Button(self.root, text="Синхронный парсинг", command=self.start_parsing)
        self.start_button.grid(row=2, column=0, padx=(50, 0), pady=10, sticky="w")

        self.async_button = tk.Button(self.root, text="Асинхронный парсинг", command=lambda: self.run_async(self.start_async_parsing))
        self.async_button.grid(row=2, column=0, padx=(325, 0), pady=10, sticky="w")

        self.clear_button = tk.Button(self.root, text="Очистить базу данных", command=self.clear_database)
        self.clear_button.grid(row=2, column=0, padx=(600, 0), pady=10, sticky="w")

        self.delete_button = tk.Button(self.root, text="Удалить отбор", command=self.delete_parsing)
        self.delete_button.grid(row=2, column=0, padx=(775, 0), pady=10, sticky="w")

        self.update_parsings_treeview()
        self.names_treeview.bind("<Double-1>", self.copy_to_clipboard)
        self.parsings_treeview.bind("<ButtonRelease-1>", self.update_names_treeview)
        self.names_treeview.bind("<Button-1>", self.toggle_checkbox)

        self.names_treeview.bind("<Motion>", self.show_tooltip)
        self.names_treeview.bind("<Leave>", lambda e: self.tooltip.hide())

    def toggle_checkbox(self, event):
        """Переключение значения чекбокса в столбцах Просм. и Избр."""
        # Определяем, на какой ячейке был клик
        region = self.names_treeview.identify_region(event.x, event.y)
        if region != "cell":
            return

        column = self.names_treeview.identify_column(event.x)
        if column not in ("#11", "#12"):  # Проверяем, что клик был на колонке "Просм." или "Избр."
            return

        item_id = self.names_treeview.identify_row(event.y)
        if not item_id:
            return

        current_values = self.names_treeview.item(item_id)["values"]

        # Определяем индекс столбца и текущее состояние
        column_index = 10 if column == "#11" else 11  # Столбец "Просм." = 10, "Избр." = 11
        current_state = 1 if current_values[column_index] == "✔" else 0
        new_state = 0 if current_state == 1 else 1

        # Обновляем отображаемый текст
        new_text = "✔" if new_state == 1 else ""

        # Обновляем данные в Treeview
        current_values = list(current_values)
        current_values[column_index] = new_text
        self.names_treeview.item(item_id, values=current_values)

        # Обновляем базу данных
        column_name = "Viewed" if column == "#11" else "Favourites"
        self.db.cursor.execute(
            f"UPDATE Names SET {column_name} = ? WHERE ParsingID = ? AND Name = ?",
            (new_state, current_values[0], current_values[2]),  # ParsingID и Name используются как ключи
        )
        self.db.con.commit()


    def start_parsing(self, event=None):
        """Обработчик для начала парсинга"""
        query = self.input_entry.get() 
        if query:
            self.parser.start_parsing(query)
        else:
            messagebox.showwarning("Ошибка", "Введите запрос для парсинга.")

    def process_input(self):
        """Обработчик для текстового поля."""
        input_text = self.input_entry.get()
        if input_text:
            messagebox.showinfo("Ввод данных", f"Вы ввели: {input_text}")
        else:
            messagebox.showwarning("Ошибка ввода", "Пожалуйста, введите данные!")

    def copy_to_clipboard(self, event):
        item = self.names_treeview.selection()
        if not item:
            return

        column = self.names_treeview.identify_column(event.x)
        column_index = int(column.replace('#', '')) - 1 
        item_values = self.names_treeview.item(item)["values"]
        value_to_copy = item_values[column_index]

        pyperclip.copy(value_to_copy)

        print(f"Скопировано: {value_to_copy}")

    def sort_column(self, treeview, col):
        """ Сортировка столбца """
        data = [(treeview.item(item)["values"], item) for item in treeview.get_children()]
        reverse = False
        
        if col == "ParsingID":
            data.sort(key=lambda x: int(x[0][0]), reverse=reverse)
        elif col == "Date":
            data.sort(key=lambda x: x[0][1], reverse=reverse)
        elif col == "Volume":
            data.sort(key=lambda x: int(x[0][2]), reverse=reverse)
        elif col == "Name":
            data.sort(key=lambda x: x[0][1].lower(), reverse=reverse)

        for item in treeview.get_children():
            treeview.delete(item)
        
        for values, item in data:
            treeview.insert("", tk.END, iid=item, values=values)

    def update_parsings_treeview(self):
        self.db.cursor.execute("SELECT ParsingID, Date, Request, Volume FROM Parsings")
        parsings = self.db.cursor.fetchall()

        self.parsings_treeview.delete(*self.parsings_treeview.get_children())
        for parsing in parsings:
            self.parsings_treeview.insert("", tk.END, values=parsing)


    def update_names_treeview(self, event=None):
        """Обновление списка элементов для выбранного парсинга."""
        selected_item = self.parsings_treeview.selection()
        if not selected_item:
            return
        parsing_id = self.parsings_treeview.item(selected_item)["values"][0]

        self.db.cursor.execute("SELECT ParsingID, ID, Name, Date, Archive, Fond, Inventory, Cases, Page, URL, Viewed, Favourites FROM Names WHERE ParsingID = ?", (parsing_id,))
        names = self.db.cursor.fetchall()

        self.names_treeview.delete(*self.names_treeview.get_children())

        for name in names:
            viewed_text = "✔" if name[10] == 1 else ""
            favourites_text = "✔" if name[11] == 1 else ""

            self.names_treeview.insert(
                "",
                tk.END,
                values=(
                    name[0], name[1], name[2], name[3], name[4], name[5], name[6],
                    name[7], name[8], name[9], viewed_text, favourites_text
                )
            )

    def draw_checkboxes(self):
        """Отрисовка чекбоксов в Treeview."""
        for item in self.names_treeview.get_children():
            values = self.names_treeview.item(item)["values"]
            viewed_value = self.checked_image if values[10] == 1 else self.unchecked_image
            favourites_value = self.checked_image if values[11] == 1 else self.unchecked_image

            self.names_treeview.item(item, image=viewed_value, column="#11")
            self.names_treeview.item(item, image=favourites_value, column="#12")

    def show_tooltip(self, event):
        """Отображение подсказки при наведении на ячейку"""
        region = self.names_treeview.identify_region(event.x, event.y)
        if region != "cell":
            self.tooltip.hide()
            return

        column = self.names_treeview.identify_column(event.x)
        item_id = self.names_treeview.identify_row(event.y)

        if not item_id:
            self.tooltip.hide()
            return

        column_index = int(column.replace("#", "")) - 1
        item_values = self.names_treeview.item(item_id)["values"]

        if column_index >= len(item_values):
            self.tooltip.hide()
            return

        cell_text = str(item_values[column_index])

        cell_coords = self.names_treeview.bbox(item_id, column)
        if not cell_coords:
            self.tooltip.hide()
            return
        x, y, width, height = cell_coords

        x_root = self.names_treeview.winfo_rootx() + x
        y_root = self.names_treeview.winfo_rooty() + y + height
        self.tooltip.show(cell_text, x_root, y_root)

    def run_async(self, func):
        """Запуск асинхронной функции."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(func())

    def clear_database(self):
        self.db.clear_database()
        self.update_parsings_treeview()
        self.names_treeview.delete(*self.names_treeview.get_children())

    def delete_parsing(self):
        """Удаление выбранного отбора."""
        selected_item = self.parsings_treeview.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите отбор для удаления.")
            return

        parsing_id = self.parsings_treeview.item(selected_item)["values"][0]

        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить отбор №{parsing_id}?")
        if not confirm:
            return

        self.db.cursor.execute("DELETE FROM Parsings WHERE ParsingID = ?", (parsing_id,))
        self.db.con.commit()

        self.db.cursor.execute("DELETE FROM Names WHERE ParsingID = ?", (parsing_id,))
        self.db.con.commit()

        self.update_parsings_treeview()
        self.names_treeview.delete(*self.names_treeview.get_children())