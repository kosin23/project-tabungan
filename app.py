import json
from datetime import datetime
from flask import Flask, request, redirect, session
import os
import psycopg2
def get_conn():
    return psycopg2.connect(os.environ["DATABASE_URL"])

def buat_database():

    conn = get_conn()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transaksi(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        jenis TEXT,
        nominal INTEGER,
        keterangan TEXT,
        tanggal TEXT
    )
    """)

    conn.commit()
    conn.close()

app = Flask(__name__)
app.secret_key = "rahasia123"

@app.route("/")
def home():

    if "username" not in session:
        return redirect("/login")

    username = session.get("username")

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
        SELECT * FROM users WHERE username=%s AND password=%s
        (username,)
    )

    data = cursor.fetchall()

    conn.close()

    total_pemasukan = 0
    total_pengeluaran = 0

    for transaksi in data:

        if transaksi[0] == "pemasukan":
            total_pemasukan += int(transaksi[1])

        elif transaksi[0] == "pengeluaran":
            total_pengeluaran += int(transaksi[1])

    saldo = total_pemasukan - total_pengeluaran

    saldo_format = f"Rp {saldo:,}".replace(",", ".")
    pemasukan_format = f"Rp {total_pemasukan:,}".replace(",", ".")
    pengeluaran_format = f"Rp {total_pengeluaran:,}".replace(",", ".")
    
    username = session.get("username", "Guest")

    admin_button = ""

    if username == "admin":

        admin_button = """
        <a href="/admin">
            <button>Panel Admin</button>
        </a>

        <br><br>
        """

    return f"""
    <style>

    body{{
        font-family: "Segoe UI", sans-serif;
        text-align: center;

        background: linear-gradient(135deg, #c7d2fe, #dbeafe);

        min-height: 100vh;

        display: flex;
        justify-content: center;
        align-items: center;
    }}

    .card{{
        background: #eef2ff;
        backdrop-filter: blur(12px);
        width: 90%;
        max-width: 420px;

        padding: 35px;

        border-radius: 20px;

        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }}

    .saldo-card{{
        margin-bottom: 25px;
    }}

    .statistik{{
        display: flex;
        gap: 15px;
        margin-top: 20px;
    }}

    .box{{
        flex: 1;
        padding: 15px;
        border-radius: 15px;
    }}

    .pemasukan-box{{
        background: #dcfce7;
    }}

    .pengeluaran-box{{
        background: #fee2e2;
    }}

    .pemasukan-box h3{{
        color: #15803d;
    }}

    .pengeluaran-box h3{{
        color: #dc2626;
    }}

    .box p{{
        font-size: 18px;
        font-weight: bold;
    }}

    h1{{
        color: #333;
    }}

    h2{{
        color: #222;
    }}

    #saldo{{
        font-size: 42px;
        font-weight: bold;
        color: #1e293b;

        margin-top: 10px;
        margin-bottom: 15px;
    }}

    #pemasukan{{
        color: #16a34a;
        font-weight: 600;
    }}

    #pengeluaran{{
        color: #dc2626;
        font-weight: 600;
    }}

    button{{
        background: #4f46e5;

        color: white;

        border: none;

        padding: 14px 28px;

        margin: 8px;

        border-radius: 12px;

        cursor: pointer;

        font-size: 16px;
        font-weight: bold;

        transition: all 0.3s ease;
    }}

    button:hover{{
        transform: translateY(-3px);

        box-shadow: 0 6px 15px rgba(79,70,229,0.35);
    }}

    hr{{
        margin-top: 20px;
        margin-bottom: 20px;

        border: none;

        height: 1px;

        background: #d1d5db;
    }}

    p{{
        font-size: 16px;
    }}

    </style>

    <body>

        <div class="card">

            <h1>Selamat Datang {username}</h1>

            <p>Semangat ya mencatat pemasukan dan pengeluaranmu</p>

            <div class="saldo-card">

                <h2>💰 Saldo Saat Ini</h2>

                <h1 id="saldo">{saldo_format}</h1>

                <button onclick="toggleSaldo()">👁️ Hide / Show</button>

                <div class="statistik">

                    <div class="box pemasukan-box">
                        <h3>📈 Pemasukan</h3>
                        <p id="pemasukan">{pemasukan_format}</p>
                    </div>

                    <div class="box pengeluaran-box">
                        <h3>📉 Pengeluaran</h3>
                        <p id="pengeluaran">{pengeluaran_format}</p>
                    </div>

                </div>

            </div>

            <a href="/pemasukan">
                <button>Pemasukan</button>
            </a>

            <br><br>

            <a href="/pengeluaran">
                <button>Pengeluaran</button>
            </a>

            <br><br>

            <a href="/rekapan">
                <button>Rekapan</button>
            </a>

            <br><br>

            {admin_button}

            <a href="/logout">
                 <button>Keluar</button>
            </a>

        </div>

        <script>

        let saldoTampil = true;
        let saldoAsli = "{saldo_format}";

        function toggleSaldo(){{

            let saldo = document.getElementById("saldo");
            let pemasukan = document.getElementById("pemasukan");
            let pengeluaran = document.getElementById("pengeluaran");

            if(saldoTampil){{
                saldo.innerHTML = "********";
                pemasukan.innerHTML = "********";
                pengeluaran.innerHTML = "********";

                saldoTampil = false;
            }}

            else{{
                saldo.innerHTML = saldoAsli;
                pemasukan.innerHTML = "{pemasukan_format}";
                pengeluaran.innerHTML = "{pengeluaran_format}";

                saldoTampil = true;
            }}
        }}

        </script>

    </body>
    """

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_conn()
        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
            )

            conn.commit()

            return redirect("/login")

        except:
            return "<h1>Username sudah digunakan!</h1>"

        finally:
            conn.close()

    return """
    <style>

    body{
        font-family: "Segoe UI", sans-serif;

        background: linear-gradient(135deg, #c7d2fe, #dbeafe);

        min-height: 100vh;

        display:flex;
        justify-content:center;
        align-items:center;
    }

    .card{
        background:#eef2ff;

        width:400px;

        padding:35px;

        border-radius:20px;

        box-shadow:0 8px 25px rgba(0,0,0,0.15);

        text-align:center;
    }

    h1{
        color:#1e293b;
    }

    input{
        width:90%;

        padding:14px;

        margin:10px 0;

        border:2px solid #cbd5e1;

        border-radius:12px;

        font-size:15px;
    }

    button{
        background:#4f46e5;

        color:white;

        border:none;

        padding:14px 28px;

        border-radius:12px;

        cursor:pointer;

        font-size:16px;

        font-weight:bold;
    }

    a{
        text-decoration:none;
    }

    .link{
        margin-top:15px;
    }

    </style>

    <div class="card">

        <h1>Daftar</h1>

        <form method="POST">

            <input
                type="text"
                name="username"
                placeholder="Username"
                required
            >

            <input
                type="password"
                name="password"
                placeholder="Password"
                required
            >

            <br><br>

        <button type="submit">
            Daftar
        </button>

    </form>

     <div class="link">

        Sudah punya akun?

    <a href="/login">
        Login
    </a>

    </div>

</div>
"""

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            SELECT * FROM users WHERE username=%s AND password=%s
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["username"] = username

            return redirect("/")

        else:

            return """
            <style>

            body{
                font-family: "Segoe UI", sans-serif;

                background: linear-gradient(135deg, #c7d2fe, #dbeafe);

                min-height:100vh;

                display:flex;
                justify-content:center;
                align-items:center;
            }

            .card{
                background:#eef2ff;

                width:400px;

                padding:35px;

                border-radius:20px;

                box-shadow:0 8px 25px rgba(0,0,0,0.15);

                text-align:center;
            }

            h1{
                color:#dc2626;
            }

            p{
                color:#475569;
            }

            button{
                background:#4f46e5;

                color:white;

                border:none;

                padding:14px 28px;

                border-radius:12px;

                cursor:pointer;

                font-size:16px;

                font-weight:bold;
            }

            a{
                text-decoration:none;
            }

            </style>

            <div class="card">

                <h1>Login Gagal</h1>

                <p>
                Username atau Password salah
                </p>

                <br>

            <a href="/login">
                <button>Coba Lagi</button>
            </a>

        </div>
        """

    return """
    <style>

    body{
        font-family: "Segoe UI", sans-serif;

        background: linear-gradient(135deg, #c7d2fe, #dbeafe);

        min-height: 100vh;

        display:flex;
        justify-content:center;
        align-items:center;
    }

    .card{
        background:#eef2ff;

        width:400px;

        padding:35px;

        border-radius:20px;

        box-shadow:0 8px 25px rgba(0,0,0,0.15);

        text-align:center;
    }

    h1{
        color:#1e293b;
    }

    input{
        width:90%;

        padding:14px;

        margin:10px 0;

        border:2px solid #cbd5e1;

        border-radius:12px;

        font-size:15px;
    }

    button{
        background:#4f46e5;

        color:white;

        border:none;

        padding:14px 28px;

        border-radius:12px;

        cursor:pointer;

        font-size:16px;

        font-weight:bold;
    }

    a{
        text-decoration:none;
    }

    .link{
        margin-top:15px;
    }

    </style>

    <div class="card">

        <h1>Login</h1>

        <form method="POST">

            <input
                type="text"
                name="username"
                placeholder="Username"
                required
            >

            <input
                type="password"
                name="password"
                placeholder="Password"
                required
            >

            <br><br>

        <button type="submit">
            Login
        </button>

    </form>

    <div class="link">

        Belum punya akun?

        <a href="/register">
            Daftar
        </a>

    </div>

</div>
"""

@app.route("/admin")
def admin():

    if session.get("username") != "admin":
        return "<h1>Akses Ditolak!</h1>"

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username FROM users")

    users = cursor.fetchall()

    conn.close()

    daftar_user = ""

    for user in users:

        daftar_user += f"""
        <tr>
            <td>{user[0]}</td>
            <td>{user[1]}</td>

            <td>

                <a href="/admin-reset/{user[0]}">
                    <button>Reset</button>
                </a>

                <a href="/hapus-user/{user[0]}">
                    <button>Hapus</button>
                </a>

            </td>

        </tr>
        """

    return f"""
    <style>

    body{{
        font-family: "Segoe UI", sans-serif;

        background: linear-gradient(135deg,#c7d2fe,#dbeafe);

        min-height:100vh;

        display:flex;
        justify-content:center;
        align-items:center;
    }}

    .card{{
        background:#eef2ff;

        width:700px;

        padding:35px;

        border-radius:20px;

        box-shadow:0 8px 25px rgba(0,0,0,0.15);

        text-align:center;
    }}

    h1{{
        olor:#1e293b;
    }}

    table{{
        width:100%;
        border-collapse:collapse;

        margin-top:20px;
    }}

    th{{
        background:#4f46e5;
        color:white;

        padding:12px;
    }}

    td{{
        background:white;
        padding:12px;
    }}

    button{{
        background:#4f46e5;
        color:white;

        border:none;

        padding:8px 15px;

        border-radius:10px;

        cursor:pointer;

        font-weight:bold;
    }}

    button:hover{{
        opacity:0.9;
    }}

    .hapus{{
        background:#dc2626;
    }}

    .reset{{
        background:#f59e0b;
    }}

    .kembali{{
        margin-top:20px;
    }}

    a{{
        text-decoration:none;
    }}

    </style>

    <div class="card">

        <h1>Panel Admin</h1>

        <table>

            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Aksi</th>
            </tr>

            {daftar_user}

        </table>

        <div class="kembali">

            <a href="/">
                <button>Kembali</button>
            </a>

        </div>

    </div>
    """

@app.route("/hapus-user/<int:id_user>")
def hapus_user(id_user):

    if session.get("username") != "admin":
        return "Akses Ditolak"

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute(
    SELECT * FROM users WHERE username=%s AND password=%s
    (id_user,)
    )

    user = cursor.fetchone()

    if user and user[0] == "admin":
        return """
        <style>

        body{
            font-family:"Segoe UI",sans-serif;

            background:linear-gradient(135deg,#c7d2fe,#dbeafe);

            min-height:100vh;

            display:flex;
            justify-content:center;
            align-items:center;
        }

        .card{
            background:#eef2ff;

            width:500px;

            padding:35px;

            border-radius:20px;

            box-shadow:0 8px 25px rgba(0,0,0,0.15);

            text-align:center;
        }

        h1{
            color:#dc2626;
        }

        button{
            background:#4f46e5;

            color:white;

            border:none;

            padding:14px 28px;

            border-radius:12px;

            cursor:pointer;

            font-weight:bold;
        }

        a{
            text-decoration:none;
        }

        </style>

        <div class="card">

            <h1>Akun admin tidak boleh dihapus!</h1>

            <br>

            <a href="/admin">
                <button>Kembali ke Panel Admin</button>
            </a>

        </div>
        """  

    cursor.execute(
        "DELETE FROM users WHERE id=%",
        (id_user,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")

@app.route("/admin-reset/<int:id_user>", methods=["GET", "POST"])
def admin_reset(id_user):

    if request.method == "POST":

        password_baru = request.form["password_baru"]
        konfirmasi = request.form["konfirmasi"]

        if password_baru != konfirmasi:
            return "<h1>Password tidak sama!</h1>"

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password=% WHERE id=%",
            (password_baru, id_user)
        )

        conn.commit()
        conn.close()

        return redirect("/admin")

    return """
    <style>

    body{
        font-family:"Segoe UI",sans-serif;

        background:linear-gradient(135deg,#c7d2fe,#dbeafe);

        min-height:100vh;

        display:flex;
        justify-content:center;
        align-items:center;
    }

    .card{
        background:#eef2ff;

        width:420px;

        padding:35px;

        border-radius:20px;

        box-shadow:0 8px 25px rgba(0,0,0,0.15);

        text-align:center;
    }

    h1{
        color:#1e293b;
    }

    input{
        width:90%;

        padding:14px;

        margin:10px 0;

        border:2px solid #cbd5e1;

        border-radius:12px;

        font-size:15px;
    }

    button{
        background:#4f46e5;

        color:white;

        border:none;

        padding:14px 28px;

        border-radius:12px;

        cursor:pointer;

        font-weight:bold;
    }

    .back-btn{
        background:#64748b;
    }

    </style>

    <div class="card">

        <h1>Reset Password</h1>

        <form method="POST">

            <input
                type="password"
                name="password_baru"
                placeholder="Password Baru"
                required
            >

            <input
                type="password"
                name="konfirmasi"
                placeholder="Konfirmasi Password"
                required
            >

            <br><br>

            <button type="submit">
                Simpan Password
            </button>

            <br><br>

            <a href="/admin">
                <button type="button" class="back-btn">
                ← Kembali
                </button>
            </a>

        </form>

    </div>
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

        username = session["username"]

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
        """
            INSERT INTO transaksi
            (username, jenis, nominal, keterangan, tanggal)
            VALUES (%s, %s, %s, %s, %s)
        """,
        (
            username,
            "pemasukan",
            int(nominal),
            keterangan,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

        conn.commit()
        conn.close()

        return redirect("/")

    return """
    <style>

    body{
        font-family: "Segoe UI", sans-serif;
        background: linear-gradient(135deg, #c7d2fe, #dbeafe);

        min-height: 100vh;

        display: flex;
        justify-content: center;
        align-items: center;
    }

    .card{
        background: #f8fafc;

        width: 650px;

        padding: 45px;

        border-radius: 25px;

        box-shadow: 0 8px 25px rgba(0,0,0,0.15);

        text-align: center;
    }

    h1{
        color: #1e293b;
        font-size: 42px;
        text-align: center;
        margin-bottom: 30px;
    }

    p{
        font-size: 20px;
        font-weight: 600;
        color: #334155;
        margin-bottom: 10px;
    }

    input{
        width: 90%;

        padding: 16px;

        font-size: 18px;

        border: 1px solid #cbd5e1;

        border-radius: 12px;

        margin-top: 8px;
    }
    
    form{
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    button{
        background: #4f46e5;

        color: white;

        border: none;

        padding: 14px 30px;

        border-radius: 12px;

        cursor: pointer;

        ont-size: 16px;

        font-weight: bold;

        display: block;
        margin: 10px auto;
    }

    button:hover{
        transform: translateY(-2px);
    }

    .back-btn{
        background: #64748b;
    }

    </style>

    <div class="card">

        <h1>💰 Halaman Pemasukan</h1>

        <form method="POST">

            <p>Nominal</p>

            <input
                type="text"
                id="nominal"
                name="nominal"
                oninput="formRupiah(this)"
            >

            <br><br>

            <p>Keterangan</p>

            <input
                type="text"
                name="keterangan"
            >

            <br><br>

            <button type="submit">
                Simpan
            </button>

        </form>

        <br>

        <a href="/">
            <button type="button" class="back-btn">
                ← Kembali
            </button>
        </a>

    </div>

    <script>

    function formRupiah(input){

        let angka = input.value.replace(/\\D/g, "");

        if(angka === ""){
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

        username = session["username"]

        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute(
        """
            INSERT INTO transaksi
            (username, jenis, nominal, keterangan, tanggal)
            VALUES (%s, %s, %s, %s, %s)
        """,
        (
            username,
            "pengeluaran",
            int(nominal),
            keterangan,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

        conn.commit()
        conn.close()

        return redirect("/")

    return """
    <style>

    body{
        font-family: "Segoe UI", sans-serif;
        background: linear-gradient(135deg, #c7d2fe, #dbeafe);

        min-height: 100vh;

        display: flex;
        justify-content: center;
        align-items: center;
    }

    .card{
        background: #f8fafc;

        width: 650px;

        padding: 45px;

        border-radius: 25px;

        box-shadow: 0 8px 25px rgba(0,0,0,0.15);

        text-align: center;
    }

    h1{
        color: #1e293b;
        font-size: 42px;
        text-align: center;
        margin-bottom: 30px;
    }

    p{
        font-size: 20px;
        font-weight: 600;
        color: #334155;
        margin-bottom: 10px;
    }

    input{
        width: 90%;

        padding: 16px;

        font-size: 18px;

        border: 1px solid #cbd5e1;

        border-radius: 12px;

        margin-top: 8px;
    }
    
    form{
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    button{
        background: #4f46e5;

        color: white;

        border: none;

        padding: 14px 30px;

        border-radius: 12px;

        cursor: pointer;

        ont-size: 16px;

        font-weight: bold;

        display: block;
        margin: 10px auto;
    }

    button:hover{
        transform: translateY(-2px);
    }

    .back-btn{
        background: #64748b;
    }

    </style>

    <div class="card">

        <h1>💸 Halaman Pengeluaran</h1>

        <form method="POST">

            <p>Nominal</p>

            <input
                type="text"
                id="nominal"
                name="nominal"
                oninput="formRupiah(this)"
            >

            <br><br>

            <p>Keterangan</p>

            <input
                type="text"
                name="keterangan"
            >

            <br><br>

            <button type="submit">
                Simpan
            </button>

        </form>

        <br>

        <a href="/">
            <button type="button" class="back-btn">
                ← Kembali
            </button>
        </a>

    </div>

    <script>

    function formRupiah(input){

        let angka = input.value.replace(/\\D/g, "");

        if(angka === ""){
            input.value = "";
            return;
        }

        input.value = Number(angka).toLocaleString("id-ID");
    }

    </script>
    """

@app.route("/rekapan")
def rekapan():

    dari = request.args.get("dari")
    sampai = request.args.get("sampai")
    
    username = session["username"]

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, jenis, nominal, keterangan, tanggal
    FROM transaksi
    WHERE username = %
    ORDER BY tanggal DESC
    """, (username,))

    data = cursor.fetchall()

    conn.close()

    print("DATA REKAPAN")
    print(data)

    total_pemasukan = 0
    total_pengeluaran = 0

    hasil =""

    hasil_pemasukan = ""
    hasil_pengeluaran = ""

    data_filter = []

    for transaksi in data:

        tanggal_transaksi = transaksi[4][:10]

        print("TRANSAKSI:", tanggal_transaksi)
        print("DARI:", dari)
        print("SAMPAI:", sampai)

        if dari and sampai:

            if dari <= tanggal_transaksi <= sampai:
                data_filter.append(transaksi)

        else:
            data_filter.append(transaksi)

    for transaksi in data_filter:

        if transaksi[1] == "pemasukan":

            total_pemasukan += int(transaksi[2])

            nominal_format = f"Rp {int(transaksi[2]):,}".replace(",", ".")

            hasil_pemasukan += f"""
            <div class="transaksi-card">

                <h3>{transaksi[3]}</h3>

                <p>{nominal_format}</p>

                <small>{transaksi[4]}</small>

                <br><br>

                <a href="/edit/{transaksi[0]}">
                <button>Edit Transaksi</button>
                </a>

                <a href="/hapus/{transaksi[0]}" onclick="return confirm('⚠️ Data yang dihapus tidak bisa dikembalikan. Lanjutkan?')">
                    <button>Hapus Transaksi</button>
                </a>

            </div>
            """

        elif transaksi[1] == "pengeluaran":

            total_pengeluaran += int(transaksi[2])

            nominal_format = f"Rp {int(transaksi[2]):,}".replace(",", ".")

            hasil_pengeluaran += f"""
                <div class="transaksi-card">

                <h3>{transaksi[3]}</h3>

                <p>{nominal_format}</p>

                <small>{transaksi[4]}</small>

                <br><br>

                <a href="/edit/{transaksi[0]}">
                    <button>Edit Transaksi</button>
                </a>

                <a href="/hapus/{transaksi[0]}" onclick="return confirm('⚠️ Data yang dihapus tidak bisa dikembalikan. Lanjutkan?')">
                    <button>Hapus Transaksi</button>
                </a>

            </div>
            """

    saldo = total_pemasukan - total_pengeluaran

    total_pemasukan_format = f"Rp {total_pemasukan:,}".replace(",", ".")
    total_pengeluaran_format = f"Rp {total_pengeluaran:,}".replace(",", ".")
    saldo_format = f"Rp {saldo:,}".replace(",", ".")

    hari_ini = datetime.now().strftime("%Y-%m-%d")
    
    return f"""
    <style>

    body{{
        font-family: "Segoe UI", sans-serif;
        background: linear-gradient(135deg, #c7d2fe, #dbeafe);
        padding: 30px;
    }}

    input[type="date"]{{
    width: 180px;
    padding: 12px;

    font-size: 16px;

    border: 2px solid #cbd5e1;
    border-radius: 12px;

    background: white;
    }}

    .filter-box button{{
    padding: 12px 20px;
    font-size: 15px;
    }}

    .transaksi-card{{
        background: white;
        padding: 20px;
        margin: 15px auto;

        width: 90%;
        max-width: 450px;

        border-radius: 15px;

        border-top: 5px solid #4f46e5;

        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}

    button{{
        background: #ef4444;
        color: white;
        border: none;
        padding: 10px 18px;
        border-radius: 10px;
        cursor: pointer;
    }}

    .kembali{{
        text-align:center;
        margin-top:15px;
        margin-bottom:15px;
    }}

    h1,h2,h3{{
        text-align:center;
    }}

    </style>

    <div style="text-align:center; margin-bottom:25px;">

        <h3>📅 Filter Tanggal</h3>

        <form method="GET">

        <input
            type="date"
            name="dari"
            max="{hari_ini}"
            value="{dari if dari else ''}"
        >

        <input
            type="date"
            name="sampai"
            max="{hari_ini}"
            value="{sampai if sampai else ''}"
        >

            <button type="submit">
                Tampilkan
            </button>

        </form>

    </div>
    
        <br>

        <h1>Rekapan Transaksi</h1>

        <h2>Total Pemasukan : {total_pemasukan_format}</h2>
        <h2>Total Pengeluaran : {total_pengeluaran_format}</h2>
        <h2>Saldo : {saldo_format}</h2>

        <div style="text-align:center;">
            <a href="/">
                <button>← Kembali</button>
            </a>
        </div>

    <br><br>

        <hr>

        <h2>Pemasukan</h2>
        {hasil_pemasukan}

        <hr>

        <h2>Pengeluaran</h2>
        {hasil_pengeluaran}


        """


@app.route("/hapus/<int:id>")
def hapus(id):

    conn = get_conn()
    cursor = conn.cursor()

    username = session["username"]

    cursor.execute(
        """
        DELETE FROM transaksi
        WHERE id=% AND username=%
        """,
        (id, username)
    )

    conn.commit()
    conn.close()

    return redirect("/rekapan")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = get_conn()
    cursor = conn.cursor()

    if request.method == "POST":

        nominal = request.form["nominal"]

        nominal = nominal.replace("Rp", "")
        nominal = nominal.replace(".", "")
        nominal = nominal.strip()

        keterangan = request.form["keterangan"]

        cursor.execute(
            """
            UPDATE transaksi
            SET nominal=%, keterangan=%
            WHERE id=%
            """,
            (nominal, keterangan, id)
        )

        conn.commit()
        conn.close()

        return redirect("/rekapan")


    username = session["username"]

    cursor.execute(
        """
        SELECT *
        FROM transaksi
        WHERE id=% AND username=%
        """,
        (id, username)
    )

    transaksi = cursor.fetchone()
    if not transaksi:
        conn.close()
        return "Data tidak ditemukan atau bukan milik Anda"

    if not transaksi:
        return "Data tidak ditemukan"
    
    nominal_format = f"Rp {int(transaksi[3]):,}".replace(",", ".")
    
    print("DATA EDIT")
    print(transaksi)

    conn.close()

    return f"""
    <style>

    body{{
        font-family:"Segoe UI",sans-serif;
        background:linear-gradient(135deg,#c7d2fe,#dbeafe);
        min-height:100vh;

        display:flex;
        justify-content:center;
        align-items:center;
    }}

    .card{{
        background:#eef2ff;
        width:450px;
        padding:35px;
        border-radius:20px;
        box-shadow:0 8px 25px rgba(0,0,0,0.15);
        text-align:center;
    }}

    h1{{
        color:#1e293b;
        margin-bottom:25px;
    }}

    input,select{{
        width:90%;
        padding:14px;
        margin:10px 0;
        border:2px solid #cbd5e1;
        border-radius:12px;
        font-size:15px;
    }}

    .save-btn{{
        background:#4f46e5;
        color:white;
        border:none;
        padding:14px 28px;
        border-radius:12px;
        cursor:pointer;
        font-size:16px;
        font-weight:bold;
    }}

    .back-btn{{
        background:#ef4444;
        color:white;
        border:none;
        padding:12px 24px;
        border-radius:12px;
        cursor:pointer;
        text-decoration:none;
        display:inline-block;
        margin-top:15px;
    }}

    </style>

    <div class="card">

        <h1>Edit Transaksi</h1>

        <form method="POST">

            <p>Jenis</p>

            <select name="jenis">

                <option value="pemasukan"
                    {"selected" if transaksi[2]=="pemasukan" else ""}>
                    Pemasukan
                </option>

                <option value="pengeluaran"
                    {"selected" if transaksi[2]=="pengeluaran" else ""}>
                    Pengeluaran
                </option>

            </select>

            <p>Nominal</p>

            <input
                type="text"
                id="nominal"
                name="nominal"
                value="{nominal_format}"
                required
            >

            <p>Keterangan</p>

            <input
                type="text"
                name="keterangan"
                value="{transaksi[4]}"
                required
            >

            <button class="save-btn" type="submit">
                Simpan Perubahan
            </button>

        </form>

        <a href="/rekapan" class="back-btn">
            ← Kembali
        </a>

    </div>

    <script>

    const nominalInput = document.getElementById("nominal");

    nominalInput.addEventListener("input", function() {{

        let angka = this.value.replace(/[^0-9]/g, "");

        if (angka === "") {{
            this.value = "";
            return;
        }}

        this.value =
            "Rp " +
            Number(angka).toLocaleString("id-ID");
    }});

    </script>
    """

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/cekuser")
def cekuser():

    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")

    data = cursor.fetchall()

    conn.close()

    return str(data)
    
if __name__ == "__main__":

    buat_database()
    
    app.run()


