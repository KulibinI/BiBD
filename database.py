import sqlite3

class Database:
    def __init__(self):
        self.con = sqlite3.connect('database.db')
        self.cursor = self.con.cursor()
        self.init_database()

    def init_database(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Names(
           ParsingID INTEGER,
           ID Integer,
           Name STRING,
           Date STRING,
           Archive STRING,
           Fond STRING,
           Inventory STRING,
           Cases STRING,
           Page STRING,
           URL STRING,
           Viewed INTEGER DEFAULT 0,
           Favourites INTEGER DEFAULT 0,                                                
           FOREIGN KEY (ParsingID) REFERENCES Parsings(ParsingID)
        );
        """)
        self.con.commit()

        self.cursor.execute("PRAGMA table_info(Names);")
        columns = self.cursor.fetchall()
        column_names = [column[1] for column in columns]

        if "Date" not in column_names:
            self.cursor.execute("ALTER TABLE Names ADD COLUMN Date STRING;")
            self.con.commit()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Parsings(
           ParsingID INTEGER PRIMARY KEY,
           Date STRING,
           Request STRING,
           Volume INT
        );
        """)
        self.con.commit()

    def clear_database(self):
        self.cursor.execute("DELETE FROM Names")
        self.cursor.execute("DELETE FROM Parsings")
        self.con.commit()