import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import html
import aiohttp
import asyncio
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import tkinter as tk
from tkinter import scrolledtext

class Parser:
    def __init__(self, db_cursor, update_parsings_func, root=None):
        self.cursor = db_cursor
        self.db = db_cursor.connection
        self.update_parsings_func = update_parsings_func
        self.root = root

    def start_parsing(self, query):
        driver = webdriver.Chrome()

        search_url = f"https://yandex.ru/archive/search?text={query}"
        driver.get(search_url)

        parsing_id = self.get_max_parsing_id() + 1
        IDs = 1
        not_added_urls = []

        while True:
            names = driver.find_elements(By.CSS_SELECTOR, ".Snippet-Title")
            datas = driver.find_elements(By.CSS_SELECTOR, ".Card_CardSubtitle__8MYEY")
            infos = driver.find_elements(By.CSS_SELECTOR, ".Text_TextSecondary__ae_j2")
            URLs = driver.find_elements(By.CSS_SELECTOR, ".Snippet-Title a")
            
            for name, data, info, URLo in zip(names, datas, infos, URLs):
                name_text = name.text
                data_text = data.text
                info_text = info.text
                URL_text = URLo.get_attribute("href")
                base_url = URL_text.split('?')[0]

                data_parts = info_text.split(",")
                if len(data_parts) == 5:
                    part1 = data_parts[0].strip()
                    part2 = data_parts[1].strip()
                    part3 = data_parts[2].strip()
                    part4 = data_parts[3].strip()
                    part5 = data_parts[4].strip()
                
                existing = self.cursor.execute("SELECT COUNT(*) FROM Names WHERE URL LIKE ? AND ParsingID != ?", (base_url + '%', parsing_id)).fetchone()[0]
                if existing == 0:
                    self.cursor.execute("INSERT INTO Names(ParsingID, ID, Name, Date, Archive, Fond, Inventory, Cases, Page, URL) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (parsing_id, IDs, name_text, data_text, part1, part2, part3, part4, part5, URL_text))
                    self.db.commit()
                else:
                    not_added_urls.append(URL_text)
                IDs += 1

            if not self.click_load_more(driver):
                break
            time.sleep(1)

        req = query
        volume = self.cursor.execute("SELECT COUNT(*) FROM Names WHERE ParsingID = ?", (parsing_id,)).fetchone()[0]
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO Parsings(ParsingID, Date, Request, Volume) VALUES (?, ?, ?, ?)", (parsing_id, current_datetime, req, volume))
        self.db.commit()

        driver.quit()
        self.update_parsings_func()
        
        if not_added_urls:
            message = "Следующие ссылки были найдены, но не добавлены в базу данных (уже существуют):\n" + "\n".join(not_added_urls)
        else:
            message = "Все найденные ссылки были добавлены в базу данных."
        
        self.show_message(message)

    def show_message(self, message):
        # Создаем новое окно
        message_window = tk.Toplevel(self.root)
        message_window.title("Результаты парсинга")
        
        # Создаем виджет ScrolledText для отображения сообщения
        text_area = scrolledtext.ScrolledText(message_window, wrap=tk.WORD, width=80, height=20)
        text_area.insert(tk.END, message)
        
        # Убедитесь, что текст находится в редактируемом состоянии
        text_area.config(state=tk.NORMAL)
        
        # Функция копирования текста
        def copy_text(event=None):
            text_area.event_generate("<<Copy>>")

        # Функция выделения всего текста
        def select_all(event=None):
            text_area.tag_add("sel", "1.0", "end")
            text_area.mark_set("insert", "end")
            text_area.see("insert")

        # Создание контекстного меню
        context_menu = tk.Menu(message_window, tearoff=0)
        context_menu.add_command(label="Копировать", command=copy_text)
        context_menu.add_command(label="Выделить всё", command=select_all)

        # Привязываем контекстное меню к правой кнопке мыши
        text_area.bind("<Button-3>", lambda event: context_menu.post(event.x_root, event.y_root))

        # После этого нужно снова сделать его только для чтения
        text_area.config(state=tk.DISABLED)
        
        text_area.pack(padx=10, pady=10)

        # Кнопка для закрытия окна
        close_button = tk.Button(message_window, text="Закрыть", command=message_window.destroy)
        close_button.pack(pady=5)

        # Показать окно
        message_window.mainloop()

    def click_load_more(self, driver):
        try:
            load_more_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'Pagination-PagesItem') and contains(@class, 'Pagination-PagesNext')]"))
            )

            if 'Pagination-PagesItem_disabled' in load_more_button.get_attribute("class"):
                return False
            
            load_more_button.click()
            return True
        except:
            return False

    def get_max_parsing_id(self):
        self.cursor.execute("SELECT MAX(ParsingID) FROM Parsings")
        max_id = self.cursor.fetchone()[0]
        return max_id if max_id else 0

    async def fetch_page(self, session, url):
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()

    async def parse_page(self, page_content, parsing_id):
        tree = html.fromstring(page_content)

        names = tree.cssselect(".Snippet-Title")
        datas = tree.cssselect(".Card_CardSubtitle__8MYEY")
        infos = tree.cssselect(".Text_TextSecondary__ae_j2")
        URLs = tree.cssselect(".Snippet-Title a")

        for name, data, info, URLo in zip(names, datas, infos, URLs):
            name_text = name.text_content().strip()
            data_text = data.text_content().strip()
            info_text = info.text_content().strip()
            URL_text = URLo.get_attribute("href")

            self.cursor.execute("INSERT INTO Names(ParsingID, Name, Date, Info, URL) VALUES (?, ?, ?, ?, ?)", (parsing_id, name_text, data_text, info_text, URL_text))
        self.con.commit()

    async def start_async_parsing(self, query):
        async with aiohttp.ClientSession() as session:
            parsing_id = self.get_max_parsing_id() + 1
            page_number = 1
            base_url = f"https://yandex.ru/archive/search?text={query}"

            while True:
                url = f"{base_url}&PAGEN_1={page_number}"
                page_content = await self.fetch_page(session, url)
                await self.parse_page(page_content, parsing_id)

                tree = html.fromstring(page_content)
                next_button = tree.cssselect("div.pagination__item a:contains('>')")
                if not next_button:
                    break
                page_number += 1
