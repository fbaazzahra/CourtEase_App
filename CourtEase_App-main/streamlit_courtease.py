import streamlit as st
import sqlite3

# =======================================================
#                 DATABASE CONNECTION
# =======================================================
class Database:
    def __init__(self, db_name="courtease.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS Field (
                name TEXT PRIMARY KEY,
                type TEXT,
                price REAL
            )
        """)
        self.c.execute("""
            CREATE TABLE IF NOT EXISTS Booking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_name TEXT,
                date TEXT,
                start_time TEXT,
                duration INTEGER
            )
        """)
        self.conn.commit()


# =======================================================
#                        FIELD
# =======================================================
class Field:
    def __init__(self, name, type, price_per_hour):
        self._name = name
        self._type = type
        self._price_per_hour = price_per_hour

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

    def get_price(self):
        return self._price_per_hour


# =======================================================
#                   FIELD REPOSITORY
# =======================================================
class FieldRepository:
    def __init__(self, db: Database):
        self.db = db

    def create_field(self, name, type, price):
        q = "INSERT INTO Field (name, type, price) VALUES (?, ?, ?)"
        self.db.c.execute(q, (name, type, price))
        self.db.conn.commit()

    def get_all(self):
        self.db.c.execute("SELECT name, type, price FROM Field")
        rows = self.db.c.fetchall()
        return [Field(r[0], r[1], r[2]) for r in rows]

    def delete_field(self, name):
        self.db.c.execute("DELETE FROM Field WHERE name=?", (name,))
        self.db.conn.commit()


# =======================================================
#                        BOOKING
# =======================================================
class Booking:
    def __init__(self, field: Field, date, start_time, duration):
        self.field = field
        self._date = date
        self._start_time = start_time
        self._duration = duration

    def get_date(self):
        return self._date

    def get_start_time(self):
        return self._start_time

    def get_duration(self):
        return self._duration

    def total_cost(self):
        return self._duration * self.field.get_price()


# =======================================================
#                  BOOKING REPOSITORY
# =======================================================
class BookingRepository:
    def __init__(self, db: Database, field_repo: FieldRepository):
        self.db = db
        self.field_repo = field_repo

    def create_booking(self, field_name, date, time, duration):
        q = """
            INSERT INTO Booking (field_name, date, start_time, duration)
            VALUES (?, ?, ?, ?)
        """
        self.db.c.execute(q, (field_name, date, time, duration))
        self.db.conn.commit()

    def get_all(self):
        self.db.c.execute("""
            SELECT field_name, date, start_time, duration
            FROM Booking
        """)
        rows = self.db.c.fetchall()
        bookings = []
        for r in rows:
            field = self.field_repo.get_by_name(r[0])
            if field:
                bookings.append(Booking(field, r[1], r[2], r[3]))
        return bookings

    def delete_booking(self, id):
        self.db.c.execute("DELETE FROM Booking WHERE id=?", (id,))
        self.db.conn.commit()

    def get_by_name(self, name):
        self.db.c.execute("SELECT name, type, price FROM Field WHERE name=?", (name,))
        row = self.db.c.fetchone()
        return Field(row[0], row[1], row[2]) if row else None


# Tambahan method kecil agar tidak error
def field_repo_get_by_name(self, name):
    self.db.c.execute("SELECT name, type, price FROM Field WHERE name=?", (name,))
    row = self.db.c.fetchone()
    return Field(row[0], row[1], row[2]) if row else None

FieldRepository.get_by_name = field_repo_get_by_name


# =======================================================
#                     STREAMLIT APP
# =======================================================
db = Database()
field_repo = FieldRepository(db)
booking_repo = BookingRepository(db, field_repo)

st.title("🏟 CourtEase — Booking Lapangan (OOP Version)")

menu = st.sidebar.radio("Menu", ["Home", "Kelola Lapangan", "Booking", "Data Booking"])


# =======================================================
#                         HOME
# =======================================================
if menu == "Home":
    st.header("Selamat datang di CourtEase 👋")

    fields = field_repo.get_all()
    if not fields:
        st.info("Belum ada lapangan.")
    else:
        for f in fields:
            st.write(f"**{f.get_name()}** — {f.get_type()} — Rp{f.get_price():,.0f}/jam")


# =======================================================
#                    KELOLA LAPANGAN
# =======================================================
elif menu == "Kelola Lapangan":
    st.header("🛠 Kelola Lapangan")

    name = st.text_input("Nama Lapangan")
    type = st.selectbox("Jenis", ["Futsal", "Badminton", "Basket", "Mini Soccer"])
    price = st.number_input("Harga / Jam", min_value=0.0)

    if st.button("Tambah"):
        field_repo.create_field(name, type, price)
        st.success("Lapangan ditambahkan!")
        st.experimental_rerun()

    st.subheader("Daftar Lapangan")
    for f in field_repo.get_all():
        st.write(f"{f.get_name()} — {f.get_type()} — Rp{f.get_price():,.0f}")
        if st.button(f"Hapus {f.get_name()}"):
            field_repo.delete_field(f.get_name())
            st.experimental_rerun()


# =======================================================
#                        BOOKING
# =======================================================
elif menu == "Booking":
    st.header("📅 Booking Lapangan")

    fields = field_repo.get_all()
    if not fields:
        st.warning("Belum ada lapangan.")
    else:
        field_names = [f.get_name() for f in fields]
        chosen = st.selectbox("Pilih Lapangan", field_names)

        date = st.date_input("Tanggal")
        time = st.time_input("Jam Mulai")
        duration = st.number_input("Durasi (jam)", min_value=1)

        if st.button("Buat Booking"):
            booking_repo.create_booking(chosen, str(date), str(time), duration)
            st.success("Booking berhasil!")


# =======================================================
#                     DATA BOOKING
# =======================================================
elif menu == "Data Booking":
    st.header("📄 Data Booking")

    db.db.c.execute("""
        SELECT id, field_name, date, start_time, duration 
        FROM Booking
    """)
    rows = db.db.c.fetchall()

    if not rows:
        st.info("Belum ada booking.")
    else:
        for b in rows:
            field = field_repo.get_by_name(b[1])
            total = field.get_price() * b[4]

            st.write(f"""
                **Lapangan:** {b[1]}  
                **Tanggal:** {b[2]}  
                **Mulai:** {b[3]}  
                **Durasi:** {b[4]} jam  
                **Total:** Rp{total:,.0f}
            """)

            if st.button(f"Hapus Booking {b[0]}"):
                db.db.c.execute("DELETE FROM Booking WHERE id=?", (b[0],))
                db.db.conn.commit()
                st.experimental_rerun()
