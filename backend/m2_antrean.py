from backend.m1_pesanan import Array, STATUS, OID

OPERATOR = "+-*/"
DIGIT = "0123456789."


class Tumpukan:
    def __init__(self):
        self.larik = Array()

    def push(self, x):
        self.larik.append(x)

    def pop(self):
        if self.larik.size == 0:
            raise IndexError("tumpukan kosong")
        return self.larik.hapus(self.larik.size - 1)

    def peek(self):
        if self.larik.size == 0:
            raise IndexError("tumpukan kosong")
        return self.larik.get(self.larik.size - 1)

    def kosong(self):
        return self.larik.size == 0

    def panjang(self):
        return self.larik.size

    def kosongkan(self):
        self.larik = Array()

    def ke_list(self):
        return self.larik.ke_list()


def adalah_operator(t):
    return len(t) == 1 and t in OPERATOR


def prioritas_operator(op):
    if op == "*" or op == "/":
        return 2
    return 1


def ke_angka(t):
    if "." in t:
        return float(t)
    return int(t)


def teks_angka(x):
    if isinstance(x, float) and x == int(x):
        return str(int(x))
    return str(x)


def tokenisasi(teks):
    hasil = Array()
    angka = ""
    for ch in teks:
        if ch in DIGIT:
            angka += ch
            continue
        if angka != "":
            try:
                ke_angka(angka)
            except ValueError:
                raise ValueError("angka tidak valid: " + angka)
            hasil.append(angka)
            angka = ""
        if ch == " " or ch == "\t":
            continue
        if ch in "+-*/()":
            hasil.append(ch)
        else:
            raise ValueError("karakter tidak dikenal: " + ch)
    if angka != "":
        try:
            ke_angka(angka)
        except ValueError:
            raise ValueError("angka tidak valid: " + angka)
        hasil.append(angka)
    return hasil


def teks_tumpukan(tumpukan):
    isi = tumpukan.ke_list()
    if len(isi) == 0:
        return "kosong"
    return " ".join(isi)


def catat(langkah, nomor, token, tindakan, stack_teks, output_teks):
    if langkah is None:
        return
    langkah.append((nomor, token, tindakan, stack_teks, output_teks))


def ke_postfix(ekspresi, langkah=None):
    token = tokenisasi(ekspresi)
    keluaran = Array()
    tumpukan = Tumpukan()
    for i in range(token.size):
        t = token.get(i)
        nomor = "1.%d" % (i + 1)
        if t == "(":
            tumpukan.push(t)
            catat(langkah, nomor, t, "push ( ke stack", teks_tumpukan(tumpukan), " ".join(keluaran.ke_list()))
        elif t == ")":
            ditemukan = False
            while not tumpukan.kosong():
                atas = tumpukan.pop()
                if atas == "(":
                    ditemukan = True
                    break
                keluaran.append(atas)
            if not ditemukan:
                raise ValueError("kurung tutup tidak punya pasangan")
            catat(langkah, nomor, t, "pop sampai (, lalu buang (", teks_tumpukan(tumpukan), " ".join(keluaran.ke_list()))
        elif adalah_operator(t):
            dikeluarkan = Array()
            while not tumpukan.kosong():
                atas = tumpukan.peek()
                if atas == "(":
                    break
                if prioritas_operator(atas) >= prioritas_operator(t):
                    keluaran.append(tumpukan.pop())
                    dikeluarkan.append(atas)
                else:
                    break
            tumpukan.push(t)
            if dikeluarkan.size > 0:
                tindakan = "pop " + " ".join(dikeluarkan.ke_list()) + " (lebih kuat atau sama), push " + t
            else:
                tindakan = "push " + t
            catat(langkah, nomor, t, tindakan, teks_tumpukan(tumpukan), " ".join(keluaran.ke_list()))
        else:
            keluaran.append(t)
            catat(langkah, nomor, t, "operand, langsung ke output", teks_tumpukan(tumpukan), " ".join(keluaran.ke_list()))
    while not tumpukan.kosong():
        atas = tumpukan.pop()
        if atas == "(":
            raise ValueError("kurung buka tidak tertutup")
        keluaran.append(atas)
    catat(langkah, "1.akhir", "-", "pop sisa stack", teks_tumpukan(tumpukan), " ".join(keluaran.ke_list()))
    return keluaran.ke_list()


def hitung(postfix, langkah=None):
    tumpukan = Tumpukan()
    for i in range(len(postfix)):
        t = postfix[i]
        nomor = "2.%d" % (i + 1)
        if adalah_operator(t):
            if tumpukan.panjang() < 2:
                raise ValueError("ekspresi tidak valid")
            b = tumpukan.pop()
            a = tumpukan.pop()
            if t == "+":
                hasil = a + b
            elif t == "-":
                hasil = a - b
            elif t == "*":
                hasil = a * b
            else:
                if b == 0:
                    raise ValueError("pembagian dengan nol")
                hasil = a / b
                if hasil == int(hasil):
                    hasil = int(hasil)
            tumpukan.push(hasil)
            tindakan = "pop %s dan %s -> %s %s %s = %s" % (teks_angka(b), teks_angka(a), teks_angka(a), t, teks_angka(b), teks_angka(hasil))
        else:
            tumpukan.push(ke_angka(t))
            tindakan = "operand, push " + t
        isi = tumpukan.ke_list()
        teks = ""
        for j in range(len(isi)):
            if j > 0:
                teks += " "
            teks += teks_angka(isi[j])
        catat(langkah, nomor, t, tindakan, teks, "")
    if tumpukan.panjang() != 1:
        raise ValueError("ekspresi tidak valid")
    return tumpukan.pop()


class HasilKasir:
    def __init__(self, postfix_teks, total, langkah):
        self.postfix_teks = postfix_teks
        self.total = total
        self.langkah = langkah


def mesin_kasir(ekspresi):
    langkah = Array()
    postfix = ke_postfix(ekspresi, langkah)
    total = hitung(postfix, langkah)
    return HasilKasir(" ".join(postfix), total, langkah.ke_list())


class AntreanNaif:
    def __init__(self):
        self.larik = Array(1024)

    def enqueue(self, x):
        self.larik.append(x)

    def dequeue(self):
        if self.larik.size == 0:
            return None
        return self.larik.hapus(0)

    def dequeue_belakang(self):
        if self.larik.size == 0:
            return None
        return self.larik.hapus(self.larik.size - 1)

    def enqueue_depan(self, x):
        self.larik.insert(0, x)

    def panjang(self):
        return self.larik.size

    def kapasitas(self):
        return self.larik.kapasitas

    def total_geseran(self):
        return self.larik.jumlah_geser

    def ke_list(self):
        return self.larik.ke_list()


class AntreanMelingkar:
    def __init__(self, kapasitas=1024):
        if kapasitas < 1:
            kapasitas = 1
        self.kapasitas_data = kapasitas
        self.data = [None] * kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0
        self.jumlah_tumbuh = 0

    def tumbuh(self):
        baru = [None] * (self.kapasitas_data * 2)
        for i in range(self.count):
            baru[i] = self.data[(self.front + i) % self.kapasitas_data]
        self.data = baru
        self.front = 0
        self.rear = self.count
        self.kapasitas_data = self.kapasitas_data * 2
        self.jumlah_tumbuh += 1

    def enqueue(self, x):
        if self.count == self.kapasitas_data:
            self.tumbuh()
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.kapasitas_data
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        x = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.kapasitas_data
        self.count -= 1
        return x

    def dequeue_belakang(self):
        if self.count == 0:
            return None
        self.rear = (self.rear - 1) % self.kapasitas_data
        x = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return x

    def enqueue_depan(self, x):
        if self.count == self.kapasitas_data:
            self.tumbuh()
        self.front = (self.front - 1) % self.kapasitas_data
        self.data[self.front] = x
        self.count += 1

    def is_empty(self):
        return self.count == 0

    def panjang(self):
        return self.count

    def kapasitas(self):
        return self.kapasitas_data

    def total_geseran(self):
        return 0

    def ke_list(self):
        hasil = [None] * self.count
        for i in range(self.count):
            hasil[i] = self.data[(self.front + i) % self.kapasitas_data]
        return hasil


class LayananAntrean:
    def __init__(self, hook_batal_order=None, hook_ulang_order=None):
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar()
        self.undo = Tumpukan()
        self.redo = Tumpukan()
        self.hook_batal_order = hook_batal_order
        self.hook_ulang_order = hook_ulang_order

    def isi_awal(self, data):
        self.naif = AntreanNaif()
        self.melingkar = AntreanMelingkar()
        self.undo = Tumpukan()
        self.redo = Tumpukan()
        for i in range(data.size):
            p = data.get(i)
            if p[STATUS] == "ANTRE":
                self.naif.enqueue(p)
                self.melingkar.enqueue(p)

    def pilih(self, varian):
        if varian == "NAIF":
            return self.naif
        return self.melingkar

    def catat_aksi(self, aksi):
        self.undo.push(aksi)
        self.redo.kosongkan()

    def enqueue(self, pesanan):
        self.naif.enqueue(pesanan)
        self.melingkar.enqueue(pesanan)
        self.catat_aksi(("ENQUEUE", pesanan))

    def catat_order(self, pesanan, jenis, struktur):
        self.catat_aksi(("ORDER", pesanan, jenis, struktur))

    def keluarkan(self, antrean, n):
        hasil = Array()
        for _ in range(n):
            x = antrean.dequeue()
            if x is None:
                break
            hasil.append(x)
        return hasil.ke_list()

    def dequeue_naif(self, n=1):
        sebelum = self.naif.total_geseran()
        daftar = self.keluarkan(self.naif, n)
        geser = self.naif.total_geseran() - sebelum
        if len(daftar) > 0:
            self.catat_aksi(("DEQUEUE", "NAIF", daftar))
        return daftar, geser

    def dequeue_circular(self, n=1):
        daftar = self.keluarkan(self.melingkar, n)
        if len(daftar) > 0:
            self.catat_aksi(("DEQUEUE", "CIRCULAR", daftar))
        return daftar, 0

    def undo_last(self):
        if self.undo.kosong():
            return None
        aksi = self.undo.pop()
        jenis = aksi[0]
        if jenis == "ENQUEUE":
            self.naif.dequeue_belakang()
            self.melingkar.dequeue_belakang()
        elif jenis == "DEQUEUE":
            antrean = self.pilih(aksi[1])
            daftar = aksi[2]
            i = len(daftar) - 1
            while i >= 0:
                antrean.enqueue_depan(daftar[i])
                i -= 1
        elif jenis == "ORDER":
            if self.hook_batal_order is not None:
                self.hook_batal_order(aksi[1], aksi[3])
        self.redo.push(aksi)
        return aksi

    def redo_last(self):
        if self.redo.kosong():
            return None
        aksi = self.redo.pop()
        jenis = aksi[0]
        if jenis == "ENQUEUE":
            self.naif.enqueue(aksi[1])
            self.melingkar.enqueue(aksi[1])
        elif jenis == "DEQUEUE":
            antrean = self.pilih(aksi[1])
            for _ in range(len(aksi[2])):
                antrean.dequeue()
        elif jenis == "ORDER":
            if self.hook_ulang_order is not None:
                self.hook_ulang_order(aksi[1], aksi[2], aksi[3])
        self.undo.push(aksi)
        return aksi

    def history(self):
        isi = self.undo.ke_list()
        hasil = [None] * len(isi)
        for i in range(len(isi)):
            aksi = isi[i]
            if aksi[0] == "ENQUEUE":
                hasil[i] = "ENQUEUE " + aksi[1][OID]
            elif aksi[0] == "DEQUEUE":
                hasil[i] = "DEQUEUE %s x%d" % (aksi[1], len(aksi[2]))
            else:
                hasil[i] = "ORDER %s %s" % (aksi[1][OID], aksi[3])
        return hasil

    def stats(self):
        return (
            ("queue_len_naif", self.naif.panjang()),
            ("queue_len_circular", self.melingkar.panjang()),
            ("queue_capacity_naif", self.naif.kapasitas()),
            ("queue_capacity_circular", self.melingkar.kapasitas()),
            ("total_geseran", self.naif.total_geseran()),
            ("undo_depth", self.undo.panjang()),
            ("redo_depth", self.redo.panjang()),
        )
