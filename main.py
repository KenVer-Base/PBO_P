import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  
    "database": "db_klinik"
}

CURRENT_USER = {
    "IdAkun": None,
    "Nama": None,
    "Role": None
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Error Database", f"Gagal terhubung: {err}")
        return None

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Informasi Klinik Terpadu")
        self.state("zoomed") 
        
        # Style Configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", rowheight=25)
        
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.show_login()

    def show_login(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        LoginFrame(self.container, self).pack(fill="both", expand=True)

    def show_dashboard(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        Dashboard(self.container, self).pack(fill="both", expand=True)


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        bg_frame = ttk.Frame(self)
        bg_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(bg_frame, text="LOGIN SISTEM KLINIK", font=("Helvetica", 16, "bold")).pack(pady=20)
        
        frame = ttk.LabelFrame(bg_frame, text="Masuk sebagai Petugas", padding=20)
        frame.pack(fill="both")
        
        ttk.Label(frame, text="Username:").grid(row=0, column=0, pady=5, sticky="e")
        self.entry_user = ttk.Entry(frame, width=30)
        self.entry_user.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Password:").grid(row=1, column=0, pady=5, sticky="e")
        self.entry_pass = ttk.Entry(frame, show="*", width=30)
        self.entry_pass.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Button(frame, text="LOGIN", command=self.do_login).grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")

    def do_login(self):
        user = self.entry_user.get()
        pwd = self.entry_pass.get()
        
        conn = get_db()
        if conn:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM akun WHERE Username=%s AND Password=%s", (user, pwd))
            account = cur.fetchone()
            conn.close()
            
            if account:
                CURRENT_USER["IdAkun"] = account["IdAkun"]
                CURRENT_USER["Nama"] = account["NamaLengkap"]
                CURRENT_USER["Role"] = account["Jobdesk"]
                messagebox.showinfo("Login Sukses", f"Selamat Datang, {account['NamaLengkap']} ({account['Jobdesk']})")
                self.controller.show_dashboard()
            else:
                messagebox.showerror("Gagal", "Username atau Password salah!")


class Dashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        header = ttk.Frame(self, padding=10)
        header.pack(fill="x")
        ttk.Label(header, text=f"User: {CURRENT_USER['Nama']} | Role: {CURRENT_USER['Role']}", 
                  font=("Arial", 12, "bold"), foreground="#0055aa").pack(side="left")
        ttk.Button(header, text="Logout", command=controller.show_login).pack(side="right")
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        role = CURRENT_USER['Role']
        
        if role == 'Admin':
            self.notebook.add(FrameMasterPasien(self.notebook), text="Master Pasien")
            self.notebook.add(FrameMasterObat(self.notebook), text="Master Obat")
            self.notebook.add(FrameMasterAkun(self.notebook), text="Master Akun")

        if role in ['Frontdesk', 'Admin']:
            self.notebook.add(FramePendaftaran(self.notebook), text="Pendaftaran")

        if role in ['Perawat', 'Admin']:
            self.notebook.add(FramePerawat(self.notebook), text="Pemeriksaan Fisik")

        if role in ['Dokter', 'Admin']:
            self.notebook.add(FrameDokter(self.notebook), text="Dokter & Resep")
            
        if role in ['Kasir', 'Admin']:
            self.notebook.add(FrameKasir(self.notebook), text="Kasir")


class BaseCRUD(ttk.Frame):
    def __init__(self, parent, title):
        super().__init__(parent)
        ttk.Label(self, text=title, font=("Arial", 14, "bold")).pack(pady=10)
        self.tree = ttk.Treeview(self, show='headings', height=10)
        self.tree.pack(fill="both", expand=True, padx=10)
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Refresh Data", command=self.load_data).pack(side="left", padx=5)
        
        self.load_data()

    def load_data(self): pass

class FrameMasterPasien(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Data Pasien (Client)")
        self.tree['columns'] = ("ID", "Nama", "Gender", "Usia", "Alamat")
        for c in self.tree['columns']: self.tree.heading(c, text=c)

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM pasien")
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

class FrameMasterObat(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Data Obat (Gudang)")
        self.tree['columns'] = ("ID", "Nama", "Stok", "Satuan", "Harga")
        for c in self.tree['columns']: self.tree.heading(c, text=c)

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM barang")
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

class FrameMasterAkun(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Data Akun Pegawai")
        self.tree['columns'] = ("ID", "Username", "Nama", "Jobdesk")
        for c in self.tree['columns']: self.tree.heading(c, text=c)

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT IdAkun, Username, NamaLengkap, Jobdesk FROM akun")
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()


class FramePendaftaran(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        f_form = ttk.LabelFrame(self, text="Form Pendaftaran Kunjungan", padding=10)
        f_form.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(f_form, text="Cari Pasien:").grid(row=0, column=0, sticky="w")
        
        f_pasien = ttk.Frame(f_form)
        f_pasien.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        self.cb_pasien = ttk.Combobox(f_pasien, state="readonly", width=35)
        self.cb_pasien.pack(side="left")
        
        btn_new = ttk.Button(f_pasien, text="+ Pasien Baru", command=self.popup_pasien_baru)
        btn_new.pack(side="left", padx=5)
        
        ttk.Label(f_form, text="Dokter Tujuan:").grid(row=1, column=0, sticky="w")
        self.cb_dokter = ttk.Combobox(f_form, state="readonly", width=35)
        self.cb_dokter.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Button(f_form, text="DAFTARKAN PASIEN", command=self.simpan_daftar).grid(row=2, column=1, pady=15, sticky="w")
        
        self.tree = ttk.Treeview(self, columns=("NoReg", "Pasien", "Dokter", "Status"), show="headings")
        for c in ("NoReg", "Pasien", "Dokter", "Status"): self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.refresh_data()

    def refresh_data(self):
        conn = get_db()
        cur = conn.cursor()
        
        cur.execute("SELECT IdPasien, Nama FROM pasien ORDER BY Nama ASC")
        self.cb_pasien['values'] = [f"{x[0]} | {x[1]}" for x in cur.fetchall()]
        
        cur.execute("SELECT IdAkun, NamaLengkap FROM akun WHERE Jobdesk='Dokter'")
        self.cb_dokter['values'] = [f"{x[0]} | {x[1]}" for x in cur.fetchall()]
        
        for i in self.tree.get_children(): self.tree.delete(i)
        query = """SELECT p.NoReg, ps.Nama, ak.NamaLengkap, p.Status 
                   FROM pendaftaran p 
                   JOIN pasien ps ON p.IdPasien = ps.IdPasien
                   JOIN akun ak ON p.IdAkun_Dokter = ak.IdAkun
                   ORDER BY p.TanggalDanWaktu DESC"""
        cur.execute(query)
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def popup_pasien_baru(self):
        """Memunculkan Jendela Popup untuk Input Pasien Baru"""
        top = tk.Toplevel(self)
        top.title("Input Data Pasien Baru")
        top.geometry("400x300")
        
        top.transient(self)
        top.grab_set() 
        
        f = ttk.Frame(top, padding=20)
        f.pack(fill="both", expand=True)
        
        ttk.Label(f, text="Nama Lengkap:").grid(row=0, column=0, sticky="w", pady=5)
        e_nama = ttk.Entry(f, width=30)
        e_nama.grid(row=0, column=1, pady=5)
        
        ttk.Label(f, text="Alamat:").grid(row=1, column=0, sticky="w", pady=5)
        e_alamat = ttk.Entry(f, width=30)
        e_alamat.grid(row=1, column=1, pady=5)
        
        ttk.Label(f, text="Gender:").grid(row=2, column=0, sticky="w", pady=5)
        c_gender = ttk.Combobox(f, values=["L", "P"], state="readonly", width=10)
        c_gender.grid(row=2, column=1, sticky="w", pady=5)
        
        ttk.Label(f, text="Usia:").grid(row=3, column=0, sticky="w", pady=5)
        e_usia = ttk.Entry(f, width=10)
        e_usia.grid(row=3, column=1, sticky="w", pady=5)
        
        def simpan_pasien_baru():
            nama, alamat = e_nama.get(), e_alamat.get()
            gender, usia = c_gender.get(), e_usia.get()
            
            if not nama or not gender or not usia:
                messagebox.showwarning("Warning", "Nama, Gender, dan Usia wajib diisi!", parent=top)
                return

            conn = get_db()
            cur = conn.cursor()
            try:
                cur.execute("INSERT INTO pasien (Nama, Alamat, Gender, Usia) VALUES (%s, %s, %s, %s)", 
                            (nama, alamat, gender, usia))
                conn.commit()
                messagebox.showinfo("Sukses", "Data Pasien Baru Tersimpan!", parent=top)
                self.refresh_data() 
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=top)
            finally:
                conn.close()

        ttk.Button(f, text="SIMPAN DATA PASIEN", command=simpan_pasien_baru).grid(row=4, column=1, pady=20, sticky="e")

    def simpan_daftar(self):
        if not self.cb_pasien.get() or not self.cb_dokter.get():
            return messagebox.showwarning("Warning", "Pilih Pasien dan Dokter!")
        
        id_pasien = self.cb_pasien.get().split(" | ")[0]
        id_dokter = self.cb_dokter.get().split(" | ")[0]
        id_frontdesk = CURRENT_USER['IdAkun'] 
        
        today = datetime.now().strftime("%Y%m%d")
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(*) FROM pendaftaran WHERE NoReg LIKE 'REG-{today}%'")
        count = cur.fetchone()[0] + 1
        no_reg = f"REG-{today}-{count:03d}"
        
        try:
            query = """INSERT INTO pendaftaran (NoReg, IdPasien, IdAkun_Frontdesk, IdAkun_Dokter, Status) 
                       VALUES (%s, %s, %s, %s, 'Menunggu')"""
            cur.execute(query, (no_reg, id_pasien, id_frontdesk, id_dokter))
            conn.commit()
            messagebox.showinfo("Sukses", f"Pendaftaran Berhasil\nNo: {no_reg}")
            self.refresh_data()
            self.cb_pasien.set('')
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

class FramePerawat(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        f_input = ttk.LabelFrame(self, text="Input Tanda Vital", padding=10)
        f_input.pack(fill="x", padx=10)
        
        ttk.Label(f_input, text="Pilih Antrian (Menunggu):").grid(row=0, column=0, sticky="w")
        self.cb_antrian = ttk.Combobox(f_input, state="readonly", width=40)
        self.cb_antrian.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(f_input, text="TB (cm):").grid(row=1, column=0); self.e_tb = ttk.Entry(f_input); self.e_tb.grid(row=1, column=1)
        ttk.Label(f_input, text="BB (kg):").grid(row=1, column=2); self.e_bb = ttk.Entry(f_input); self.e_bb.grid(row=1, column=3)
        ttk.Label(f_input, text="Suhu (C):").grid(row=2, column=0); self.e_suhu = ttk.Entry(f_input); self.e_suhu.grid(row=2, column=1)
        ttk.Label(f_input, text="Tensi:").grid(row=2, column=2); self.e_tensi = ttk.Entry(f_input); self.e_tensi.grid(row=2, column=3)
        
        ttk.Button(f_input, text="Simpan Hasil", command=self.simpan_fisik).grid(row=3, column=1, pady=10)
        
        self.refresh_data()

    def refresh_data(self):
        conn = get_db()
        cur = conn.cursor()
        query = """SELECT p.NoReg, ps.Nama 
                   FROM pendaftaran p JOIN pasien ps ON p.IdPasien = ps.IdPasien 
                   WHERE p.Status='Menunggu'"""
        cur.execute(query)
        self.cb_antrian['values'] = [f"{x[0]} | {x[1]}" for x in cur.fetchall()]
        conn.close()

    def simpan_fisik(self):
        if not self.cb_antrian.get(): return
        no_reg = self.cb_antrian.get().split(" | ")[0]
        id_perawat = CURRENT_USER['IdAkun']
        
        conn = get_db()
        cur = conn.cursor()
        try:
            q1 = """INSERT INTO pemeriksaanfisik (NoReg, IdAkun_Perawat, TinggiBadan, BeratBadan, Suhu, Tensi)
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            cur.execute(q1, (no_reg, id_perawat, self.e_tb.get(), self.e_bb.get(), self.e_suhu.get(), self.e_tensi.get()))
            
            cur.execute("UPDATE pendaftaran SET Status='Diperiksa' WHERE NoReg=%s", (no_reg,))
            
            conn.commit()
            messagebox.showinfo("Sukses", "Data Fisik Disimpan. Pasien diteruskan ke Dokter.")
            self.refresh_data()
            self.cb_antrian.set('')
            for e in [self.e_tb, self.e_bb, self.e_suhu, self.e_tensi]: e.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

class FrameDokter(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.cart_obat = [] 
        
        f_top = ttk.Frame(self, padding=5)
        f_top.pack(fill="x")
        ttk.Label(f_top, text="Antrian Pasien:").pack(side="left")
        self.cb_pasien = ttk.Combobox(f_top, state="readonly", width=40)
        self.cb_pasien.pack(side="left", padx=5)
        self.cb_pasien.bind("<<ComboboxSelected>>", self.load_fisik_info)
        
        f_mid = ttk.LabelFrame(self, text="Diagnosa & Tindakan", padding=5)
        f_mid.pack(fill="x", padx=5)
        
        self.lbl_info_fisik = ttk.Label(f_mid, text="Data Fisik: -", foreground="blue")
        self.lbl_info_fisik.grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        ttk.Label(f_mid, text="Tindakan Medis:").grid(row=1, column=0, sticky="w")
        self.cb_tindakan = ttk.Combobox(f_mid, state="readonly", width=40)
        self.cb_tindakan.grid(row=1, column=1, sticky="w")
        
        ttk.Label(f_mid, text="Diagnosa Tambahan:").grid(row=2, column=0, sticky="w")
        self.e_diagnosa = ttk.Entry(f_mid, width=40)
        self.e_diagnosa.grid(row=2, column=1, sticky="w")

        f_bot = ttk.LabelFrame(self, text="Resep Obat", padding=5)
        f_bot.pack(fill="both", expand=True, padx=5, pady=5)
        
        f_add = ttk.Frame(f_bot)
        f_add.pack(fill="x")
        ttk.Label(f_add, text="Obat:").pack(side="left")
        self.cb_obat = ttk.Combobox(f_add, state="readonly", width=25)
        self.cb_obat.pack(side="left", padx=5)
        ttk.Label(f_add, text="Jml:").pack(side="left")
        self.e_jml = ttk.Entry(f_add, width=5)
        self.e_jml.pack(side="left")
        ttk.Button(f_add, text="+ Tambah Obat", command=self.tambah_obat).pack(side="left", padx=5)
        
        self.tree_cart = ttk.Treeview(f_bot, columns=("ID", "Nama", "Jml", "Subtotal"), show="headings", height=5)
        for c in ("ID", "Nama", "Jml", "Subtotal"): self.tree_cart.heading(c, text=c)
        self.tree_cart.pack(fill="both", expand=True)
        
        ttk.Button(self, text="SIMPAN REKAM MEDIS & SELESAI", command=self.simpan_all).pack(fill="x", pady=10)
        
        self.refresh_data()

    def refresh_data(self):
        conn = get_db()
        cur = conn.cursor()
        query = """SELECT p.NoReg, ps.Nama, p.Status 
                   FROM pendaftaran p JOIN pasien ps ON p.IdPasien = ps.IdPasien
                   WHERE p.Status IN ('Menunggu', 'Diperiksa')"""
        
        if CURRENT_USER['Role'] == 'Dokter':
            query += f" AND p.IdAkun_Dokter = {CURRENT_USER['IdAkun']}"
            
        cur.execute(query)
        self.cb_pasien['values'] = [f"{x[0]} | {x[1]} ({x[2]})" for x in cur.fetchall()]
        
        cur.execute("SELECT IdTindakan, NamaTindakan, Tarif FROM master_tindakan")
        self.cb_tindakan['values'] = [f"{x[0]} | {x[1]} | Rp{int(x[2])}" for x in cur.fetchall()]
        
        cur.execute("SELECT IdBarang, NamaBarang, HargaSatuan FROM barang WHERE Stok > 0")
        self.cb_obat['values'] = [f"{x[0]} | {x[1]} | @{int(x[2])}" for x in cur.fetchall()]
        conn.close()

    def load_fisik_info(self, event):
        if not self.cb_pasien.get(): return
        no_reg = self.cb_pasien.get().split(" | ")[0]
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM pemeriksaanfisik WHERE NoReg='{no_reg}'")
        res = cur.fetchone()
        conn.close()
        if res:
            self.lbl_info_fisik.config(text=f"Tensi: {res['Tensi']}, Suhu: {res['Suhu']}C, BB: {res['BeratBadan']}kg")
        else:
            self.lbl_info_fisik.config(text="Data Fisik: Belum diperiksa perawat")

    def tambah_obat(self):
        val = self.cb_obat.get()
        qty = self.e_jml.get()
        if not val or not qty.isdigit(): return
        
        id_obat = val.split(" | ")[0]
        nama_obat = val.split(" | ")[1]
        harga = float(val.split(" | @")[1])
        subtotal = harga * int(qty)
        
        self.cart_obat.append({"id": id_obat, "nama": nama_obat, "qty": int(qty), "sub": subtotal})
        self.tree_cart.insert("", "end", values=(id_obat, nama_obat, qty, int(subtotal)))
        self.e_jml.delete(0, tk.END)

    def simpan_all(self):
        if not self.cb_pasien.get() or not self.cb_tindakan.get():
            return messagebox.showwarning("Warning", "Pilih Pasien dan Tindakan!")
            
        no_reg = self.cb_pasien.get().split(" | ")[0]
        
        str_tindakan = self.cb_tindakan.get()
        nama_tindakan = str_tindakan.split(" | ")[1]
        tarif_tindakan = float(str_tindakan.split(" | Rp")[1])
        
        diagnosa_final = f"{nama_tindakan}. {self.e_diagnosa.get()}"
        
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO rekammedis (NoReg, Diagnosa, CatatanDokter) VALUES (%s, %s, 'Resep Diberikan')", 
                        (no_reg, diagnosa_final))
            id_rek = cur.lastrowid
            
            total_obat = 0
            for item in self.cart_obat:
                cur.execute("INSERT INTO resepobat (IdRek, IdBarang, Jumlah, SubTotalHarga) VALUES (%s, %s, %s, %s)",
                            (id_rek, item['id'], item['qty'], item['sub']))
                cur.execute("UPDATE barang SET Stok = Stok - %s WHERE IdBarang=%s", (item['qty'], item['id']))
                total_obat += item['sub']
                
            grand_total = tarif_tindakan + total_obat
            no_tagihan = f"INV-{no_reg}"
            cur.execute("""INSERT INTO tagihan (NoTagihan, NoReg, TotalBiayaTindakan, TotalBiayaObat, GrandTotal, StatusBayar)
                           VALUES (%s, %s, %s, %s, %s, 'Pending')""",
                        (no_tagihan, no_reg, tarif_tindakan, total_obat, grand_total))
            
            cur.execute("UPDATE pendaftaran SET Status='Selesai' WHERE NoReg=%s", (no_reg,))
            
            conn.commit()
            messagebox.showinfo("Sukses", "Pemeriksaan Selesai. Data masuk ke Kasir.")
            self.refresh_data()
            self.cart_obat = []
            for i in self.tree_cart.get_children(): self.tree_cart.delete(i)
            self.cb_pasien.set('')
            self.e_diagnosa.delete(0, tk.END)
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

class FrameKasir(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.tree = ttk.Treeview(self, columns=("NoTagihan", "NoReg", "Tindakan", "Obat", "Total", "Status"), show="headings")
        for c in self.tree['columns']: self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Refresh Data", command=self.refresh_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="PROSES BAYAR (LUNAS)", command=self.bayar).pack(side="left", padx=5)
        
        self.refresh_data()

    def refresh_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tagihan WHERE StatusBayar='Pending'")
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def bayar(self):
        sel = self.tree.selection()
        if not sel: return
        no_tagihan = self.tree.item(sel[0])['values'][0]
        
        if messagebox.askyesno("Konfirmasi", f"Bayar Lunas tagihan {no_tagihan}?"):
            conn = get_db()
            cur = conn.cursor()
            cur.execute("UPDATE tagihan SET StatusBayar='Lunas' WHERE NoTagihan=%s", (no_tagihan,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sukses", "Pembayaran Berhasil!")
            self.refresh_data()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()