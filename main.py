import tkinter as tk
from tkinter import ttk, messagebox
from models import AuthModel, MasterDataModel, PendaftaranModel, DokterModel, KasirModel

CURRENT_USER = {"IdAkun": None, "Nama": None, "Role": None}

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Informasi Klinik Terpadu (OOP Version)")
        self.state("zoomed") 
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", rowheight=25)
        
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.show_login()

    def show_login(self):
        self.clear_frame()
        LoginFrame(self.container, self).pack(fill="both", expand=True)

    def show_dashboard(self):
        self.clear_frame()
        Dashboard(self.container, self).pack(fill="both", expand=True)

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()


class BasePage(tk.Frame):
    """
    Parent class untuk semua halaman.
    Menyediakan method umum agar tidak perlu rewrite kode message box.
    """
    def __init__(self, parent):
        super().__init__(parent)
    
    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_info(self, message):
        messagebox.showinfo("Sukses", message)
    
    def show_warning(self, message):
        messagebox.showwarning("Peringatan", message)


class LoginFrame(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.model = AuthModel() 
        
        bg = ttk.Frame(self)
        bg.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(bg, text="LOGIN SISTEM OOP", font=("Arial", 16, "bold")).pack(pady=20)
        
        f = ttk.LabelFrame(bg, text="Masuk", padding=20)
        f.pack(fill="both")
        
        ttk.Label(f, text="Username:").grid(row=0, column=0, pady=5)
        self.entry_user = ttk.Entry(f, width=30)
        self.entry_user.grid(row=0, column=1, pady=5)
        
        ttk.Label(f, text="Password:").grid(row=1, column=0, pady=5)
        self.entry_pass = ttk.Entry(f, show="*", width=30)
        self.entry_pass.grid(row=1, column=1, pady=5)
        
        ttk.Button(f, text="LOGIN", command=self.do_login).grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")

    def do_login(self):
        try:
            user_data = self.model.login(self.entry_user.get(), self.entry_pass.get())
            if user_data:
                CURRENT_USER["IdAkun"] = user_data["IdAkun"]
                CURRENT_USER["Nama"] = user_data["NamaLengkap"]
                CURRENT_USER["Role"] = user_data["Jobdesk"]
                self.show_info(f"Selamat Datang, {user_data['NamaLengkap']}")
                self.controller.show_dashboard()
            else:
                self.show_warning("Username atau Password salah!")
        except Exception as e:
            self.show_error(str(e))


class Dashboard(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        header = ttk.Frame(self, padding=10)
        header.pack(fill="x")
        ttk.Label(header, text=f"User: {CURRENT_USER['Nama']} ({CURRENT_USER['Role']})", 
                  font=("Arial", 12, "bold")).pack(side="left")
        ttk.Button(header, text="Logout", command=controller.show_login).pack(side="right")
        
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)
        
        role = CURRENT_USER['Role']
        
        if role == 'Admin':
            nb.add(FrameMasterPasien(nb), text="Master Pasien")
            nb.add(FrameMasterObat(nb), text="Master Obat")

        if role in ['Frontdesk', 'Admin']:
            nb.add(FramePendaftaran(nb), text="Pendaftaran")

        if role in ['Dokter', 'Admin']:
            nb.add(FrameDokter(nb), text="Dokter & Resep")
            
        if role in ['Kasir', 'Admin']:
            nb.add(FrameKasir(nb), text="Kasir")


class BaseCRUD(BasePage):
    """
    Kelas ini mewarisi BasePage.
    Digunakan khusus untuk halaman yang isinya hanya Tabel data.
    """
    def __init__(self, parent, title):
        super().__init__(parent)
        self.model = MasterDataModel()
        
        ttk.Label(self, text=title, font=("Arial", 14, "bold")).pack(pady=10)
        self.tree = ttk.Treeview(self, show='headings', height=10)
        self.tree.pack(fill="both", expand=True, padx=10)
        
        btn = ttk.Frame(self)
        btn.pack(pady=10)
        ttk.Button(btn, text="Refresh Data", command=self.load_data).pack(side="left")
        
        self.after(100, self.load_data)

    def load_data(self):
        pass 

class FrameMasterPasien(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Data Pasien")
        self.tree['columns'] = ("ID", "Nama", "Gender", "Usia", "Alamat")
        for c in self.tree['columns']: self.tree.heading(c, text=c)

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        data = self.model.get_all_pasien()
        for row in data:
            self.tree.insert("", "end", values=(row['IdPasien'], row['Nama'], row['Gender'], row['Usia'], row['Alamat']))

class FrameMasterObat(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Data Obat")
        self.tree['columns'] = ("ID", "Nama", "Stok", "Satuan", "Harga")
        for c in self.tree['columns']: self.tree.heading(c, text=c)

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        data = self.model.get_all_obat()
        for row in data:
            self.tree.insert("", "end", values=(row['IdBarang'], row['NamaBarang'], row['Stok'], row['Satuan'], row['HargaSatuan']))


class FramePendaftaran(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = PendaftaranModel() 
        self.master_model = MasterDataModel() 
        
        f = ttk.LabelFrame(self, text="Pendaftaran", padding=10)
        f.pack(fill="x", padx=10, pady=5)
        
        self.cb_pasien = ttk.Combobox(f, state="readonly", width=30)
        self.cb_pasien.grid(row=0, column=0, padx=5)
        
        self.cb_dokter = ttk.Combobox(f, state="readonly", width=30)
        self.cb_dokter.grid(row=0, column=1, padx=5)
        
        ttk.Button(f, text="Daftar", command=self.simpan).grid(row=0, column=2, padx=5)
        ttk.Button(f, text="+ Pasien Baru", command=self.popup_pasien).grid(row=0, column=3, padx=5)
        
        self.tree = ttk.Treeview(self, columns=("Reg", "Pasien", "Dokter", "Status"), show="headings")
        for c in ("Reg", "Pasien", "Dokter", "Status"): self.tree.heading(c, text=c)
        self.tree.pack(fill="both", expand=True, padx=10)
        
        self.refresh()

    def refresh(self):
        pasien = self.master_model.get_all_pasien()
        self.cb_pasien['values'] = [f"{x['IdPasien']} | {x['Nama']}" for x in pasien]
        
        dokter = self.model.get_dokter_list()
        self.cb_dokter['values'] = [f"{x['IdAkun']} | {x['NamaLengkap']}" for x in dokter]
        
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.model.get_riwayat_hari_ini():
            self.tree.insert("", "end", values=(r['NoReg'], r['Nama'], r['NamaLengkap'], r['Status']))

    def simpan(self):
        if not self.cb_pasien.get() or not self.cb_dokter.get(): return
        try:
            id_pasien = self.cb_pasien.get().split(" | ")[0]
            id_dokter = self.cb_dokter.get().split(" | ")[0]
            reg = self.model.buat_registrasi(id_pasien, id_dokter, CURRENT_USER['IdAkun'])
            self.show_info(f"Terdaftar: {reg}")
            self.refresh()
        except Exception as e:
            self.show_error(str(e))

    def popup_pasien(self):
        # Setup Jendela Popup
        win = tk.Toplevel(self)
        win.title("Input Pasien Baru")
        win.geometry("350x350")
        
        # Buat frame di dalam popup agar lebih rapi
        f_content = ttk.Frame(win, padding=20)
        f_content.pack(fill="both", expand=True)
        
        # 1. Input Nama
        ttk.Label(f_content, text="Nama Lengkap:").pack(anchor="w")
        e_nm = ttk.Entry(f_content)
        e_nm.pack(fill="x", pady=(0, 10))
        
        # 2. Input Gender (INI YANG DIUBAH MENJADI PILIHAN)
        ttk.Label(f_content, text="Jenis Kelamin:").pack(anchor="w")
        
        # values=["L", "P"] -> Pilihan yang muncul
        # state="readonly" -> Agar user tidak bisa mengetik manual (harus pilih)
        cb_gender = ttk.Combobox(f_content, values=["L", "P"], state="readonly")
        cb_gender.pack(fill="x", pady=(0, 10))
        cb_gender.current(0) # Set default otomatis memilih 'L' agar tidak kosong
        
        # 3. Input Usia
        ttk.Label(f_content, text="Usia:").pack(anchor="w")
        e_usia = ttk.Entry(f_content)
        e_usia.pack(fill="x", pady=(0, 10))

        # 4. Input Alamat
        ttk.Label(f_content, text="Alamat:").pack(anchor="w")
        e_alamat = ttk.Entry(f_content)
        e_alamat.pack(fill="x", pady=(0, 10))
        
        def save():
            # Validasi input tidak boleh kosong
            nama = e_nm.get()
            gender = cb_gender.get() # Mengambil nilai dari Pilihan (L/P)
            usia = e_usia.get()
            alamat = e_alamat.get()

            if not nama or not usia:
                messagebox.showwarning("Warning", "Nama dan Usia wajib diisi!", parent=win)
                return

            # Panggil Model untuk simpan ke database
            try:
                self.master_model.tambah_pasien(nama, alamat, gender, usia)
                self.show_info(f"Pasien '{nama}' berhasil ditambahkan!")
                self.refresh() # Refresh dropdown di halaman utama
                win.destroy()  # Tutup popup
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=win)
            
        # Tombol Simpan
        ttk.Button(f_content, text="SIMPAN DATA PASIEN", command=save).pack(pady=20, fill="x")


class FrameDokter(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = DokterModel()
        self.master_model = MasterDataModel()
        self.cart = []
        
        # UI Setup Singkat
        f = ttk.Frame(self); f.pack(fill="x", padx=10)
        ttk.Label(f, text="Pasien Antri:").pack(side="left")
        self.cb_pasien = ttk.Combobox(f, width=30, state="readonly")
        self.cb_pasien.pack(side="left", padx=5)
        
        f2 = ttk.LabelFrame(self, text="Tindakan & Obat"); f2.pack(fill="both", expand=True, padx=10)
        self.e_diagnosa = ttk.Entry(f2, width=40); self.e_diagnosa.pack(pady=5)
        self.e_diagnosa.insert(0, "Input Diagnosa disini...")
        
        self.cb_obat = ttk.Combobox(f2, width=30); self.cb_obat.pack(pady=5)
        ttk.Button(f2, text="Tambah Obat", command=self.add_obat).pack(pady=5)
        
        self.tree_cart = ttk.Treeview(f2, columns=("ID", "Nama", "Qty"), show="headings", height=5)
        self.tree_cart.heading("Nama", text="Nama Obat"); self.tree_cart.pack(fill="x")
        
        ttk.Button(self, text="SIMPAN REKAM MEDIS", command=self.simpan).pack(pady=10)
        
        self.refresh()

    def refresh(self):
        antrian = self.model.get_antrian(CURRENT_USER['IdAkun'])
        self.cb_pasien['values'] = [f"{x['NoReg']} | {x['Nama']}" for x in antrian]
        obat = self.master_model.get_all_obat()
        self.cb_obat['values'] = [f"{x['IdBarang']} | {x['NamaBarang']} | @{int(x['HargaSatuan'])}" for x in obat]

    def add_obat(self):
        val = self.cb_obat.get()
        if val:
            parts = val.split(" | ")
            self.cart.append({'id': parts[0], 'nama': parts[1], 'qty': 1, 'sub': float(parts[2].replace("@", ""))})
            self.tree_cart.insert("", "end", values=(parts[0], parts[1], 1))

    def simpan(self):
        if not self.cb_pasien.get(): return
        no_reg = self.cb_pasien.get().split(" | ")[0]
        try:
            self.model.simpan_transaksi_medis(no_reg, self.e_diagnosa.get(), 50000, self.cart)
            self.show_info("Sukses")
            self.cart = []
            self.refresh()
        except Exception as e:
            self.show_error(str(e))

class FrameKasir(BaseCRUD): # Reuse BaseCRUD karena mirip tabel biasa
    def __init__(self, parent):
        super().__init__(parent, "Kasir - Pending Payment")
        self.model = KasirModel() # Override model
        self.tree['columns'] = ("NoTagihan", "Total", "Status")
        for c in self.tree['columns']: self.tree.heading(c, text=c)
        
        ttk.Button(self, text="BAYAR LUNAS", command=self.bayar).pack()

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.model.get_tagihan_pending():
            self.tree.insert("", "end", values=(r['NoTagihan'], int(r['GrandTotal']), r['StatusBayar']))

    def bayar(self):
        sel = self.tree.selection()
        if sel:
            no = self.tree.item(sel[0])['values'][0]
            self.model.bayar_tagihan(no)
            self.show_info("Lunas!")
            self.load_data()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()