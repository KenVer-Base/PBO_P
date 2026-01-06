import tkinter as tk
from tkinter import ttk, messagebox
from models import AuthModel, MasterDataModel, PendaftaranModel, DokterModel, KasirModel, PerawatModel

CURRENT_USER = {
    "IdAkun": None, 
    "Nama": None, 
    "Role": None
}

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Klinik Terpadu")
        self.state("zoomed") 
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", rowheight=25)
        
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        self.show_login()

    def show_login(self):
        self.clear_frame()
        frame = LoginFrame(self.container, self)
        frame.pack(fill="both", expand=True)

    def show_dashboard(self):
        self.clear_frame()
        frame = Dashboard(self.container, self)
        frame.pack(fill="both", expand=True)

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

class BasePage(tk.Frame):
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
        
        bg_frame = ttk.Frame(self)
        bg_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(bg_frame, text="SISTEM KLINIK", font=("Arial", 20, "bold")).pack(pady=20)
        
        frame_login = ttk.LabelFrame(bg_frame, text="Login Area", padding=20)
        frame_login.pack(fill="both")
        
        ttk.Label(frame_login, text="Username:").grid(row=0, column=0, pady=5, sticky="e")
        self.entry_user = ttk.Entry(frame_login, width=30)
        self.entry_user.grid(row=0, column=1, pady=5)
        
        ttk.Label(frame_login, text="Password:").grid(row=1, column=0, pady=5, sticky="e")
        self.entry_pass = ttk.Entry(frame_login, show="*", width=30)
        self.entry_pass.grid(row=1, column=1, pady=5)
        
        btn_login = ttk.Button(frame_login, text="MASUK", command=self.do_login)
        btn_login.grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")

    def do_login(self):
        try:
            username = self.entry_user.get()
            password = self.entry_pass.get()
            
            user = self.model.login(username, password)
            
            if user:
                CURRENT_USER["IdAkun"] = user["IdAkun"]
                CURRENT_USER["Nama"] = user["NamaLengkap"]
                CURRENT_USER["Role"] = user["Jobdesk"]
                self.show_info(f"Selamat datang, {user['NamaLengkap']} ({user['Jobdesk']})")
                self.controller.show_dashboard()
            else:
                self.show_warning("Login Gagal: Username/Password salah")
        except Exception as e:
            self.show_error(str(e))

class Dashboard(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        header = ttk.Frame(self, padding=10)
        header.pack(fill="x")
        
        lbl_info = ttk.Label(header, text=f"Login: {CURRENT_USER['Nama']} ({CURRENT_USER['Role']})", font=("Arial", 12, "bold"))
        lbl_info.pack(side="left")
        
        ttk.Button(header, text="Logout", command=controller.show_login).pack(side="right")
        
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        role = CURRENT_USER['Role']
        
        if role == 'Frontdesk':
            notebook.add(FrameMasterObat(notebook), text="Kelola Obat")
            notebook.add(FrameMasterTindakan(notebook), text="Kelola Tindakan")
            notebook.add(FrameMasterSupplier(notebook), text="Kelola Supplier")
            notebook.add(FramePendaftaran(notebook), text="Registrasi Pasien")
            notebook.add(FrameMasterPasien(notebook), text="Data Pasien")

        elif role == 'Perawat':
            notebook.add(FramePerawat(notebook), text="Pemeriksaan Fisik")

        elif role == 'Dokter':
            notebook.add(FrameDokter(notebook), text="Pemeriksaan Dokter")
            
        elif role == 'Kasir':
            notebook.add(FrameKasir(notebook), text="Kasir / Pembayaran")

class BaseCRUD(BasePage):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.model = MasterDataModel()
        
        ttk.Label(self, text=title, font=("Arial", 14, "bold")).pack(pady=10)
        
        self.tree = ttk.Treeview(self, show='headings', height=10)
        self.tree.pack(fill="both", expand=True, padx=10)
        
        self.btn_frame = ttk.Frame(self)
        self.btn_frame.pack(pady=10)
        
        ttk.Button(self.btn_frame, text="Refresh", command=self.load_data).pack(side="left", padx=5)
        
        self.after(100, self.load_data)

    def load_data(self):
        pass

class FrameMasterPasien(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Master Data Pasien")
        self.tree['columns'] = ("ID", "Nama", "Gender", "Usia", "Alamat")
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        data = self.model.get_all_pasien()
        for row in data:
            self.tree.insert("", "end", values=(row['IdPasien'], row['Nama'], row['Gender'], row['Usia'], row['Alamat']))

class FrameMasterObat(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Master Obat & Supplier (ADMIN)")
        # Tambahkan kolom ID Supplier (tersembunyi/gabung) dan Nama Supplier
        self.tree['columns'] = ("ID", "Nama", "Stok", "Satuan", "Harga", "Supplier")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nama", text="Nama Obat")
        self.tree.heading("Stok", text="Stok")
        self.tree.heading("Satuan", text="Satuan")
        self.tree.heading("Harga", text="Harga")
        self.tree.heading("Supplier", text="Supplier")
        
        self.tree.column("ID", width=50)
        
        ttk.Button(self.btn_frame, text="+ Obat Baru", command=self.popup_obat_baru).pack(side="left", padx=5)
        ttk.Button(self.btn_frame, text="Edit Data", command=self.popup_edit_obat).pack(side="left", padx=5)
        ttk.Button(self.btn_frame, text="Hapus", command=self.hapus_obat).pack(side="left", padx=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        data = self.model.get_all_obat()
        for row in data:
            # Format Supplier: ID | Nama (agar saat edit mudah diambil ID-nya)
            supplier_display = f"{row['IdSupplier']} | {row['NamaSupplier']}" if row['IdSupplier'] else "No Supplier"
            self.tree.insert("", "end", values=(
                row['IdBarang'], 
                row['NamaBarang'], 
                row['Stok'], 
                row['Satuan'], 
                int(row['HargaSatuan']),
                supplier_display
            ))

    def get_supplier_list(self):
        # Mengambil list supplier untuk combobox format "ID | Nama"
        raw_data = self.model.get_all_supplier()
        return [f"{s['IdSupplier']} | {s['NamaSupplier']}" for s in raw_data]

    def popup_obat_baru(self):
        window = tk.Toplevel(self)
        window.title("Obat Baru")
        window.geometry("350x400")
        
        frame_input = ttk.Frame(window, padding=10)
        frame_input.pack(fill="both")
        
        ttk.Label(frame_input, text="Pilih Supplier:").pack(anchor="w")
        cb_supplier = ttk.Combobox(frame_input, values=self.get_supplier_list(), state="readonly")
        cb_supplier.pack(fill="x", pady=5)

        ttk.Label(frame_input, text="Nama Obat:").pack(anchor="w")
        entry_nama = ttk.Entry(frame_input)
        entry_nama.pack(fill="x", pady=5)
        
        ttk.Label(frame_input, text="Stok Awal:").pack(anchor="w")
        entry_stok = ttk.Entry(frame_input)
        entry_stok.pack(fill="x", pady=5)
        
        ttk.Label(frame_input, text="Satuan:").pack(anchor="w")
        entry_satuan = ttk.Entry(frame_input)
        entry_satuan.pack(fill="x", pady=5)
        
        ttk.Label(frame_input, text="Harga Jual:").pack(anchor="w")
        entry_harga = ttk.Entry(frame_input)
        entry_harga.pack(fill="x", pady=5)
        
        def save():
            if not cb_supplier.get():
                return messagebox.showwarning("Info", "Pilih Supplier Dulu")
            
            try:
                id_supp = cb_supplier.get().split(" | ")[0]
                self.model.tambah_obat(id_supp, entry_nama.get(), entry_stok.get(), entry_satuan.get(), entry_harga.get())
                self.load_data()
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        ttk.Button(frame_input, text="Simpan", command=save).pack(pady=20)

    def popup_edit_obat(self):
        selected = self.tree.selection()
        if not selected:
            return messagebox.showwarning("Info", "Pilih obat yang mau diedit")
        
        values = self.tree.item(selected[0])['values']
        id_barang = values[0]
        current_supplier_str = str(values[5]) # "ID | Nama"
        
        window = tk.Toplevel(self)
        window.title(f"Edit Obat: {values[1]}")
        window.geometry("350x400")
        
        frame_input = ttk.Frame(window, padding=10)
        frame_input.pack(fill="both")
        
        ttk.Label(frame_input, text="Supplier:").pack(anchor="w")
        cb_supplier = ttk.Combobox(frame_input, values=self.get_supplier_list(), state="readonly")
        cb_supplier.pack(fill="x", pady=5)
        # Set combobox value to current supplier
        if " | " in current_supplier_str:
             cb_supplier.set(current_supplier_str)

        ttk.Label(frame_input, text="Nama Obat:").pack(anchor="w")
        entry_nama = ttk.Entry(frame_input)
        entry_nama.pack(fill="x", pady=5)
        entry_nama.insert(0, values[1])
        
        ttk.Label(frame_input, text="Stok:").pack(anchor="w")
        entry_stok = ttk.Entry(frame_input)
        entry_stok.pack(fill="x", pady=5)
        entry_stok.insert(0, values[2])
        
        ttk.Label(frame_input, text="Satuan:").pack(anchor="w")
        entry_satuan = ttk.Entry(frame_input)
        entry_satuan.pack(fill="x", pady=5)
        entry_satuan.insert(0, values[3])
        
        ttk.Label(frame_input, text="Harga Jual:").pack(anchor="w")
        entry_harga = ttk.Entry(frame_input)
        entry_harga.pack(fill="x", pady=5)
        entry_harga.insert(0, values[4])
        
        def save_changes():
            if not cb_supplier.get():
                return messagebox.showwarning("Info", "Supplier tidak boleh kosong")

            try:
                id_supp = cb_supplier.get().split(" | ")[0]
                self.model.update_obat_lengkap(id_barang, id_supp, entry_nama.get(), entry_stok.get(), entry_satuan.get(), entry_harga.get())
                self.show_info("Data Obat Diperbarui")
                self.load_data()
                window.destroy()
            except Exception as e:
                self.show_error(str(e))
        
        ttk.Button(frame_input, text="Update Data", command=save_changes).pack(pady=20)

    def hapus_obat(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        values = self.tree.item(selected[0])['values']
        
        if messagebox.askyesno("Hapus", f"Yakin hapus obat '{values[1]}' selamanya?"):
            try:
                self.model.hapus_obat(values[0])
                self.show_info("Obat dihapus")
                self.load_data()
            except Exception as e:
                self.show_error(f"Gagal hapus (mungkin sudah dipakai transaksi): {e}")

class FrameMasterTindakan(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Master Tarif & Tindakan (ADMIN)")
        self.tree['columns'] = ("ID", "Nama Tindakan", "Tarif")
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        
        ttk.Button(self.btn_frame, text="+ Tindakan Baru", command=self.popup_tambah).pack(side="left", padx=5)
        ttk.Button(self.btn_frame, text="Hapus", command=self.hapus).pack(side="left", padx=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        data = self.model.get_all_tindakan()
        for row in data:
            self.tree.insert("", "end", values=(row['IdTindakan'], row['NamaTindakan'], int(row['Tarif'])))

    def popup_tambah(self):
        window = tk.Toplevel(self)
        window.title("Tindakan Baru")
        window.geometry("300x250")
        
        frame_input = ttk.Frame(window, padding=10)
        frame_input.pack(fill="both")
        
        ttk.Label(frame_input, text="Nama Tindakan:").pack(anchor="w")
        entry_nama = ttk.Entry(frame_input)
        entry_nama.pack(fill="x", pady=5)
        
        ttk.Label(frame_input, text="Tarif (Rp):").pack(anchor="w")
        entry_tarif = ttk.Entry(frame_input)
        entry_tarif.pack(fill="x", pady=5)
        
        def save():
            try:
                self.model.tambah_tindakan(entry_nama.get(), entry_tarif.get())
                self.load_data()
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        ttk.Button(frame_input, text="Simpan", command=save).pack(pady=10)

    def hapus(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        id_tindakan = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Konfirmasi", "Hapus tindakan ini?"):
            self.model.hapus_tindakan(id_tindakan)
            self.load_data()

class FrameMasterSupplier(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Data Supplier (ADMIN)")
        self.tree['columns'] = ("ID", "Nama Supplier", "Alamat", "Telepon")
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
        
        ttk.Button(self.btn_frame, text="+ Supplier Baru", command=self.popup_tambah).pack(side="left", padx=5)
        ttk.Button(self.btn_frame, text="Hapus", command=self.hapus).pack(side="left", padx=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        data = self.model.get_all_supplier()
        for row in data:
            self.tree.insert("", "end", values=(row['IdSupplier'], row['NamaSupplier'], row['Alamat'], row['NoTelepon']))

    def popup_tambah(self):
        window = tk.Toplevel(self)
        window.title("Supplier Baru")
        window.geometry("300x300")
        
        frame_input = ttk.Frame(window, padding=10)
        frame_input.pack(fill="both")
        
        ttk.Label(frame_input, text="Nama PT/Supplier:").pack(anchor="w")
        entry_nama = ttk.Entry(frame_input)
        entry_nama.pack(fill="x", pady=5)
        
        ttk.Label(frame_input, text="Alamat:").pack(anchor="w")
        entry_alamat = ttk.Entry(frame_input)
        entry_alamat.pack(fill="x", pady=5)
        
        ttk.Label(frame_input, text="No Telepon:").pack(anchor="w")
        entry_telp = ttk.Entry(frame_input)
        entry_telp.pack(fill="x", pady=5)
        
        def save():
            try:
                self.model.tambah_supplier(entry_nama.get(), entry_alamat.get(), entry_telp.get())
                self.load_data()
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        ttk.Button(frame_input, text="Simpan", command=save).pack(pady=10)

    def hapus(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        id_sup = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Konfirmasi", "Hapus Supplier ini?"):
            try:
                self.model.hapus_supplier(id_sup)
                self.load_data()
            except Exception as e:
                self.show_error(f"Gagal menghapus! Supplier ini terhubung ke data Obat.\n\nDetail Error: {e}")

class FramePendaftaran(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = PendaftaranModel()
        self.master_model = MasterDataModel()
        
        frame_input = ttk.LabelFrame(self, text="Registrasi Pasien Baru/Lama", padding=10)
        frame_input.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(frame_input, text="Pasien:").grid(row=0, column=0)
        self.cb_pasien = ttk.Combobox(frame_input, state="readonly", width=30)
        self.cb_pasien.grid(row=0, column=1, padx=5)
        
        ttk.Label(frame_input, text="Dokter Tujuan:").grid(row=0, column=2)
        self.cb_dokter = ttk.Combobox(frame_input, state="readonly", width=30)
        self.cb_dokter.grid(row=0, column=3, padx=5)
        
        ttk.Button(frame_input, text="DAFTAR", command=self.simpan).grid(row=0, column=4, padx=5)
        ttk.Button(frame_input, text="+ Input Pasien Baru", command=self.popup_pasien).grid(row=0, column=5, padx=5)
        
        self.tree = ttk.Treeview(self, columns=("Reg", "Pasien", "Dokter", "Status"), show="headings")
        for col in ("Reg", "Pasien", "Dokter", "Status"):
            self.tree.heading(col, text=col)
            
        self.tree.pack(fill="both", expand=True, padx=10)
        
        self.refresh()

    def refresh(self):
        list_pasien = self.master_model.get_all_pasien()
        self.cb_pasien['values'] = [f"{x['IdPasien']} | {x['Nama']}" for x in list_pasien]
        
        list_dokter = self.model.get_dokter_list()
        self.cb_dokter['values'] = [f"{x['IdAkun']} | {x['NamaLengkap']}" for x in list_dokter]
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        riwayat = self.model.get_riwayat_hari_ini()
        for row in riwayat:
            self.tree.insert("", "end", values=(row['NoReg'], row['Nama'], row['NamaLengkap'], row['Status']))

    def simpan(self):
        if not self.cb_pasien.get() or not self.cb_dokter.get():
            return
            
        try:
            id_pasien = self.cb_pasien.get().split(" | ")[0]
            id_dokter = self.cb_dokter.get().split(" | ")[0]
            
            reg = self.model.buat_registrasi(id_pasien, id_dokter, CURRENT_USER['IdAkun'])
            self.show_info(f"Berhasil Mendaftar: {reg}")
            self.refresh()
        except Exception as e:
            self.show_error(str(e))

    def popup_pasien(self):
        window = tk.Toplevel(self)
        window.title("Pasien Baru")
        window.geometry("300x350")
        
        frame_input = ttk.Frame(window, padding=10)
        frame_input.pack(fill="both")

        ttk.Label(frame_input, text="Nama:").pack(anchor="w")
        entry_nama = ttk.Entry(frame_input)
        entry_nama.pack(fill="x", pady=5)
        
        ttk.Label(frame_input, text="Gender:").pack(anchor="w")
        cb_gender = ttk.Combobox(frame_input, values=["L", "P"], state="readonly")
        cb_gender.pack(fill="x", pady=5)
        cb_gender.current(0)
        
        ttk.Label(frame_input, text="Usia:").pack(anchor="w")
        entry_usia = ttk.Entry(frame_input)
        entry_usia.pack(fill="x", pady=5)
        
        ttk.Label(frame_input, text="Alamat:").pack(anchor="w")
        entry_alamat = ttk.Entry(frame_input)
        entry_alamat.pack(fill="x", pady=5)
        
        def save():
            if not entry_nama.get() or not entry_usia.get():
                return
            try:
                self.master_model.tambah_pasien(entry_nama.get(), entry_alamat.get(), cb_gender.get(), entry_usia.get())
                self.refresh()
                window.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                
        ttk.Button(frame_input, text="Simpan", command=save).pack(pady=20)

class FramePerawat(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = PerawatModel()
        
        frame_input = ttk.LabelFrame(self, text="Pemeriksaan Awal (Tanda Vital)", padding=10)
        frame_input.pack(fill="x", padx=10)
        
        ttk.Label(frame_input, text="Antrian Pasien:").grid(row=0, column=0)
        self.cb_antrian = ttk.Combobox(frame_input, width=40, state="readonly")
        self.cb_antrian.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_input, text="TB (cm):").grid(row=1, column=0)
        self.entry_tb = ttk.Entry(frame_input)
        self.entry_tb.grid(row=1, column=1)
        
        ttk.Label(frame_input, text="BB (kg):").grid(row=1, column=2)
        self.entry_bb = ttk.Entry(frame_input)
        self.entry_bb.grid(row=1, column=3)
        
        ttk.Label(frame_input, text="Suhu (C):").grid(row=2, column=0)
        self.entry_suhu = ttk.Entry(frame_input)
        self.entry_suhu.grid(row=2, column=1)
        
        ttk.Label(frame_input, text="Tensi:").grid(row=2, column=2)
        self.entry_tensi = ttk.Entry(frame_input)
        self.entry_tensi.grid(row=2, column=3)
        
        ttk.Button(frame_input, text="SIMPAN DATA", command=self.simpan).grid(row=3, column=1, pady=10)
        self.refresh()

    def refresh(self):
        self.cb_antrian.set('')
        for entry in [self.entry_tb, self.entry_bb, self.entry_suhu, self.entry_tensi]:
            entry.delete(0, tk.END)
            
        try:
            antrian = self.model.get_antrian_perawat()
            self.cb_antrian['values'] = [f"{x['NoReg']} | {x['Nama']}" for x in antrian]
        except Exception as e:
            self.show_error(str(e))

    def simpan(self):
        if not self.cb_antrian.get():
            return
            
        no_reg = self.cb_antrian.get().split(" | ")[0]
        try:
            self.model.simpan_pemeriksaan(
                no_reg, 
                CURRENT_USER['IdAkun'], 
                self.entry_tb.get(), 
                self.entry_bb.get(), 
                self.entry_suhu.get(), 
                self.entry_tensi.get()
            )
            self.show_info("Data Fisik Tersimpan")
            self.refresh()
        except Exception as e:
            self.show_error(str(e))

class FrameDokter(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = DokterModel()
        self.master_model = MasterDataModel()
        self.cart = []
        
        frame_top = ttk.Frame(self)
        frame_top.pack(fill="x", padx=10)
        
        ttk.Label(frame_top, text="Pilih Pasien:").pack(side="left")
        self.cb_pasien = ttk.Combobox(frame_top, width=40, state="readonly")
        self.cb_pasien.pack(side="left", padx=5)
        self.cb_pasien.bind("<<ComboboxSelected>>", self.load_fisik)
        
        self.lbl_fisik = ttk.Label(self, text="Data Fisik: -", foreground="blue", font=("Arial", 10, "italic"))
        self.lbl_fisik.pack(padx=10, anchor="w", pady=5)
        
        frame_medis = ttk.LabelFrame(self, text="Input Medis", padding=10)
        frame_medis.pack(fill="both", expand=True, padx=10)
        
        ttk.Label(frame_medis, text="Diagnosa Dokter:").pack(anchor="w")
        self.entry_diag = ttk.Entry(frame_medis, width=60)
        self.entry_diag.pack(fill="x", pady=5)
        
        ttk.Label(frame_medis, text="Tindakan / Jasa:").pack(anchor="w")
        self.cb_tindakan = ttk.Combobox(frame_medis, state="readonly")
        self.cb_tindakan.pack(fill="x", pady=5)

        ttk.Label(frame_medis, text="Resep Obat:").pack(anchor="w")
        frame_obat = ttk.Frame(frame_medis)
        frame_obat.pack(fill="x", pady=5)
        
        self.cb_obat = ttk.Combobox(frame_obat, width=40, state="readonly")
        self.cb_obat.pack(side="left")
        
        ttk.Button(frame_obat, text="+ Tambah Obat", command=self.add_obat).pack(side="left", padx=5)
        
        self.tree_cart = ttk.Treeview(frame_medis, columns=("ID", "Nama", "Qty", "Subtotal"), show="headings", height=5)
        self.tree_cart.heading("Nama", text="Nama Obat")
        self.tree_cart.heading("Qty", text="Jml")
        self.tree_cart.heading("Subtotal", text="Subtotal")
        self.tree_cart.pack(fill="x")
        
        ttk.Button(self, text="SELESAI PEMERIKSAAN", command=self.simpan).pack(pady=10)
        self.refresh()

    def refresh(self):
        antrian = self.model.get_antrian(CURRENT_USER['IdAkun'])
        self.cb_pasien['values'] = [f"{x['NoReg']} | {x['Nama']} ({x['Status']})" for x in antrian]
        
        obat = self.master_model.get_all_obat()
        self.cb_obat['values'] = [f"{x['IdBarang']} | {x['NamaBarang']} | @{int(x['HargaSatuan'])}" for x in obat]
        
        tindakan = self.master_model.get_all_tindakan()
        self.cb_tindakan['values'] = [f"{x['NamaTindakan']} | Rp {int(x['Tarif'])}" for x in tindakan]

    def load_fisik(self, event):
        if not self.cb_pasien.get():
            return
            
        no_reg = self.cb_pasien.get().split(" | ")[0]
        data = self.model.get_data_fisik(no_reg)
        
        if data:
            info = f"TB: {data['TinggiBadan']} cm, BB: {data['BeratBadan']} kg, Suhu: {data['Suhu']} C, Tensi: {data['Tensi']}"
            self.lbl_fisik.config(text=info)
        else:
            self.lbl_fisik.config(text="Pasien ini belum diperiksa perawat.")

    def add_obat(self):
        val = self.cb_obat.get()
        if val:
            parts = val.split(" | ")
            harga = float(parts[2].replace("@", ""))
            
            self.cart.append({'id': parts[0], 'nama': parts[1], 'qty': 1, 'sub': harga})
            self.tree_cart.insert("", "end", values=(parts[0], parts[1], 1, int(harga)))

    def simpan(self):
        if not self.cb_pasien.get():
            return messagebox.showwarning("Warning", "Pilih Pasien")
        if not self.cb_tindakan.get():
            return messagebox.showwarning("Warning", "Pilih Tindakan")

        no_reg = self.cb_pasien.get().split(" | ")[0]
        str_tindakan = self.cb_tindakan.get()
        tarif = float(str_tindakan.split(" | Rp ")[1])
        nama_tindakan = str_tindakan.split(" | ")[0]
        
        diagnosa_full = f"{self.entry_diag.get()} (Tindakan: {nama_tindakan})"

        try:
            self.model.simpan_transaksi_medis(no_reg, diagnosa_full, tarif, self.cart)
            self.show_info("Pemeriksaan Selesai")
            
            self.cart = []
            self.entry_diag.delete(0, tk.END)
            self.cb_tindakan.set('')
            
            for item in self.tree_cart.get_children():
                self.tree_cart.delete(item)
                
            self.refresh()
        except Exception as e:
            self.show_error(str(e))

class FrameKasir(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Kasir - Pembayaran Pending")
        self.model = KasirModel()
        self.tree['columns'] = ("NoTagihan", "Total", "Status")
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            
        ttk.Button(self.btn_frame, text="PROSES PEMBAYARAN", command=self.bayar).pack(side="left", padx=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        data = self.model.get_tagihan_pending()
        for row in data:
            self.tree.insert("", "end", values=(row['NoTagihan'], int(row['GrandTotal']), row['StatusBayar']))

    def bayar(self):
        selected = self.tree.selection()
        if selected:
            no_tagihan = self.tree.item(selected[0])['values'][0]
            if messagebox.askyesno("Konfirmasi", f"Bayar lunas tagihan {no_tagihan}?"):
                self.model.bayar_tagihan(no_tagihan)
                self.show_info("Pembayaran Lunas!")
                self.load_data()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()