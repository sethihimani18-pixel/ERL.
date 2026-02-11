import sqlite3

DATABASE = 'emergency_resources.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    ''')

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM resources")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_resources = [
            ('City General Hospital', 'Hospital', '123 Main St, Delhi', '011-1234567', 28.6139, 77.2090),
            ('Emergency Medical Center', 'Hospital', '456 Park Ave, Delhi', '011-2345678', 28.6289, 77.2190),
            ('Red Cross Ambulance Service', 'Ambulance', '789 Cross Rd, Delhi', '011-3456789', 28.6239, 77.2290),
            ('Quick Response Ambulance', 'Ambulance', '321 Speed Lane, Delhi', '011-4567890', 28.6189, 77.2390),
            ('Central Blood Bank', 'Blood Bank', '654 Life St, Delhi', '011-5678901', 28.6339, 77.2490),
            ('Community Blood Center', 'Blood Bank', '987 Care Blvd, Delhi', '011-6789012', 28.6439, 77.2590),
            ('Metro Hospital', 'Hospital', '147 Health Ave, Delhi', '011-7890123', 28.6039, 77.1990),
            ('Rapid Ambulance Co.', 'Ambulance', '258 Fast Track, Delhi', '011-8901234', 28.6539, 77.2690),
            ('Universal Blood Bank', 'Blood Bank', '369 Donor St, Delhi', '011-9012345', 28.6639, 77.2790),
            ('Apollo Emergency', 'Hospital', '741 Medical Rd, Delhi', '011-0123456', 28.5939, 77.1890)
        ]

        cursor.executemany('''
            INSERT INTO resources (name, type, address, phone, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_resources)

        print("Sample data inserted.")
    else:
        print("Database already contains data. Skipping insertion.")

    conn.commit()
    conn.close()
    print("Database initialized successfully!")


if __name__ == '__main__':
    init_db()
