import csv

OID = 0
PELANGGAN = 1
RESTO = 2
MENU = 3
HARGA = 4
PRIORITAS = 5
T_MASUK = 6
T_SELESAI = 7
STATUS = 8

JENIS_VIP = 1
JENIS_PRIORITAS = 2
JENIS_REGULER = 3


def buat_pesanan(oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status):
    return (oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status)


def ke_int_atau_none(teks):
    teks = teks.strip()
    if teks == "":
        return None
    return int(teks)


def nomor_dari_oid(oid):
    return int(oid[2:])


class Array:
    def __init__(self, kapasitas=4):
        if kapasitas < 1:
            kapasitas = 1
        self.kapasitas = kapasitas
        self.data = [None] * kapasitas
        self.size = 0
        self.jumlah_salin = 0
        self.jumlah_geser = 0

    def __len__(self):
        return self.size

    def __getitem__(self, i):
        return self.get(i)

    def __setitem__(self, i, v):
        self.ubah(i, v)

    def tumbuh(self):
        baru = [None] * (self.kapasitas * 2)
        for i in range(self.size):
            baru[i] = self.data[i]
        self.jumlah_salin += self.size
        self.data = baru
        self.kapasitas = self.kapasitas * 2

    def append(self, v):
        if self.size == self.kapasitas:
            self.tumbuh()
        self.data[self.size] = v
        self.size += 1

    def insert(self, i, v):
        if i < 0 or i > self.size:
            raise IndexError("posisi sisip di luar jangkauan")
        if self.size == self.kapasitas:
            self.tumbuh()
        j = self.size
        while j > i:
            self.data[j] = self.data[j - 1]
            j -= 1
        self.jumlah_geser += self.size - i
        self.data[i] = v
        self.size += 1

    def get(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("indeks di luar jangkauan")
        return self.data[i]

    def ubah(self, i, v):
        if i < 0 or i >= self.size:
            raise IndexError("indeks di luar jangkauan")
        self.data[i] = v

    def hapus(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("indeks di luar jangkauan")
        nilai = self.data[i]
        j = i
        while j < self.size - 1:
            self.data[j] = self.data[j + 1]
            j += 1
        self.jumlah_geser += self.size - 1 - i
        self.data[self.size - 1] = None
        self.size -= 1
        return nilai

    def panjang(self):
        return self.size

    def ke_list(self):
        hasil = [None] * self.size
        for i in range(self.size):
            hasil[i] = self.data[i]
        return hasil


class Simpul:
    def __init__(self, nilai):
        self.nilai = nilai
        self.next = None


class LinkList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
        self.jumlah_telusur = 0

    def append(self, v):
        simpul = Simpul(v)
        if self.head is None:
            self.head = simpul
            self.tail = simpul
        else:
            self.tail.next = simpul
            self.tail = simpul
        self.size += 1

    def tambah_depan(self, v):
        simpul = Simpul(v)
        simpul.next = self.head
        self.head = simpul
        if self.tail is None:
            self.tail = simpul
        self.size += 1

    def simpul_ke(self, i):
        sekarang = self.head
        for _ in range(i):
            sekarang = sekarang.next
        self.jumlah_telusur += i
        return sekarang

    def insert(self, i, v):
        if i < 0 or i > self.size:
            raise IndexError("posisi sisip di luar jangkauan")
        if i == 0:
            self.tambah_depan(v)
            return
        if i == self.size:
            self.append(v)
            return
        sebelum = self.simpul_ke(i - 1)
        simpul = Simpul(v)
        simpul.next = sebelum.next
        sebelum.next = simpul
        self.size += 1

    def get(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("indeks di luar jangkauan")
        return self.simpul_ke(i).nilai

    def hapus(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("indeks di luar jangkauan")
        if i == 0:
            nilai = self.head.nilai
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self.size -= 1
            return nilai
        sebelum = self.simpul_ke(i - 1)
        target = sebelum.next
        sebelum.next = target.next
        if target is self.tail:
            self.tail = sebelum
        self.size -= 1
        return target.nilai

    def panjang(self):
        return self.size

    def ke_list(self):
        hasil = [None] * self.size
        sekarang = self.head
        i = 0
        while sekarang is not None:
            hasil[i] = sekarang.nilai
            sekarang = sekarang.next
            i += 1
        return hasil


def baca_csv(path):
    hasil = Array(1024)
    with open(path, newline="", encoding="utf-8") as berkas:
        pembaca = csv.reader(berkas)
        for baris in pembaca:
            if len(baris) < 9:
                continue
            if baris[0].strip() == "oid":
                continue
            hasil.append(
                buat_pesanan(
                    baris[0].strip(),
                    baris[1],
                    baris[2],
                    baris[3],
                    int(baris[4]),
                    int(baris[5]),
                    ke_int_atau_none(baris[6]),
                    ke_int_atau_none(baris[7]),
                    baris[8].strip(),
                )
            )
    return hasil


def posisi_sisip(jenis, n):
    if jenis == JENIS_VIP:
        return 0
    if jenis == JENIS_PRIORITAS:
        return n // 2
    return n


class ManajerPesanan:
    def __init__(self):
        self.data_awal = Array()
        self.array = Array()
        self.linked = LinkList()
        self.nomor_berikut = 1
        self.dimuat = False

    def muat(self, path):
        data = baca_csv(path)
        self.data_awal = data
        self.array = Array(1024)
        self.linked = LinkList()
        nomor_maks = 0
        for i in range(data.size):
            p = data.get(i)
            self.array.append(p)
            self.linked.append(p)
            nomor = nomor_dari_oid(p[OID])
            if nomor > nomor_maks:
                nomor_maks = nomor
        self.nomor_berikut = nomor_maks + 1
        self.dimuat = True

    def struktur(self, nama):
        if nama == "array":
            return self.array
        if nama == "linked":
            return self.linked
        raise ValueError("struktur tidak dikenal")

    def pesanan_baru(self, pelanggan, prioritas, resto="kafe-teknik", menu="roti-bakar", harga=12000, t_masuk=28800):
        oid = "O-%06d" % self.nomor_berikut
        self.nomor_berikut += 1
        return buat_pesanan(oid, pelanggan, resto, menu, harga, prioritas, t_masuk, None, "ANTRE")

    def lihat(self, nama, i):
        return self.struktur(nama).get(i)

    def tambah(self, nama, jenis, pesanan):
        s = self.struktur(nama)
        posisi = posisi_sisip(jenis, s.size)
        s.insert(posisi, pesanan)
        return posisi

    def hapus(self, nama, i):
        return self.struktur(nama).hapus(i)

    def cari_indeks_oid(self, nama, oid):
        s = self.struktur(nama)
        if nama == "array":
            for i in range(s.size):
                if s.data[i][OID] == oid:
                    return i
            return -1
        sekarang = s.head
        i = 0
        while sekarang is not None:
            if sekarang.nilai[OID] == oid:
                return i
            sekarang = sekarang.next
            i += 1
        return -1

    def hapus_oid(self, nama, oid):
        i = self.cari_indeks_oid(nama, oid)
        if i < 0:
            return None
        return self.hapus(nama, i)

    def penghitung(self, nama):
        s = self.struktur(nama)
        if nama == "array":
            return s.jumlah_geser
        return s.jumlah_telusur
