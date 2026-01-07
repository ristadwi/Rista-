"""
=====================================================================
SERVER SIDE - Kalkulator Client-Server
=====================================================================
File ini berisi logika server yang menangani koneksi dari client
dan memproses operasi matematika (penambahan, pengurangan, 
perkalian, dan pembagian).

Struktur Objek:
1. CalculationEngine: Class yang mengenkapsulasi semua operasi matematika.
2. CalculatorServer: Class yang mengelola koneksi socket dan request handling.

Protokol Komunikasi:
- Request  : JSON {"operation": "add/sub/mul/div", "args": [num1, num2]}
- Response : JSON {"status": "success/error", "result": ..., "message": ...}
=====================================================================
"""

import socket
import json
import threading


# =====================================================================
# CLASS: CalculationEngine
# Deskripsi: Mengenkapsulasi semua logika perhitungan matematika.
#            Class ini bertanggung jawab untuk melakukan operasi
#            aritmatika dasar berdasarkan input yang diberikan.
# =====================================================================
class CalculationEngine:
    """
    Engine untuk melakukan perhitungan matematika.
    Mendukung operasi: penambahan, pengurangan, perkalian, pembagian.
    """

    def add(self, a: float, b: float) -> float:
        """
        Melakukan operasi penambahan.
        
        Args:
            a (float): Angka pertama
            b (float): Angka kedua
            
        Returns:
            float: Hasil penjumlahan a + b
        """
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """
        Melakukan operasi pengurangan.
        
        Args:
            a (float): Angka pertama (pengurang)
            b (float): Angka kedua (yang dikurangi)
            
        Returns:
            float: Hasil pengurangan a - b
        """
        return a - b

    def multiply(self, a: float, b: float) -> float:
        """
        Melakukan operasi perkalian.
        
        Args:
            a (float): Angka pertama
            b (float): Angka kedua
            
        Returns:
            float: Hasil perkalian a * b
        """
        return a * b

    def divide(self, a: float, b: float) -> float:
        """
        Melakukan operasi pembagian.
        
        Args:
            a (float): Angka pembilang (numerator)
            b (float): Angka penyebut (denominator)
            
        Returns:
            float: Hasil pembagian a / b
            
        Raises:
            ValueError: Jika b adalah 0 (pembagian dengan nol)
        """
        if b == 0:
            raise ValueError("Pembagian dengan nol tidak diperbolehkan!")
        return a / b

    def calculate(self, operation: str, args: list) -> dict:
        """
        Method utama untuk menjalankan operasi berdasarkan string nama operasi.
        
        Args:
            operation (str): Nama operasi ('add', 'sub', 'mul', 'div')
            args (list): List berisi dua angka [a, b]
            
        Returns:
            dict: Dictionary dengan status dan hasil atau pesan error
        """
        try:
            # Validasi jumlah argumen
            if len(args) != 2:
                return {
                    "status": "error",
                    "message": "Diperlukan tepat 2 argumen!"
                }

            a, b = float(args[0]), float(args[1])

            # Mapping operasi ke method yang sesuai
            operations_map = {
                "add": self.add,
                "sub": self.subtract,
                "mul": self.multiply,
                "div": self.divide
            }

            # Cek apakah operasi valid
            if operation not in operations_map:
                return {
                    "status": "error",
                    "message": f"Operasi '{operation}' tidak dikenal!"
                }

            # Jalankan operasi dan kembalikan hasil
            result = operations_map[operation](a, b)
            
            # Format hasil: bulatkan jika bilangan bulat
            if result == int(result):
                result = int(result)
            else:
                result = round(result, 10)  # Batasi presisi desimal

            return {
                "status": "success",
                "result": result
            }

        except ValueError as e:
            # Handle error seperti pembagian dengan nol
            return {
                "status": "error",
                "message": str(e)
            }
        except Exception as e:
            # Handle error umum lainnya
            return {
                "status": "error",
                "message": f"Terjadi kesalahan: {str(e)}"
            }


# =====================================================================
# CLASS: CalculatorServer
# Deskripsi: Mengelola koneksi socket TCP dan menangani request dari client.
#            Server ini berjalan secara multi-threaded sehingga dapat
#            melayani beberapa client secara bersamaan.
# =====================================================================
class CalculatorServer:
    """
    Server socket untuk menerima dan memproses request perhitungan dari client.
    Mendukung koneksi multi-client menggunakan threading.
    """

    def __init__(self, host: str = "localhost", port: int = 5000):
        """
        Inisialisasi server dengan host dan port yang ditentukan.
        
        Args:
            host (str): Alamat host server (default: localhost)
            port (int): Nomor port server (default: 5000)
        """
        self.host = host
        self.port = port
        self.engine = CalculationEngine()  # Instance dari engine perhitungan
        self.server_socket = None
        self.is_running = False

    def start(self):
        """
        Memulai server dan mulai mendengarkan koneksi dari client.
        Server akan terus berjalan sampai dihentikan secara manual.
        """
        # Membuat socket TCP/IP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Mengizinkan reuse alamat (berguna saat restart server)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind socket ke alamat dan port
        self.server_socket.bind((self.host, self.port))
        
        # Mulai mendengarkan koneksi (max 5 antrian)
        self.server_socket.listen(5)
        self.is_running = True

        print("=" * 60)
        print("   KALKULATOR SERVER")
        print("=" * 60)
        print(f"   Server berjalan di {self.host}:{self.port}")
        print("   Menunggu koneksi dari client...")
        print("   Tekan Ctrl+C untuk menghentikan server")
        print("=" * 60)

        try:
            while self.is_running:
                # Menerima koneksi baru dari client
                client_socket, client_address = self.server_socket.accept()
                print(f"\n[INFO] Koneksi baru dari: {client_address}")

                # Buat thread baru untuk menangani client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True  # Thread akan berhenti saat main thread berhenti
                client_thread.start()

        except KeyboardInterrupt:
            print("\n[INFO] Server dihentikan oleh user.")
        finally:
            self.stop()

    def stop(self):
        """
        Menghentikan server dan menutup socket.
        """
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
            print("[INFO] Server socket ditutup.")

    def _handle_client(self, client_socket: socket.socket, client_address: tuple):
        """
        Menangani komunikasi dengan satu client.
        Method ini berjalan di thread terpisah untuk setiap client.
        
        Args:
            client_socket: Socket yang terhubung dengan client
            client_address: Tuple berisi (ip, port) client
        """
        try:
            while True:
                # Terima data dari client (max 4096 bytes)
                data = client_socket.recv(4096)
                
                if not data:
                    # Client menutup koneksi
                    break

                # Decode data menjadi string dan parse JSON
                request_str = data.decode("utf-8")
                print(f"[REQUEST] Dari {client_address}: {request_str}")

                try:
                    # Parse JSON request
                    request = json.loads(request_str)
                    operation = request.get("operation", "")
                    args = request.get("args", [])

                    # Proses perhitungan menggunakan engine
                    response = self.engine.calculate(operation, args)

                except json.JSONDecodeError:
                    # Request tidak valid (bukan JSON)
                    response = {
                        "status": "error",
                        "message": "Format request tidak valid (bukan JSON)!"
                    }

                # Kirim response ke client
                response_str = json.dumps(response)
                print(f"[RESPONSE] Ke {client_address}: {response_str}")
                client_socket.send(response_str.encode("utf-8"))

        except ConnectionResetError:
            print(f"[INFO] Koneksi dengan {client_address} terputus.")
        except Exception as e:
            print(f"[ERROR] Error pada client {client_address}: {e}")
        finally:
            # Tutup koneksi dengan client
            client_socket.close()
            print(f"[INFO] Koneksi dengan {client_address} ditutup.")


# =====================================================================
# MAIN BLOCK
# Deskripsi: Entry point untuk menjalankan server.
#            Server akan dijalankan di localhost:5000.
# =====================================================================
if __name__ == "__main__":
    # Konfigurasi server
    HOST = "localhost"
    PORT = 5000

    # Buat instance server dan jalankan
    server = CalculatorServer(host=HOST, port=PORT)
    server.start()
