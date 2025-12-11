import streamlit as st
import sqlite3


# ======================================================
#                CLASS DATABASE (SQLite)
# ======================================================
class Database:
    def __init__(self, db_name="app.db"):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.c = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.c.execute("""
        CREATE TABLE IF NOT EXISTS Field (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL
        )
        """)
        self.conn.commit()

    def add_field(self, name, price):
        self.c.execute("INSERT INTO Field (name, price) VALUES (?, ?)", (name, price))
        self.conn.commit()

    def get_fields(self):
        self.c.execute("SELECT * FROM Field")
        return self.c.fetchall()

    def delete_field(self, id):
        self.c.execute("DELETE FROM Field WHERE id=?", (id,))
        self.conn.commit()



# ======================================================
#              CLASS APLIKASI (Streamlit)
# ======================================================
class App:
    def __init__(self):
        self.db = Database()  # panggil database
        self.menu()

    def menu(self):
        st.title("Contoh Streamlit + SQLite (OOP Sederhana)")
        pilihan = st.sidebar.selectbox("Menu", ["Home", "Kelola Lapangan"])

        if pilihan == "Home":
            self.home()
        elif pilihan == "Kelola Lapangan":
            self.kelola_lapangan()

    def home(self):
        st.header("🏠 Home")
        data = self.db.get_fields()
        if not data:
            st.info("Belum ada data lapangan.")
        else:
            for d in data:
                st.write(f"{d[1]} — Rp{d[2]:,.0f}")

    def kelola_lapangan(self):
        st.header("⚙️ Kelola Lapangan")

        name = st.text_input("Nama Lapangan")
        price = st.number_input("Harga per Jam", min_value=0.0)

        if st.button("Tambah"):
            self.db.add_field(name, price)
            st.success("Berhasil ditambahkan!")

        st.subheader("Data Lapangan")
        for f in self.db.get_fields():
            st.write(f"{f[1]} — Rp{f[2]:,.0f}")
            if st.button(f"Hapus {f[1]}"):
                self.db.delete_field(f[0])
                st.success("Data dihapus!")
                st.experimental_rerun()


# ======================================================
#                    RUN APP
# ======================================================
App()
