import json
from datetime import datetime

nama_kamu = input("siapa nama kamu ? ")


print("hello", nama_kamu, "SEMANGAT YA MENABUNGNYA")
print("----------")

transaksi_list = []

def simpan_data():
    with open("data_transaksi.json", "w") as file:
         json.dump(transaksi_list, file)
    pass

def load_data():
     global transaksi_list

     try :
          with open("data_transaksi.json", "r") as file:
               transaksi_list = json.load(file)
          pass
     except : 
            transaksi_list = []

load_data()

while True:
    print("1. Pemasukan")
    print("2. Pengeluaran")
    print("3. Rekapan")
    print("4. Hapus Transaksi")
    print("5. Keluar")

    pilihan = input("Masukan pilihanmu : ")

    tanggal = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    if pilihan == "1" :
        
        while True:
            nominal = int(input("masukan jumlah uang masuk kamu hari ini : "))
            keterangan = input("Keterangan : ")
            print("Pemasukan:", nominal)

            transaksi = {
                "jenis": "pemasukan",
                "nominal": nominal,
                "keterangan": keterangan,
                "tanggal": tanggal
        }
            
            transaksi_list.append(transaksi)
            simpan_data()
        
            lagi = input("Apakah kamu ingin menambahkan pemasukanmu lagi ? (y/n) : ")
            if lagi.lower() == "n":
                break        

    if pilihan == "2" :

        while True:
            nominal = int (input("masukan jumlah keluar kamu hari ini : "))
            keterangan = input("Keterangan : ")
            print("Pengeluaran:", nominal)

            transaksi = {
                "jenis": "pengeluaran",
                "nominal": nominal,
                "keterangan": keterangan,
                "tanggal": tanggal
        }
            transaksi_list.append(transaksi)
            simpan_data()

            lagi = input("Apakah kmu ingin menambahkan pengeluaranmu lagi ? (y/n) : ")
            if lagi.lower() == "n":
                 break

    if pilihan == "3" :
        
        print("\n====== REKAPAN TRANSAKSI ======")

        jumlah_transaksi = len(transaksi_list)
        print("Jumlah Transaksi :", jumlah_transaksi)

        total_pemasukan = 0
        total_pengeluaran = 0
        if len(transaksi_list) == 0:
            print(" Kamu belum ada melakukan transaksi apapun nih !! \n jangan lupa untuk di rekap ya pemasukan dan pengeluarannya")

        nomor = 1

        for transaksi in transaksi_list:
            print(f"[{nomor}]")
            print("Tanggal :", transaksi["tanggal"])
            print("Jenis :", transaksi["jenis"])
            uang = f"{transaksi['nominal']:,}".replace(",",".")
            print("Nominal : Rp ", uang)
            print("Keterangan :", transaksi["keterangan"])
            print("===============================")
            nomor = nomor + 1


            if transaksi["jenis"] == "pemasukan":
                      total_pemasukan = total_pemasukan + transaksi["nominal"]
            if transaksi["jenis"] == "pengeluaran":
                      total_pengeluaran = total_pengeluaran + transaksi["nominal"]

        saldo_akhir = total_pemasukan - total_pengeluaran
        print()
        print("Tanggal :", transaksi["tanggal"])
        uang = f"{total_pemasukan:,}".replace(",",".")
        print("Total Pemasukan : RP ",uang )
        uang = f"{total_pengeluaran:,}".replace(",",".")
        print("Total Pengeluaran : RP ",uang)
        uang = f"{saldo_akhir:,}".replace(",",".")
        print("Saldo Akhir : RP", uang)
        print("------------------------------")


    if pilihan == "4":
        nomor = 1

        for transaksi in transaksi_list:
            print(f"[{nomor}] {transaksi['keterangan']}")
            nomor = nomor + 1

        nomor_transaksi = input("Masukan Nomor Transaksi Yang Ingin Dihapus : ")

        if nomor_transaksi.isdigit():
            nomor_transaksi = int(nomor_transaksi)

            if 1 <= nomor_transaksi <= len(transaksi_list):
                del transaksi_list[nomor_transaksi - 1]
                print("Transaksi berhasil dihapus.")
            else:
                print("Nomor transaksi tidak valid.")
        else:
            print("Input tidak valid.")


    
    if pilihan == "5" :
        print("Semangat ya dalam menabungnya")
        break


