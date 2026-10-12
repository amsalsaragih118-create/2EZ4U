import time
import tkinter as tk
from tkinter import ttk

from backend.m1_pesanan import (
    ManajerPesanan, OID, PELANGGAN, RESTO, MENU, HARGA, PRIORITAS, T_MASUK, T_SELESAI, STATUS,
    JENIS_VIP, JENIS_PRIORITAS, JENIS_REGULER,
)
from backend.m2_antrean import LayananAntrean, mesin_kasir
from backend.m3_laporan import LaporanHarian, BATAS_INSERTION


def fmt_int(n):
    s = str(n)
    negatif = s.startswith("-")
    if negatif:
        s = s[1:]
    hasil = ""
    hitung = 0
    i = len(s) - 1
    while i >= 0:
        if hitung == 3:
            hasil = "." + hasil
            hitung = 0
        hasil = s[i] + hasil
        hitung += 1
        i -= 1
    if negatif:
        hasil = "-" + hasil
    return hasil


def fmt_waktu(detik):
    ms = detik * 1000.0
    if ms >= 1000.0:
        return ("%.2f s" % (ms / 1000.0)).replace(".", ",")
    return ("%.2f ms" % ms).replace(".", ",")


def fmt_jam(detik):
    if detik is None:
        return "-"
    j = detik // 3600
    m = (detik % 3600) // 60
    s = detik % 60
    return "%02d:%02d:%02d" % (j % 24, m, s)


def fmt_rp(nilai):
    if isinstance(nilai, float) and nilai != int(nilai):
        return "Rp " + ("%.2f" % nilai).replace(".", ",")
    return "Rp " + fmt_int(int(nilai))


def baris_detail(p):
    return [
        ("oid", p[OID]),
        ("pelanggan", p[PELANGGAN]),
        ("resto", p[RESTO]),
        ("menu", p[MENU]),
        ("harga", fmt_int(p[HARGA])),
        ("prioritas", str(p[PRIORITAS])),
        ("masuk", fmt_jam(p[T_MASUK])),
        ("selesai", fmt_jam(p[T_SELESAI])),
        ("status", p[STATUS]),
    ]


def baris_pesanan(daftar, batas=200):
    jumlah = len(daftar)
    if jumlah > batas:
        jumlah = batas
    hasil = []
    for i in range(jumlah):
        p = daftar[i]
        hasil.append((str(i + 1), p[OID], p[PELANGGAN], p[RESTO], p[MENU]))
    return hasil


KOLOM_PESANAN = ("#", "oid", "pelanggan", "resto", "menu")
KOLOM_DETAIL = ("kolom", "isi")
KOLOM_URUT = ("#", "oid", "harga", "selesai", "resto", "menu")
KOLOM_LANGKAH = ("langkah", "token", "tindakan", "stack", "output")


def bangun_menu():
    daftar = []
    daftar.append(("H", "DATA"))
    daftar.append(("load", "Load", "Muat data pesanan", "Membaca data/pesanan.csv ke array dan linked list, lalu mengisi antrean dari pesanan berstatus ANTRE.", ()))
    daftar.append(("H", "M1 - DATA PESANAN"))
    nama_struktur = (("array", "ARRAY", "Array"), ("linked", "LINKEDLIST", "Linked list"))
    for kode, huruf, judul in nama_struktur:
        daftar.append((kode + "_lihat", huruf + " - LIHAT PESANAN", judul + ": lihat pesanan ke-i", "Membuka detail satu pesanan berdasarkan nomor urut.", (("urutan", "Urutan pesanan (mulai 1)", "1", None),)))
        daftar.append((kode + "_reguler", huruf + " - TAMBAH PESANAN REGULER", judul + ": pesanan REGULER, masuk paling belakang", "Pesanan reguler ditempatkan di ujung belakang barisan.", (("nama", "Nama pelanggan", "Pelanggan Baru", None),)))
        daftar.append((kode + "_prioritas", huruf + " - TAMBAH PESANAN PRIORITAS", judul + ": pesanan PRIORITAS, masuk ke tengah", "Pesanan prioritas disisipkan di tengah barisan.", (("nama", "Nama pelanggan", "Pelanggan Baru", None),)))
        daftar.append((kode + "_vip", huruf + " - TAMBAH PESANAN VIP", judul + ": pesanan VIP, masuk paling depan", "Pesanan VIP ditempatkan di urutan pertama.", (("nama", "Nama pelanggan", "Pelanggan Baru", None),)))
        daftar.append((kode + "_hapus", huruf + " - HAPUS PESANAN", judul + ": hapus pesanan ke-i", "Mencabut satu pesanan dari barisan.", (("urutan", "Urutan pesanan (mulai 1)", "1", None),)))
    daftar.append(("H", "M2 - STACK DAN QUEUE"))
    daftar.append(("postfix", "STACK - POSTFIX (MESIN KASIR)", "Stack: hitung struk lewat postfix", "Tahap 1 mengubah infix menjadi postfix, tahap 2 mengevaluasi postfix. Keduanya memakai stack.", (("ekspresi", "Struk belanja (infix)", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000", None),)))
    daftar.append(("undo", "STACK - UNDO", "Stack: batalkan aksi antrean terakhir", "Mengambil catatan teratas tumpukan undo lalu menjalankan kebalikannya.", ()))
    daftar.append(("redo", "STACK - REDO", "Stack: kerjakan lagi aksi yang dibatalkan", "Mengambil catatan teratas tumpukan redo lalu mengerjakan ulang aksi aslinya.", ()))
    daftar.append(("enqueue", "QUEUE - ENQUEUE", "Queue: pesanan baru masuk ke belakang", "Menambah pesanan di ujung belakang kedua antrean sekaligus.", (("nama", "Nama pelanggan", "Pelanggan Baru", None),)))
    daftar.append(("dequeue_naif", "QUEUE - DEQUEUE NAIF", "Queue naif: ambil dari depan dengan menggeser isi", "Setiap dequeue menggeser seluruh sisa isi satu petak ke kiri, O(n).", (("jumlah", "Berapa kali dequeue", "1", None),)))
    daftar.append(("dequeue_circular", "QUEUE - DEQUEUE CIRCULAR", "Queue circular: ambil dari depan dengan memajukan penunjuk", "Hanya penunjuk front yang maju, tidak ada elemen yang digeser, O(1).", (("jumlah", "Berapa kali dequeue", "1", None),)))
    daftar.append(("H", "M3 - SORT DAN SEARCH"))
    daftar.append(("insertion", "SORT - INSERTION SORT", "Sort: insertion sort, O(n^2)", "Batas jumlah baris %s. Menampilkan 100 baris pertama hasil." % fmt_int(BATAS_INSERTION), (("jumlah", "Jumlah baris diurutkan", "2000", None), ("kunci", "Diurutkan menurut", "harga", ("oid", "harga", "selesai")))))
    daftar.append(("merge", "SORT - MERGE SORT", "Sort: merge sort, O(n log n)", "Mampu mengurutkan seluruh data. Menampilkan 100 baris pertama hasil.", (("jumlah", "Jumlah baris diurutkan", "4000", None), ("kunci", "Diurutkan menurut", "oid", ("oid", "harga", "selesai")))))
    daftar.append(("linear", "SEARCH - LINEAR SEARCH", "Search: linear search, O(n)", "Memeriksa pesanan satu per satu dari depan. Tidak menuntut data terurut.", (("oid", "Nomor pesanan (oid)", "O-137442", None),)))
    daftar.append(("binary", "SEARCH - BINARY SEARCH", "Search: binary search, O(log n)", "Membuang separuh sisa daftar pada setiap perbandingan. Menuntut daftar terurut menurut oid.", (("oid", "Nomor pesanan (oid)", "O-137442", None),)))
    return daftar


class Aplikasi:
    def __init__(self, root, path_data):
        self.root = root
        self.path_data = path_data
        self.manajer = ManajerPesanan()
        self.layanan = None
        self.laporan = None
        self.daftar_menu = bangun_menu()
        self.menu_aktif = None
        self.widget_isian = []
        self.nama_isian = []
        self.susun_tampilan()
        self.tampilkan_menu(self.daftar_menu[1])

    def susun_tampilan(self):
        self.root.title("2EZ4U Food Delivery")
        self.root.geometry("1200x740")
        judul = tk.Label(self.root, text="2EZ4U Food Delivery", bg="#2b3a55", fg="white", font=("Helvetica", 14, "bold"), anchor="w", padx=12, pady=8)
        judul.pack(fill="x")
        utama = tk.Frame(self.root)
        utama.pack(fill="both", expand=True)

        kiri = tk.Frame(utama, width=300)
        kiri.pack(side="left", fill="y")
        kiri.pack_propagate(False)
        self.daftar = tk.Listbox(kiri, activestyle="none", exportselection=False, font=("Helvetica", 10))
        gulir_kiri = tk.Scrollbar(kiri, command=self.daftar.yview)
        self.daftar.config(yscrollcommand=gulir_kiri.set)
        gulir_kiri.pack(side="right", fill="y")
        self.daftar.pack(side="left", fill="both", expand=True)
        for entri in self.daftar_menu:
            if len(entri) == 2:
                self.daftar.insert("end", entri[1])
                self.daftar.itemconfig("end", foreground="#2b3a55", background="#e6e9f0")
            else:
                self.daftar.insert("end", "  " + entri[1])
        self.daftar.bind("<<ListboxSelect>>", self.saat_pilih)

        kanan = tk.Frame(utama, padx=12, pady=8)
        kanan.pack(side="left", fill="both", expand=True)
        self.label_judul = tk.Label(kanan, text="", font=("Helvetica", 12, "bold"), anchor="w")
        self.label_judul.pack(fill="x")
        self.label_desk = tk.Label(kanan, text="", fg="#555555", anchor="w", justify="left", wraplength=800)
        self.label_desk.pack(fill="x", pady=(0, 6))
        self.bingkai_form = tk.Frame(kanan)
        self.bingkai_form.pack(fill="x")
        self.label_ringkasan = tk.Label(kanan, text="", anchor="w", justify="left", wraplength=850, font=("Courier", 10))
        self.label_ringkasan.pack(fill="x", pady=8)

        bingkai_tabel = tk.Frame(kanan)
        bingkai_tabel.pack(fill="both", expand=True)
        self.tabel = ttk.Treeview(bingkai_tabel, show="headings")
        gulir_y = tk.Scrollbar(bingkai_tabel, orient="vertical", command=self.tabel.yview)
        gulir_x = tk.Scrollbar(bingkai_tabel, orient="horizontal", command=self.tabel.xview)
        self.tabel.config(yscrollcommand=gulir_y.set, xscrollcommand=gulir_x.set)
        gulir_y.pack(side="right", fill="y")
        gulir_x.pack(side="bottom", fill="x")
        self.tabel.pack(side="left", fill="both", expand=True)

        tk.Label(kanan, text="COMMAND", anchor="w", font=("Helvetica", 9, "bold")).pack(fill="x", pady=(8, 0))
        bingkai_log = tk.Frame(kanan)
        bingkai_log.pack(fill="x")
        self.log = tk.Text(bingkai_log, height=6, font=("Courier", 9), state="disabled")
        gulir_log = tk.Scrollbar(bingkai_log, command=self.log.yview)
        self.log.config(yscrollcommand=gulir_log.set)
        gulir_log.pack(side="right", fill="y")
        self.log.pack(side="left", fill="x", expand=True)

        self.status = tk.Label(self.root, text="siap", bg="#2b3a55", fg="white", anchor="w", padx=10)
        self.status.pack(fill="x", side="bottom")

    def saat_pilih(self, event):
        pilihan = self.daftar.curselection()
        if len(pilihan) == 0:
            return
        entri = self.daftar_menu[pilihan[0]]
        if len(entri) == 2:
            return
        self.tampilkan_menu(entri)

    def tampilkan_menu(self, entri):
        self.menu_aktif = entri
        self.label_judul.config(text=entri[2])
        self.label_desk.config(text=entri[3])
        self.label_ringkasan.config(text="")
        for anak in self.bingkai_form.winfo_children():
            anak.destroy()
        self.widget_isian = []
        self.nama_isian = []
        for nama, label, default, opsi in entri[4]:
            tk.Label(self.bingkai_form, text=label, anchor="w").pack(anchor="w")
            variabel = tk.StringVar(value=default)
            if opsi is None:
                widget = tk.Entry(self.bingkai_form, width=48, textvariable=variabel)
            else:
                widget = ttk.Combobox(self.bingkai_form, values=opsi, state="readonly", width=20, textvariable=variabel)
            widget.pack(anchor="w", pady=(0, 6))
            self.widget_isian.append(variabel)
            self.nama_isian.append(nama)
        tk.Button(self.bingkai_form, text="JALANKAN", command=self.jalankan, bg="#2b3a55", fg="white", padx=16).pack(anchor="w", pady=4)
        self.atur_tabel(KOLOM_DETAIL, [])

    def atur_tabel(self, kolom, baris):
        self.tabel.delete(*self.tabel.get_children())
        self.tabel.config(columns=kolom)
        for k in kolom:
            lebar = 110
            if k == "tindakan":
                lebar = 330
            elif k in ("pelanggan", "resto", "menu", "isi", "stack", "output"):
                lebar = 200
            elif k == "#":
                lebar = 60
            self.tabel.heading(k, text=k)
            self.tabel.column(k, width=lebar, anchor="w")
        for b in baris:
            self.tabel.insert("", "end", values=b)

    def ambil(self, nama):
        for i in range(len(self.nama_isian)):
            if self.nama_isian[i] == nama:
                return self.widget_isian[i].get().strip()
        return ""

    def ambil_int(self, nama, label):
        teks = self.ambil(nama).replace(".", "")
        try:
            nilai = int(teks)
        except ValueError:
            raise ValueError(label + " harus berupa bilangan bulat")
        if nilai < 1:
            raise ValueError(label + " harus lebih dari 0")
        return nilai

    def butuh_data(self):
        if not self.manajer.dimuat:
            raise ValueError("Data belum dimuat, jalankan menu Load terlebih dahulu")

    def hook_batal(self, pesanan, struktur):
        self.manajer.hapus_oid(struktur, pesanan[OID])

    def hook_ulang(self, pesanan, jenis, struktur):
        self.manajer.tambah(struktur, jenis, pesanan)

    def jalankan(self):
        entri = self.menu_aktif
        kunci = entri[0]
        try:
            hasil = self.eksekusi(kunci)
        except Exception as galat:
            self.label_ringkasan.config(text="GALAT: " + str(galat))
            self.atur_tabel(KOLOM_DETAIL, [])
            self.catat_log(kunci, "-", "galat")
            self.status.config(text="[%s] galat" % kunci)
            return
        modul, ringkasan, kolom, baris, durasi = hasil
        self.label_ringkasan.config(text=ringkasan)
        self.atur_tabel(kolom, baris)
        self.catat_log(kunci, modul, fmt_waktu(durasi))
        self.status.config(text="[%s] %s" % (modul, fmt_waktu(durasi)))

    def catat_log(self, perintah, modul, waktu):
        self.log.config(state="normal")
        self.log.insert("1.0", "%-18s -> %-22s %s\n" % (perintah, modul, waktu))
        self.log.config(state="disabled")

    def eksekusi(self, kunci):
        if kunci == "load":
            return self.h_load()
        if kunci.startswith("array_") or kunci.startswith("linked_"):
            return self.h_m1(kunci)
        if kunci == "postfix":
            return self.h_postfix()
        if kunci == "undo":
            return self.h_undo()
        if kunci == "redo":
            return self.h_redo()
        if kunci == "enqueue":
            return self.h_enqueue()
        if kunci == "dequeue_naif":
            return self.h_dequeue("NAIF")
        if kunci == "dequeue_circular":
            return self.h_dequeue("CIRCULAR")
        if kunci == "insertion":
            return self.h_sort("insertion")
        if kunci == "merge":
            return self.h_sort("merge")
        if kunci == "linear":
            return self.h_linear()
        if kunci == "binary":
            return self.h_binary()
        raise ValueError("menu tidak dikenal")

    def h_load(self):
        mulai = time.perf_counter()
        self.manajer.muat(self.path_data)
        self.layanan = LayananAntrean(self.hook_batal, self.hook_ulang)
        self.layanan.isi_awal(self.manajer.data_awal)
        self.laporan = LaporanHarian(self.manajer.data_awal)
        durasi = time.perf_counter() - mulai
        stat = self.layanan.stats()
        ringkasan = "%s baris dimuat ke array dan linked list.\nPesanan berstatus ANTRE: %s" % (fmt_int(self.manajer.data_awal.size), fmt_int(stat[0][1]))
        baris = [("jumlah_baris", fmt_int(self.manajer.data_awal.size))]
        for nama, nilai in stat:
            baris.append((nama, fmt_int(nilai)))
        return ("M1 - load", ringkasan, KOLOM_DETAIL, baris, durasi)

    def h_m1(self, kunci):
        self.butuh_data()
        bagian = kunci.split("_")
        struktur = bagian[0]
        aksi = bagian[1]
        if struktur == "array":
            nama_struktur = "array"
            satuan = "elemen digeser"
        else:
            nama_struktur = "linked list"
            satuan = "simpul ditelusuri"
        modul = "M1 - " + struktur
        s = self.manajer.struktur(struktur)
        if aksi == "lihat":
            i = self.ambil_int("urutan", "Urutan") - 1
            mulai = time.perf_counter()
            p = self.manajer.lihat(struktur, i)
            durasi = time.perf_counter() - mulai
            ringkasan = "Pesanan ke-%s dari %s berisi %s pesanan." % (fmt_int(i + 1), nama_struktur, fmt_int(s.size))
            return (modul, ringkasan, KOLOM_DETAIL, baris_detail(p), durasi)
        if aksi == "hapus":
            i = self.ambil_int("urutan", "Urutan") - 1
            sebelum = self.manajer.penghitung(struktur)
            mulai = time.perf_counter()
            p = self.manajer.hapus(struktur, i)
            durasi = time.perf_counter() - mulai
            kerja = self.manajer.penghitung(struktur) - sebelum
            ringkasan = "Pesanan %s dicabut dari urutan %s.\n%s: %s | panjang sekarang %s" % (p[OID], fmt_int(i + 1), satuan, fmt_int(kerja), fmt_int(s.size))
            return (modul, ringkasan, KOLOM_DETAIL, baris_detail(p), durasi)
        if aksi == "reguler":
            jenis = JENIS_REGULER
        elif aksi == "prioritas":
            jenis = JENIS_PRIORITAS
        else:
            jenis = JENIS_VIP
        nama = self.ambil("nama")
        if nama == "":
            raise ValueError("Nama pelanggan tidak boleh kosong")
        p = self.manajer.pesanan_baru(nama, jenis)
        sebelum = self.manajer.penghitung(struktur)
        mulai = time.perf_counter()
        posisi = self.manajer.tambah(struktur, jenis, p)
        durasi = time.perf_counter() - mulai
        kerja = self.manajer.penghitung(struktur) - sebelum
        if self.layanan is not None:
            self.layanan.catat_order(p, jenis, struktur)
        ringkasan = "Pesanan %s disisipkan pada urutan %s dari %s.\n%s: %s" % (p[OID], fmt_int(posisi + 1), fmt_int(s.size), satuan, fmt_int(kerja))
        return (modul, ringkasan, KOLOM_DETAIL, baris_detail(p), durasi)

    def h_postfix(self):
        ekspresi = self.ambil("ekspresi")
        if ekspresi == "":
            raise ValueError("Struk belanja tidak boleh kosong")
        mulai = time.perf_counter()
        hasil = mesin_kasir(ekspresi)
        durasi = time.perf_counter() - mulai
        ringkasan = "Struk : %s\nPostfix: %s\nTOTAL : %s" % (ekspresi, hasil.postfix_teks, fmt_rp(hasil.total))
        return ("M2 - stack", ringkasan, KOLOM_LANGKAH, hasil.langkah, durasi)

    def info_antrean(self):
        stat = self.layanan.stats()
        return "Panjang antrean sekarang: naif %s, circular %s. Tumpukan undo %s, redo %s." % (fmt_int(stat[0][1]), fmt_int(stat[1][1]), fmt_int(stat[5][1]), fmt_int(stat[6][1]))

    def pesanan_dari_aksi(self, aksi):
        if aksi[0] == "DEQUEUE":
            return aksi[2]
        return [aksi[1]]

    def h_undo(self):
        self.butuh_data()
        mulai = time.perf_counter()
        aksi = self.layanan.undo_last()
        durasi = time.perf_counter() - mulai
        if aksi is None:
            return ("M2 - stack", "Tumpukan undo kosong, tidak ada yang dibatalkan.\n" + self.info_antrean(), KOLOM_PESANAN, [], durasi)
        if aksi[0] == "ENQUEUE":
            teks = "Pembatalan enqueue: %s dikeluarkan lagi dari belakang." % aksi[1][OID]
        elif aksi[0] == "DEQUEUE":
            teks = "Pembatalan dequeue: %s pesanan dikembalikan ke DEPAN antrean %s." % (fmt_int(len(aksi[2])), aksi[1].lower())
        else:
            teks = "Pembatalan penambahan pesanan: %s dihapus dari %s." % (aksi[1][OID], aksi[3])
        return ("M2 - stack", teks + "\n" + self.info_antrean(), KOLOM_PESANAN, baris_pesanan(self.pesanan_dari_aksi(aksi)), durasi)

    def h_redo(self):
        self.butuh_data()
        mulai = time.perf_counter()
        aksi = self.layanan.redo_last()
        durasi = time.perf_counter() - mulai
        if aksi is None:
            return ("M2 - stack", "Tumpukan redo kosong, tidak ada yang diulang.\n" + self.info_antrean(), KOLOM_PESANAN, [], durasi)
        if aksi[0] == "ENQUEUE":
            teks = "Enqueue dikerjakan lagi: %s masuk kembali ke belakang." % aksi[1][OID]
        elif aksi[0] == "DEQUEUE":
            teks = "Dequeue dikerjakan lagi: %s pesanan keluar dari antrean %s." % (fmt_int(len(aksi[2])), aksi[1].lower())
        else:
            teks = "Penambahan pesanan dikerjakan lagi: %s masuk ke %s." % (aksi[1][OID], aksi[3])
        return ("M2 - stack", teks + "\n" + self.info_antrean(), KOLOM_PESANAN, baris_pesanan(self.pesanan_dari_aksi(aksi)), durasi)

    def h_enqueue(self):
        self.butuh_data()
        nama = self.ambil("nama")
        if nama == "":
            raise ValueError("Nama pelanggan tidak boleh kosong")
        p = self.manajer.pesanan_baru(nama, JENIS_REGULER)
        mulai = time.perf_counter()
        self.layanan.enqueue(p)
        durasi = time.perf_counter() - mulai
        ringkasan = "%s masuk ke barisan paling belakang pada KEDUA antrean.\n%s" % (p[OID], self.info_antrean())
        return ("M2 - queue", ringkasan, KOLOM_DETAIL, baris_detail(p), durasi)

    def h_dequeue(self, varian):
        self.butuh_data()
        n = self.ambil_int("jumlah", "Jumlah dequeue")
        mulai = time.perf_counter()
        if varian == "NAIF":
            daftar, geser = self.layanan.dequeue_naif(n)
            modul = "M2 - queue naif"
        else:
            daftar, geser = self.layanan.dequeue_circular(n)
            modul = "M2 - queue circular"
        durasi = time.perf_counter() - mulai
        ringkasan = "%s pesanan keluar dari depan antrean | %s elemen digeser\n%s" % (fmt_int(len(daftar)), fmt_int(geser), self.info_antrean())
        return (modul, ringkasan, KOLOM_PESANAN, baris_pesanan(daftar), durasi)

    def baris_urut(self, data):
        jumlah = len(data)
        if jumlah > 100:
            jumlah = 100
        baris = []
        for i in range(jumlah):
            p = data[i]
            baris.append((str(i + 1), p[OID], fmt_int(p[HARGA]), fmt_jam(p[T_SELESAI]), p[RESTO], p[MENU]))
        return baris

    def h_sort(self, algoritma):
        self.butuh_data()
        n = self.ambil_int("jumlah", "Jumlah baris")
        kunci = self.ambil("kunci")
        if algoritma == "insertion":
            hasil = self.laporan.urut_insertion(n, kunci)
            modul = "M3 - insertion sort"
        else:
            hasil = self.laporan.urut_merge(n, kunci)
            modul = "M3 - merge sort"
        ringkasan = "%s pesanan terurut menurut %s | %s perbandingan, %s pemindahan" % (fmt_int(len(hasil.data)), kunci, fmt_int(hasil.perbandingan), fmt_int(hasil.pemindahan))
        return (modul, ringkasan, KOLOM_URUT, self.baris_urut(hasil.data), hasil.durasi)

    def h_linear(self):
        self.butuh_data()
        oid = self.ambil("oid")
        hasil = self.laporan.cari_linear(oid)
        if hasil.indeks < 0:
            ringkasan = "%s tidak ditemukan | %s perbandingan" % (oid, fmt_int(hasil.perbandingan))
            return ("M3 - linear search", ringkasan, KOLOM_DETAIL, [], hasil.durasi)
        ringkasan = "Ditemukan pada indeks %s | %s perbandingan" % (fmt_int(hasil.indeks), fmt_int(hasil.perbandingan))
        return ("M3 - linear search", ringkasan, KOLOM_DETAIL, baris_detail(hasil.pesanan), hasil.durasi)

    def h_binary(self):
        self.butuh_data()
        oid = self.ambil("oid")
        hasil = self.laporan.cari_binary(oid)
        if hasil.baru_dibangun:
            baris_bangun = "Daftar terurut oid dibangun sekali dengan merge sort: %s." % fmt_waktu(hasil.ongkos_bangun)
        else:
            baris_bangun = "Daftar terurut oid sudah tersedia dari pencarian sebelumnya."
        if hasil.indeks < 0:
            ringkasan = "%s\n%s tidak ditemukan | %s perbandingan" % (baris_bangun, oid, fmt_int(hasil.perbandingan))
            return ("M3 - binary search", ringkasan, KOLOM_DETAIL, [], hasil.durasi)
        ringkasan = "%s\nDitemukan pada baris ke-%s | %s perbandingan" % (baris_bangun, fmt_int(hasil.indeks + 1), fmt_int(hasil.perbandingan))
        return ("M3 - binary search", ringkasan, KOLOM_DETAIL, baris_detail(hasil.pesanan), hasil.durasi)
