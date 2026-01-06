import tkinter as tk
from tkinter import ttk, messagebox
from models import AuthModel, MasterDataModel, PendaftaranModel, DokterModel, KasirModel, PerawatModel

CURRENT_USER = {"IdAkun": None, "Nama": None, "Role": None}

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistem Klinik")
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
            user = self.model.login(self.entry_user.get(), self.entry_pass.get())
            if user:
                CURRENT_USER["IdAkun"] = user["IdAkun"]
                CURRENT_USER["Nama"] = user["NamaLengkap"]
                CURRENT_USER["Role"] = user["Jobdesk"]
                self.show_info(f"Selamat Datang, {user['NamaLengkap']}")
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

        if role in ['Perawat', 'Admin']:
            nb.add(FramePerawat(nb), text="Pemeriksaan Fisik")

        if role in ['Dokter', 'Admin']:
            nb.add(FrameDokter(nb), text="Dokter & Resep")
            
        if role in ['Kasir', 'Admin']:
            nb.add(FrameKasir(nb), text="Kasir")

class BaseCRUD(BasePage):
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

    def load_data(self): pass

class FrameMasterPasien(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Data Pasien")
        self.tree['columns'] = ("ID", "Nama", "Gender", "Usia", "Alamat")
        for c in self.tree['columns']: self.tree.heading(c, text=c)

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.model.get_all_pasien():
            self.tree.insert("", "end", values=(r['IdPasien'], r['Nama'], r['Gender'], r['Usia'], r['Alamat']))

class FrameMasterObat(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Data Obat")
        self.tree['columns'] = ("ID", "Nama", "Stok", "Satuan", "Harga")
        for c in self.tree['columns']: self.tree.heading(c, text=c)

    def load_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for r in self.model.get_all_obat():
            self.tree.insert("", "end", values=(r['IdBarang'], r['NamaBarang'], r['Stok'], r['Satuan'], r['HargaSatuan']))

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
        win = tk.Toplevel(self)
        win.title("Pasien Baru")
        win.geometry("300x350")
        
        f = ttk.Frame(win, padding=10)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Nama:").pack(anchor="w"); e_nm = ttk.Entry(f); e_nm.pack(fill="x", pady=5)
        
        ttk.Label(f, text="Gender:").pack(anchor="w")
        cb_gender = ttk.Combobox(f, values=["L", "P"], state="readonly")
        cb_gender.pack(fill="x", pady=5)
        cb_gender.current(0)

        ttk.Label(f, text="Usia:").pack(anchor="w"); e_us = ttk.Entry(f); e_us.pack(fill="x", pady=5)
        ttk.Label(f, text="Alamat:").pack(anchor="w"); e_al = ttk.Entry(f); e_al.pack(fill="x", pady=5)
        
        def save():
            if not e_nm.get() or not e_us.get(): return
            try:
                self.master_model.tambah_pasien(e_nm.get(), e_al.get(), cb_gender.get(), e_us.get())
                self.refresh()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            
        ttk.Button(f, text="Simpan", command=save).pack(pady=10)

class FramePerawat(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = PerawatModel()
        
        f = ttk.LabelFrame(self, text="Input Tanda Vital", padding=10)
        f.pack(fill="x", padx=10)
        
        ttk.Label(f, text="Pilih Antrian:").grid(row=0, column=0)
        self.cb_antrian = ttk.Combobox(f, width=40, state="readonly")
        self.cb_antrian.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(f, text="TB (cm):").grid(row=1, column=0); self.e_tb = ttk.Entry(f); self.e_tb.grid(row=1, column=1)
        ttk.Label(f, text="BB (kg):").grid(row=1, column=2); self.e_bb = ttk.Entry(f); self.e_bb.grid(row=1, column=3)
        ttk.Label(f, text="Suhu (C):").grid(row=2, column=0); self.e_suhu = ttk.Entry(f); self.e_suhu.grid(row=2, column=1)
        ttk.Label(f, text="Tensi:").grid(row=2, column=2); self.e_tensi = ttk.Entry(f); self.e_tensi.grid(row=2, column=3)
        
        ttk.Button(f, text="SIMPAN", command=self.simpan).grid(row=3, column=1, pady=10)
        self.refresh()

    def refresh(self):
        self.cb_antrian.set('')
        for e in [self.e_tb, self.e_bb, self.e_suhu, self.e_tensi]: e.delete(0, tk.END)
        try:
            antrian = self.model.get_antrian_perawat()
            self.cb_antrian['values'] = [f"{x['NoReg']} | {x['Nama']}" for x in antrian]
        except Exception as e:
            self.show_error(str(e))

    def simpan(self):
        if not self.cb_antrian.get(): return
        no_reg = self.cb_antrian.get().split(" | ")[0]
        try:
            self.model.simpan_pemeriksaan(no_reg, CURRENT_USER['IdAkun'], self.e_tb.get(), self.e_bb.get(), self.e_suhu.get(), self.e_tensi.get())
            self.show_info("Disimpan")
            self.refresh()
        except Exception as e:
            self.show_error(str(e))

class FrameDokter(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = DokterModel()
        self.master_model = MasterDataModel()
        self.cart = []
        
        f = ttk.Frame(self); f.pack(fill="x", padx=10)
        ttk.Label(f, text="Pasien:").pack(side="left")
        self.cb_pasien = ttk.Combobox(f, width=40, state="readonly")
        self.cb_pasien.pack(side="left", padx=5)
        self.cb_pasien.bind("<<ComboboxSelected>>", self.load_fisik)
        
        self.lbl_fisik = ttk.Label(self, text="Fisik: -", foreground="blue")
        self.lbl_fisik.pack(padx=10, anchor="w")
        
        f2 = ttk.LabelFrame(self, text="Resep & Tindakan", padding=10)
        f2.pack(fill="both", expand=True, padx=10)
        
        ttk.Label(f2, text="Diagnosa:").pack(anchor="w")
        self.e_diag = ttk.Entry(f2, width=50); self.e_diag.pack(fill="x")
        
        f_obat = ttk.Frame(f2); f_obat.pack(fill="x", pady=5)
        self.cb_obat = ttk.Combobox(f_obat, width=30, state="readonly"); self.cb_obat.pack(side="left")
        ttk.Button(f_obat, text="+ Obat", command=self.add_obat).pack(side="left", padx=5)
        
        self.tree_cart = ttk.Treeview(f2, columns=("ID", "Nama", "Qty"), show="headings", height=5)
        self.tree_cart.heading("Nama", text="List Obat"); self.tree_cart.pack(fill="x")
        
        ttk.Button(self, text="SELESAI & SIMPAN", command=self.simpan).pack(pady=10)
        self.refresh()

    def refresh(self):
        antrian = self.model.get_antrian(CURRENT_USER['IdAkun'])
        self.cb_pasien['values'] = [f"{x['NoReg']} | {x['Nama']} ({x['Status']})" for x in antrian]
        obat = self.master_model.get_all_obat()
        self.cb_obat['values'] = [f"{x['IdBarang']} | {x['NamaBarang']} | @{int(x['HargaSatuan'])}" for x in obat]

    def load_fisik(self, event):
        if not self.cb_pasien.get(): return
        no = self.cb_pasien.get().split(" | ")[0]
        d = self.model.get_data_fisik(no)
        if d: self.lbl_fisik.config(text=f"Tensi: {d['Tensi']}, Suhu: {d['Suhu']}, BB: {d['BeratBadan']}")
        else: self.lbl_fisik.config(text="Belum diperiksa perawat")

    def add_obat(self):
        val = self.cb_obat.get()
        if val:
            parts = val.split(" | ")
            self.cart.append({'id': parts[0], 'nama': parts[1], 'qty': 1, 'sub': float(parts[2].replace("@", ""))})
            self.tree_cart.insert("", "end", values=(parts[0], parts[1], 1))

    def simpan(self):
        if not self.cb_pasien.get(): return
        no = self.cb_pasien.get().split(" | ")[0]
        try:
            self.model.simpan_transaksi_medis(no, self.e_diag.get(), 50000, self.cart)
            self.show_info("Selesai")
            self.cart = []; self.e_diag.delete(0, tk.END)
            for i in self.tree_cart.get_children(): self.tree_cart.delete(i)
            self.refresh()
        except Exception as e:
            self.show_error(str(e))

class FrameKasir(BaseCRUD):
    def __init__(self, parent):
        super().__init__(parent, "Kasir - Pending Payment")
        self.model = KasirModel()
        self.tree['columns'] = ("NoTagihan", "Total", "Status")
        for c in self.tree['columns']: self.tree.heading(c, text=c)
        ttk.Button(self, text="BAYAR LUNAS", command=self.bayar).pack(pady=5)

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