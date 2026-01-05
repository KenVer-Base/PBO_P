import mysql.connector
from datetime import datetime

# Konfigurasi Database
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  
    "database": "db_klinik"
}

# --- PARENT CLASS (BASE) ---
class DatabaseManager:
    """
    Kelas Induk yang menangani koneksi database dasar.
    Semua model lain akan mewarisi kelas ini.
    """
    def __init__(self):
        self.config = DB_CONFIG
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            # Menggunakan dictionary=True agar hasil query berupa dict {'nama_kolom': nilai}
            self.cursor = self.conn.cursor(dictionary=True) 
        except mysql.connector.Error as err:
            raise Exception(f"Koneksi Database Gagal: {err}")

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def fetch_all(self, query, params=None):
        """Helper untuk mengambil semua data"""
        self.connect()
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        finally:
            self.disconnect()

    def fetch_one(self, query, params=None):
        """Helper untuk mengambil satu data"""
        self.connect()
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        finally:
            self.disconnect()

    def execute_query(self, query, params=None):
        """Helper untuk Insert/Update/Delete"""
        self.connect()
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.disconnect()


# --- CHILD CLASSES (INHERITANCE) ---

class AuthModel(DatabaseManager):
    """Menangani Logika Login, mewarisi DatabaseManager"""
    def login(self, username, password):
        query = "SELECT * FROM akun WHERE Username=%s AND Password=%s"
        return self.fetch_one(query, (username, password))


class MasterDataModel(DatabaseManager):
    """Menangani CRUD data master (Pasien, Obat, Akun)"""
    
    def get_all_pasien(self):
        return self.fetch_all("SELECT * FROM pasien ORDER BY Nama ASC")
    
    def get_all_obat(self):
        return self.fetch_all("SELECT * FROM barang")

    def get_all_akun(self):
        return self.fetch_all("SELECT IdAkun, Username, NamaLengkap, Jobdesk FROM akun")

    def tambah_pasien(self, nama, alamat, gender, usia):
        query = "INSERT INTO pasien (Nama, Alamat, Gender, Usia) VALUES (%s, %s, %s, %s)"
        return self.execute_query(query, (nama, alamat, gender, usia))


class PendaftaranModel(DatabaseManager):
    """Menangani Logika Frontdesk"""
    
    def get_dokter_list(self):
        return self.fetch_all("SELECT IdAkun, NamaLengkap FROM akun WHERE Jobdesk='Dokter'")

    def get_riwayat_hari_ini(self):
        query = """SELECT p.NoReg, ps.Nama, ak.NamaLengkap, p.Status 
                   FROM pendaftaran p 
                   JOIN pasien ps ON p.IdPasien = ps.IdPasien
                   JOIN akun ak ON p.IdAkun_Dokter = ak.IdAkun
                   ORDER BY p.TanggalDanWaktu DESC"""
        return self.fetch_all(query)

    def buat_registrasi(self, id_pasien, id_dokter, id_frontdesk):
        # Generate No Reg Otomatis
        self.connect() # Manual connect karena butuh transaksi kompleks
        try:
            today = datetime.now().strftime("%Y%m%d")
            self.cursor.execute(f"SELECT COUNT(*) as cnt FROM pendaftaran WHERE NoReg LIKE 'REG-{today}%'")
            count = self.cursor.fetchone()['cnt'] + 1
            no_reg = f"REG-{today}-{count:03d}"

            query = """INSERT INTO pendaftaran (NoReg, IdPasien, IdAkun_Frontdesk, IdAkun_Dokter, Status) 
                       VALUES (%s, %s, %s, %s, 'Menunggu')"""
            self.cursor.execute(query, (no_reg, id_pasien, id_frontdesk, id_dokter))
            self.conn.commit()
            return no_reg
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.disconnect()


class DokterModel(DatabaseManager):
    """Menangani Logika Dokter & Transaksi Medis"""
    
    def get_antrian(self, id_dokter):
        query = """SELECT p.NoReg, ps.Nama, p.Status 
                   FROM pendaftaran p JOIN pasien ps ON p.IdPasien = ps.IdPasien
                   WHERE p.Status IN ('Menunggu', 'Diperiksa') AND p.IdAkun_Dokter = %s"""
        return self.fetch_all(query, (id_dokter,))

    def get_data_fisik(self, no_reg):
        return self.fetch_one("SELECT * FROM pemeriksaanfisik WHERE NoReg=%s", (no_reg,))

    def simpan_transaksi_medis(self, no_reg, diagnosa, tarif_tindakan, cart_obat):
        """
        Logika kompleks: Simpan Rekam Medis -> Simpan Resep -> Potong Stok -> Buat Tagihan
        """
        self.connect()
        try:
            # 1. Rekam Medis
            self.cursor.execute("INSERT INTO rekammedis (NoReg, Diagnosa, CatatanDokter) VALUES (%s, %s, 'Resep Diberikan')", 
                                (no_reg, diagnosa))
            id_rek = self.cursor.lastrowid
            
            # 2. Resep & Stok
            total_obat = 0
            for item in cart_obat:
                self.cursor.execute("INSERT INTO resepobat (IdRek, IdBarang, Jumlah, SubTotalHarga) VALUES (%s, %s, %s, %s)",
                                    (id_rek, item['id'], item['qty'], item['sub']))
                self.cursor.execute("UPDATE barang SET Stok = Stok - %s WHERE IdBarang=%s", (item['qty'], item['id']))
                total_obat += item['sub']
            
            # 3. Tagihan
            grand_total = tarif_tindakan + total_obat
            no_tagihan = f"INV-{no_reg}"
            self.cursor.execute("""INSERT INTO tagihan (NoTagihan, NoReg, TotalBiayaTindakan, TotalBiayaObat, GrandTotal, StatusBayar)
                                   VALUES (%s, %s, %s, %s, %s, 'Pending')""",
                                (no_tagihan, no_reg, tarif_tindakan, total_obat, grand_total))
            
            # 4. Update Status
            self.cursor.execute("UPDATE pendaftaran SET Status='Selesai' WHERE NoReg=%s", (no_reg,))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.disconnect()

class KasirModel(DatabaseManager):
    def get_tagihan_pending(self):
        return self.fetch_all("SELECT * FROM tagihan WHERE StatusBayar='Pending'")

    def bayar_tagihan(self, no_tagihan):
        return self.execute_query("UPDATE tagihan SET StatusBayar='Lunas' WHERE NoTagihan=%s", (no_tagihan,))