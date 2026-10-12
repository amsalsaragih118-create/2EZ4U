import time

from backend.m1_pesanan import OID, HARGA, T_SELESAI

BATAS_INSERTION = 20000
BELUM_SELESAI = 10 ** 12


class Pencacah:
    def __init__(self):
        self.perbandingan = 0
        self.pemindahan = 0


def kunci_oid(p):
    return p[OID]


def kunci_harga(p):
    return p[HARGA]


def kunci_selesai(p):
    nilai = p[T_SELESAI]
    if nilai is None:
        return BELUM_SELESAI
    return nilai


def ambil_kunci(nama):
    if nama == "oid":
        return kunci_oid
    if nama == "harga":
        return kunci_harga
    if nama == "selesai":
        return kunci_selesai
    raise ValueError("kunci tidak dikenal: " + nama)


def insertion_sort(A, kunci, pencacah=None):
    if pencacah is None:
        pencacah = Pencacah()
    n = len(A)
    ks = [None] * n
    for i in range(n):
        ks[i] = kunci(A[i])
    for i in range(1, n):
        k = ks[i]
        v = A[i]
        j = i - 1
        while j >= 0:
            pencacah.perbandingan += 1
            if ks[j] > k:
                ks[j + 1] = ks[j]
                A[j + 1] = A[j]
                pencacah.pemindahan += 1
                j -= 1
            else:
                break
        if j + 1 != i:
            ks[j + 1] = k
            A[j + 1] = v
            pencacah.pemindahan += 1
    return A


def gabung(nilai, ks, aux_n, aux_k, lo, mid, hi, pencacah):
    i = lo
    j = mid + 1
    t = lo
    while i <= mid and j <= hi:
        pencacah.perbandingan += 1
        if ks[i] <= ks[j]:
            aux_n[t] = nilai[i]
            aux_k[t] = ks[i]
            i += 1
        else:
            aux_n[t] = nilai[j]
            aux_k[t] = ks[j]
            j += 1
        t += 1
        pencacah.pemindahan += 1
    while i <= mid:
        aux_n[t] = nilai[i]
        aux_k[t] = ks[i]
        i += 1
        t += 1
        pencacah.pemindahan += 1
    while j <= hi:
        aux_n[t] = nilai[j]
        aux_k[t] = ks[j]
        j += 1
        t += 1
        pencacah.pemindahan += 1
    for x in range(lo, hi + 1):
        nilai[x] = aux_n[x]
        ks[x] = aux_k[x]


def bagi(nilai, ks, aux_n, aux_k, lo, hi, pencacah):
    if lo >= hi:
        return
    mid = (lo + hi) // 2
    bagi(nilai, ks, aux_n, aux_k, lo, mid, pencacah)
    bagi(nilai, ks, aux_n, aux_k, mid + 1, hi, pencacah)
    gabung(nilai, ks, aux_n, aux_k, lo, mid, hi, pencacah)


def merge_sort(A, kunci, pencacah=None):
    if pencacah is None:
        pencacah = Pencacah()
    n = len(A)
    nilai = [None] * n
    ks = [None] * n
    for i in range(n):
        nilai[i] = A[i]
        ks[i] = kunci(A[i])
    aux_n = [None] * n
    aux_k = [None] * n
    bagi(nilai, ks, aux_n, aux_k, 0, n - 1, pencacah)
    return nilai


def linear_search(A, target, kunci=None, pencacah=None):
    if pencacah is None:
        pencacah = Pencacah()
    for i in range(len(A)):
        pencacah.perbandingan += 1
        k = A[i] if kunci is None else kunci(A[i])
        if k == target:
            return i
    return -1


def binary_search(A, target, kunci=None, pencacah=None):
    if pencacah is None:
        pencacah = Pencacah()
    lo = 0
    hi = len(A) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        k = A[mid] if kunci is None else kunci(A[mid])
        pencacah.perbandingan += 1
        if k == target:
            return mid
        if k < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


class HasilUrut:
    def __init__(self, data, perbandingan, pemindahan, durasi):
        self.data = data
        self.perbandingan = perbandingan
        self.pemindahan = pemindahan
        self.durasi = durasi


class HasilCari:
    def __init__(self, indeks, pesanan, perbandingan, durasi, ongkos_bangun, baru_dibangun):
        self.indeks = indeks
        self.pesanan = pesanan
        self.perbandingan = perbandingan
        self.durasi = durasi
        self.ongkos_bangun = ongkos_bangun
        self.baru_dibangun = baru_dibangun


class LaporanHarian:
    def __init__(self, data_awal):
        self.data = data_awal.ke_list()
        self.terurut_oid = None
        self.ongkos_bangun = 0.0

    def jumlah_data(self):
        return len(self.data)

    def ambil_awal(self, jumlah):
        if jumlah < 1:
            raise ValueError("jumlah baris harus lebih dari 0")
        if jumlah > len(self.data):
            jumlah = len(self.data)
        salinan = [None] * jumlah
        for i in range(jumlah):
            salinan[i] = self.data[i]
        return salinan

    def urut_insertion(self, jumlah, nama_kunci):
        if jumlah > BATAS_INSERTION:
            raise ValueError("DITOLAK: batasnya %d baris, pakai merge sort untuk data penuh" % BATAS_INSERTION)
        kunci = ambil_kunci(nama_kunci)
        salinan = self.ambil_awal(jumlah)
        pencacah = Pencacah()
        mulai = time.perf_counter()
        insertion_sort(salinan, kunci, pencacah)
        durasi = time.perf_counter() - mulai
        return HasilUrut(salinan, pencacah.perbandingan, pencacah.pemindahan, durasi)

    def urut_merge(self, jumlah, nama_kunci):
        kunci = ambil_kunci(nama_kunci)
        salinan = self.ambil_awal(jumlah)
        pencacah = Pencacah()
        mulai = time.perf_counter()
        hasil = merge_sort(salinan, kunci, pencacah)
        durasi = time.perf_counter() - mulai
        return HasilUrut(hasil, pencacah.perbandingan, pencacah.pemindahan, durasi)

    def laporan_harian(self):
        return self.urut_merge(len(self.data), "selesai")

    def bangun_indeks_oid(self):
        if self.terurut_oid is not None:
            return False
        mulai = time.perf_counter()
        self.terurut_oid = merge_sort(self.data, kunci_oid)
        self.ongkos_bangun = time.perf_counter() - mulai
        return True

    def cari_linear(self, oid):
        pencacah = Pencacah()
        mulai = time.perf_counter()
        indeks = linear_search(self.data, oid.strip().upper(), kunci_oid, pencacah)
        durasi = time.perf_counter() - mulai
        pesanan = None
        if indeks >= 0:
            pesanan = self.data[indeks]
        return HasilCari(indeks, pesanan, pencacah.perbandingan, durasi, 0.0, False)

    def cari_binary(self, oid):
        baru = self.bangun_indeks_oid()
        pencacah = Pencacah()
        mulai = time.perf_counter()
        indeks = binary_search(self.terurut_oid, oid.strip().upper(), kunci_oid, pencacah)
        durasi = time.perf_counter() - mulai
        pesanan = None
        if indeks >= 0:
            pesanan = self.terurut_oid[indeks]
        return HasilCari(indeks, pesanan, pencacah.perbandingan, durasi, self.ongkos_bangun, baru)

    def stats(self):
        return (
            ("jumlah_data", len(self.data)),
            ("indeks_oid_siap", self.terurut_oid is not None),
            ("ongkos_bangun_indeks_detik", self.ongkos_bangun),
        )
