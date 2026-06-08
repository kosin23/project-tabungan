import json
from datetime import datetime
from flask import Flask, request, redirect

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <body style="text-align:center;">
        <h1>Selamat Datang Di Website Keuanganmu</h1>
        <p>Semangat ya mencatat pemasukan dan pengeluaranmu</p>

        <a href="/pemasukan">
        <button>Pemasukan</button>
        </a>
        
        <br>
        <br>

        <a href="/pengeluaran">
        <button>Pengeluaran</button>
        </a>

        <br>
        <br>

        <a href="/rekapan">
        <button>Rekapan</button>
        </a>

        <br>
        <br>

        <a href="/keluar">
        <button>Keluar</button>
        </a>
    </body>
    """
@app.route("/pemasukan", methods=["GET","POST"])
def pemasukan():
    if request.method == "POST":
        nominal = request.form["nominal"]

        nominal = nominal.replace("RP","")
        nominal = nominal.replace(".","")

        if not nominal.isdigit():
            return """
            <script>
            alert('Nominal harus berupa angka!');
            window.history.back();
            </script>
            """
        keterangan = request.form["keterangan"]

        print(nominal)
        print(keterangan)

        transaksi = {
            "jenis": "pemasukan",
            "nominal": nominal,
            "keterangan": keterangan,
            "tanggal": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }
        print("MASUK KE POST")
        with open("data_transaksi.json", "r") as file :
            isi = file.read()
            print("ISI FILE", isi)
        with open("data_transaksi.json", "r") as file :
            data = json.load(file)

        data.append(transaksi)

        with open("data_transaksi.json", "w") as file :
            json.dump(data, file, indent=4)

        return redirect("/")

    return """
    <h1>Halaman Pemasukan</h1>

    <form method="POST">

        Nominal :
        <input type="text" id="nominal" name="nominal" oninput="formRupiah(this)">

        <br><br>

        Keterangan :
        <input type="text" name="keterangan">

        <br><br>

        <button>Simpan</button>

    </form>

    <script>

    function formRupiah(input){
        let angka = input.value.replace(/\D/g, "");

        if (angka === "") {
            input.value = "";
            return;
        }

        input.value = Number(angka).toLocaleString("id-ID");
    }
    </script>
    """

@app.route("/pengeluaran", methods=["GET", "POST"])
def pengeluaran():

    if request.method == "POST":
        nominal = request.form["nominal"]

        nominal = nominal.replace("RP","")
        nominal = nominal.replace(".","")

        if not nominal.isdigit():
            return """
            <script>
            alert('Nominal harus berupa angka!');
            window.history.back();
            </script>
            """
        keterangan = request.form["keterangan"]

        print(nominal)
        print(keterangan)

        transaksi = {
            "jenis": "pengeluaran",
            "nominal": nominal,
            "keterangan": keterangan,
            "tanggal": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        }

        with open("data_transaksi.json", "r") as file :
            data = json.load(file)

        data.append(transaksi)

        with open("data_transaksi.json", "w") as file :
            json.dump(data, file, indent=4)

        return redirect("/")

    return """
    <h1>Halaman Pengeluaran</h1>

    <form method="POST">

        Nominal :
        <input type="text" id="nominal" name="nominal" oninput="formRupiah(this)">

        <br><br>

        Keterangan :
        <input type="text" name="keterangan">

        <br><br>

        <button>Simpan</button>

    </form>

    <script>

    function formRupiah(input){
        let angka = input.value.replace(/\D/g, "");

        if (angka === "") {
            input.value = "";
            return;
        }

        input.value = Number(angka).toLocaleString("id-ID");
    }
    </script>
    """

@app.route("/rekapan")
def rekapan():

    with open("data_transaksi.json", "r") as file:
        data = json.load(file)

    print("DATA REKAPAN")
    print(data)

    total_pemasukan = 0
    total_pengeluaran = 0

    hasil =""

    hasil_pemasukan = ""
    hasil_pengeluaran = ""

    for transaksi in data:
        if transaksi["jenis"] == "pemasukan":
            total_pemasukan += int(transaksi["nominal"])

        elif transaksi["jenis"] == "pengeluaran":
            total_pengeluaran += int(transaksi["nominal"])
            
        if transaksi["jenis"] == "pemasukan":

            nominal_format = f"Rp {int(transaksi['nominal']):,}".replace(",", ".")

            hasil_pemasukan += f"""
            <p>
            {nominal_format} |
            {transaksi["keterangan"]} |
            {transaksi["tanggal"]}
            <a href="/hapus/{data.index(transaksi)}">
                <button>Hapus</button>
            </a>
            </p>
            """

        elif transaksi["jenis"] == "pengeluaran":

            nominal_format = f"Rp {int(transaksi['nominal']):,}".replace(",", ".")

            hasil_pengeluaran += f"""
            <p>
            {nominal_format} |
            {transaksi["keterangan"]} |
            {transaksi["tanggal"]}

            <a href="/hapus/{data.index(transaksi)}">
                <button>Hapus</button>
            </a>
            </p>
            """

    saldo = total_pemasukan - total_pengeluaran

    total_pemasukan_format = f"Rp {total_pemasukan:,}".replace(",", ".")
    total_pengeluaran_format = f"Rp {total_pengeluaran:,}".replace(",", ".")
    saldo_format = f"Rp {saldo:,}".replace(",", ".")

    return f"""
    <h1>Rekapan Transaksi</h1>

    <h2>Total Pemasukan : {total_pemasukan_format}</h2>
    <h2>Total Pengeluaran : {total_pengeluaran_format}</h2>
    <h2>Saldo : {saldo_format}</h2>

    <hr>

    <h2>Pemasukan</h2>
    {hasil_pemasukan}

    <hr>

    <h2>Pengeluaran</h2>
    {hasil_pengeluaran}

    <br>

    <a href="/">
        <button>Kembali</button>
    </a>
    """


@app.route("/hapus/<int:index>")
def hapus(index):

    with open("data_transaksi.json", "r") as file:
        data = json.load(file)

    data.pop(index)

    with open("data_transaksi.json", "w") as file:
        json.dump(data, file, indent=4)

    return redirect("/rekapan")

@app.route("/keluar")
def keluar():
    return ("Keluar")
app.run()


