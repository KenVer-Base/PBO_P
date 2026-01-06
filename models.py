import mysql.connector
from datetime import datetime

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  
    "database": "db_klinik"
}

class DatabaseManager:
    def __init__(self):
        self.config = DB_CONFIG
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor(dictionary=True) 
        except mysql.connector.Error as err:
            raise Exception(f"Database Error: {err}")

    def disconnect(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()

    def fetch_all(self, query, params=None):
        self.connect()
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        finally:
            self.disconnect()

    def fetch_one(self, query, params=None):
        self.connect()
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchone()
        finally:
            self.disconnect()

    def execute_query(self, query, params=None):
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

class AuthModel(DatabaseManager):
    def login(self, username, password):
        return self.fetch_one("SELECT * FROM akun WHERE Username=%s AND Password=%s", (username, password))

class MasterDataModel(DatabaseManager):
    # --- PASIEN ---
    def get_all_pasien(self):
        return self.fetch_all("SELECT * FROM pasien ORDER BY Nama ASC")
    
    def tambah_pasien(self, nama, alamat, gender, usia):
        query = "INSERT INTO pasien (Nama, Alamat, Gender, Usia) VALUES (%s, %s, %s, %s)"
        return self.execute_query(query, (nama, alamat, gender, usia))

    def get_all_obat(self):
        query = """SELECT b.*, s.NamaSupplier 
                   FROM barang b 
                   LEFT JOIN supplier s ON b.IdSupplier = s.IdSupplier
                   ORDER BY b.NamaBarang ASC"""
        return self.fetch_all(query)

    def tambah_obat(self, id_supplier, nama, stok, satuan, harga):
        query = "INSERT INTO barang (IdSupplier, NamaBarang, Stok, Satuan, HargaSatuan) VALUES (%s, %s, %s, %s, %s)"
        return self.execute_query(query, (id_supplier, nama, stok, satuan, harga))

    def update_obat_lengkap(self, id_barang, id_supplier, nama, stok, satuan, harga):
        query = """UPDATE barang 
                   SET IdSupplier=%s, NamaBarang=%s, Stok=%s, Satuan=%s, HargaSatuan=%s 
                   WHERE IdBarang=%s"""
        return self.execute_query(query, (id_supplier, nama, stok, satuan, harga, id_barang))

    def hapus_obat(self, id_barang):
        return self.execute_query("DELETE FROM barang WHERE IdBarang=%s", (id_barang,))

    def get_all_tindakan(self):
        return self.fetch_all("SELECT * FROM master_tindakan ORDER BY NamaTindakan ASC")

    def tambah_tindakan(self, nama, tarif):
        query = "INSERT INTO master_tindakan (NamaTindakan, Tarif) VALUES (%s, %s)"
        return self.execute_query(query, (nama, tarif))

    def hapus_tindakan(self, id_tindakan):
        return self.execute_query("DELETE FROM master_tindakan WHERE IdTindakan = %s", (id_tindakan,))

    def get_all_supplier(self):
        return self.fetch_all("SELECT * FROM supplier ORDER BY NamaSupplier ASC")

    def tambah_supplier(self, nama, alamat, telp):
        query = "INSERT INTO supplier (NamaSupplier, Alamat, NoTelepon) VALUES (%s, %s, %s)"
        return self.execute_query(query, (nama, alamat, telp))
    
    def hapus_supplier(self, id_supplier):
        return self.execute_query("DELETE FROM supplier WHERE IdSupplier = %s", (id_supplier,))

class PendaftaranModel(DatabaseManager):
    def get_dokter_list(self):
        return self.fetch_all("SELECT IdAkun, NamaLengkap FROM akun WHERE Jobdesk='Dokter'")

    def get_riwayat_hari_ini(self):
        query = """SELECT p.NoReg, ps.Nama, ak.NamaLengkap, p.Status 
                   FROM pendaftaran p 
                   JOIN pasien ps ON p.IdPasien = ps.IdPasien
                   JOIN akun ak ON p.IdAkun_Dokter = ak.IdAkun
                   WHERE DATE(p.TanggalDanWaktu) = CURDATE()
                   ORDER BY p.TanggalDanWaktu DESC"""
        return self.fetch_all(query)

    def buat_registrasi(self, id_pasien, id_dokter, id_frontdesk):
        self.connect()
        try:
            today = datetime.now().strftime("%Y%m%d")
            self.cursor.execute(f"SELECT COUNT(*) as cnt FROM pendaftaran WHERE NoReg LIKE 'REG-{today}%'")
            res = self.cursor.fetchone()
            count = res['cnt'] + 1 if res else 1
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

class PerawatModel(DatabaseManager):
    def get_antrian_perawat(self):
        query = """SELECT p.NoReg, ps.Nama 
                   FROM pendaftaran p JOIN pasien ps ON p.IdPasien = ps.IdPasien 
                   WHERE p.Status='Menunggu'"""
        return self.fetch_all(query)

    def simpan_pemeriksaan(self, no_reg, id_perawat, tb, bb, suhu, tensi):
        self.connect()
        try:
            q1 = """INSERT INTO pemeriksaanfisik (NoReg, IdAkun_Perawat, TinggiBadan, BeratBadan, Suhu, Tensi)
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(q1, (no_reg, id_perawat, tb, bb, suhu, tensi))
            self.cursor.execute("UPDATE pendaftaran SET Status='Diperiksa' WHERE NoReg=%s", (no_reg,))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            self.disconnect()

class DokterModel(DatabaseManager):
    def get_antrian(self, id_dokter):
        query = """SELECT p.NoReg, ps.Nama, p.Status 
                   FROM pendaftaran p JOIN pasien ps ON p.IdPasien = ps.IdPasien
                   WHERE p.Status IN ('Menunggu', 'Diperiksa') AND p.IdAkun_Dokter = %s"""
        return self.fetch_all(query, (id_dokter,))

    def get_data_fisik(self, no_reg):
        return self.fetch_one("SELECT * FROM pemeriksaanfisik WHERE NoReg=%s", (no_reg,))

    def simpan_transaksi_medis(self, no_reg, diagnosa, tarif_tindakan, cart_obat):
        self.connect()
        try:
            self.cursor.execute("INSERT INTO rekammedis (NoReg, Diagnosa, CatatanDokter) VALUES (%s, %s, 'Resep Diberikan')", 
                                (no_reg, diagnosa))
            id_rek = self.cursor.lastrowid
            
            total_obat = 0
            for item in cart_obat:
                self.cursor.execute("INSERT INTO resepobat (IdRek, IdBarang, Jumlah, SubTotalHarga) VALUES (%s, %s, %s, %s)",
                                    (id_rek, item['id'], item['qty'], item['sub']))
                self.cursor.execute("UPDATE barang SET Stok = Stok - %s WHERE IdBarang=%s", (item['qty'], item['id']))
                total_obat += item['sub']
            
            grand_total = tarif_tindakan + total_obat
            no_tagihan = f"INV-{no_reg}"
            self.cursor.execute("""INSERT INTO tagihan (NoTagihan, NoReg, TotalBiayaTindakan, TotalBiayaObat, GrandTotal, StatusBayar)
                                   VALUES (%s, %s, %s, %s, %s, 'Pending')""",
                                (no_tagihan, no_reg, tarif_tindakan, total_obat, grand_total))
            
            self.cursor.execute("UPDATE pendaftaran SET Status='Selesai' WHERE NoReg=%s", (no_reg,))
            self.conn.commit()
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