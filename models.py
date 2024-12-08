import sqlite3
import os

def get_db_connection():
    """Establish a connection to the database."""
    db_path = os.getenv('DATABASE_PATH', os.path.abspath('secretsanta.db'))
    print(f"Connecting to database at: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


def create_tables():
    """Create necessary tables if they do not already exist."""
    conn = get_db_connection()
    if conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT
        )
        ''')
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT
        )
        ''')
        
        conn.execute('''       
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gifter_id INTEGER NOT NULL,
            recipient_id INTEGER NOT NULL,
            notification_sent BOOLEAN DEFAULT 0,
            reminder_sent BOOLEAN DEFAULT 0,
            FOREIGN KEY (gifter_id) REFERENCES staff(id),
            FOREIGN KEY (recipient_id) REFERENCES staff(id)
        )
        ''')

        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT
        )
        ''')

        conn.execute('''

        CREATE TABLE IF NOT EXISTS assignments (
            gifter_id INTEGER,
            recipient_id INTEGER,
            PRIMARY KEY (gifter_id),
            FOREIGN KEY (gifter_id) REFERENCES staff (id),
            FOREIGN KEY (recipient_id) REFERENCES staff (id)
        )
        ''')

        conn.commit()
        print("Tables created successfully.")
        conn.close()
    else:
        print("Failed to create tables. No database connection.")

def populate_initial_staff():
    """Populate the staff table with initial data."""
    conn = get_db_connection()  # Establish a fresh connection
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM staff")
            count = cursor.fetchone()[0]
            if count == 0:  # Only populate if the table is empty
                staff_list = [

                        {"name": "AISHAT ASELEBE", "phone": "07828437973"},
                        {"name": "AMANDA BASS", "phone": "07840264775"},
                        {"name": 'ASHVINI "ASH" DON', "phone": "07860822084"},
                        {"name": "DAMI ORIMOOGUNJE", "phone": "07833834159"},
                        {"name": "DAMILOLA ESTHER OWOFADEJU", "phone": "07393155176"},
                        {"name": "DARRYL TAPFUMA", "phone": "07957549435"},
                        {"name": 'DOTUN "ALEX" OMOBOYE', "phone": "07745991647"},
                        {"name": 'ERANDI "ANDI" GUNASEKARA', "phone": "07838902789"},
                        {"name": "FOZIA LUNBA", "phone": "07407121467"},
                        {"name": 'IMMACULATE "MACU" DIMONYE', "phone": "07717596444"},
                        {"name": "IRIN SHAJU", "phone": "07867087425"},
                        {"name": "JOLE KAREN SAKEYU", "phone": "07778114791"},
                        {"name": "KEVIN TIMSON", "phone": "07846199563"},
                        {"name": "MADHU DON", "phone": "07309268918"},
                        {"name": "M.A SAEED", "phone": "07424061472"},
                        {"name": "MARIATOU JALLOW", "phone": "07392926381"},
                        {"name": "MICHAEL ASELEBE", "phone": "07482113212"},
                        {"name": 'OLAMIDE "OLA" DAIRO', "phone": "07920698160"},
                        {"name": 'OLUWADAMILARE "WALE" OLAWALE', "phone": "07823813330"},
                        {"name": 'ONOME "MAVIS" ERTHLARHAGHEN', "phone": "07733790213"},
                        {"name": "THILINI PANNILA", "phone": "07800534011"},
                        {"name": "VISHAL ADAV", "phone": "07305192575"},
                        {"name": 'VIVEKANANDA "VIVEK" SADHU', "phone": "07464843439"},
                        {"name": "ZAINAB FALADE", "phone": "07789067252"}
                ]
                cursor.executemany(
                    "INSERT INTO staff (name, phone) VALUES (?, ?)",
                    [(staff["name"], staff["phone"]) for staff in staff_list],
                )
                conn.commit()
                print("Staff table populated successfully.")
            else:
                print("Staff table already populated.")
        except sqlite3.Error as e:
            print(f"Error populating staff table: {e}")
        finally:
            conn.close()  # Ensure connection is closed
    else:
        print("Failed to connect to the database.")
