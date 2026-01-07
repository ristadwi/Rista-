"""
=====================================================================
CLIENT SIDE - Kalkulator Client-Server
=====================================================================
File ini berisi antarmuka pengguna (GUI) untuk kalkulator dan
logika untuk berkomunikasi dengan server.

Struktur Objek:
1. NetworkClient: Class yang mengelola koneksi socket ke server.
2. CalculatorUI: Class yang mengelola antarmuka grafis (GUI) menggunakan Tkinter.

Fitur UI/UX:
- Desain modern dengan warna gelap (dark theme)
- Tombol dengan efek hover
- Display yang jelas untuk input dan hasil
- Feedback visual untuk operasi sukses/gagal
=====================================================================
"""

import tkinter as tk
from tkinter import messagebox
import socket
import json


# =====================================================================
# CLASS: NetworkClient
# Deskripsi: Mengelola koneksi socket ke server kalkulator.
#            Class ini bertanggung jawab untuk mengirim request
#            perhitungan dan menerima response dari server.
# =====================================================================
class NetworkClient:
    """
    Client untuk berkomunikasi dengan server kalkulator via socket TCP.
    Menangani koneksi, pengiriman request, dan penerimaan response.
    """

    def __init__(self, host: str = "localhost", port: int = 5000):
        """
        Inisialisasi client dengan alamat server.
        
        Args:
            host (str): Alamat host server (default: localhost)
            port (int): Nomor port server (default: 5000)
        """
        self.host = host
        self.port = port
        self.socket = None
        self.is_connected = False

    def connect(self) -> bool:
        """
        Membuat koneksi ke server.
        
        Returns:
            bool: True jika koneksi berhasil, False jika gagal
        """
        try:
            # Buat socket TCP baru
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)  # Timeout 5 detik
            
            # Hubungkan ke server
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            print(f"[INFO] Terhubung ke server {self.host}:{self.port}")
            return True
            
        except socket.timeout:
            print("[ERROR] Timeout saat menghubungi server!")
            return False
        except ConnectionRefusedError:
            print("[ERROR] Server tidak dapat dihubungi!")
            return False
        except Exception as e:
            print(f"[ERROR] Gagal terhubung: {e}")
            return False

    def disconnect(self):
        """
        Memutuskan koneksi dari server.
        """
        if self.socket:
            self.socket.close()
            self.is_connected = False
            print("[INFO] Koneksi ditutup.")

    def send_calculation(self, operation: str, a: float, b: float) -> dict:
        """
        Mengirim request perhitungan ke server dan menerima response.
        
        Args:
            operation (str): Jenis operasi ('add', 'sub', 'mul', 'div')
            a (float): Angka pertama
            b (float): Angka kedua
            
        Returns:
            dict: Response dari server dengan status dan hasil
        """
        # Pastikan terhubung ke server
        if not self.is_connected:
            if not self.connect():
                return {
                    "status": "error",
                    "message": "Tidak dapat terhubung ke server!\nPastikan server sudah berjalan."
                }

        try:
            # Buat request dalam format JSON
            request = {
                "operation": operation,
                "args": [a, b]
            }
            request_str = json.dumps(request)

            # Kirim request ke server
            self.socket.send(request_str.encode("utf-8"))

            # Terima response dari server
            response_data = self.socket.recv(4096)
            response = json.loads(response_data.decode("utf-8"))
            
            return response

        except socket.timeout:
            self.is_connected = False
            return {
                "status": "error",
                "message": "Timeout menunggu response dari server!"
            }
        except ConnectionResetError:
            self.is_connected = False
            return {
                "status": "error",
                "message": "Koneksi ke server terputus!"
            }
        except Exception as e:
            self.is_connected = False
            return {
                "status": "error",
                "message": f"Terjadi kesalahan: {str(e)}"
            }


# =====================================================================
# CLASS: CalculatorUI
# Deskripsi: Antarmuka grafis (GUI) untuk kalkulator menggunakan Tkinter.
#            Class ini menerapkan prinsip UI/UX dengan desain yang bersih,
#            modern, dan mudah digunakan.
# =====================================================================
class CalculatorUI:
    """
    GUI Kalkulator dengan desain modern menggunakan Tkinter.
    Mendukung operasi: penambahan, pengurangan, perkalian, pembagian.
    """

    # Konstanta warna untuk tema gelap (dark theme)
    COLORS = {
        "bg_main": "#1a1a2e",          # Background utama (dark blue)
        "bg_display": "#16213e",        # Background display
        "bg_button": "#0f3460",         # Background tombol angka
        "bg_operator": "#e94560",       # Background tombol operator
        "bg_equal": "#00bf63",          # Background tombol sama dengan
        "bg_clear": "#ff6b35",          # Background tombol clear
        "text_light": "#eaeaea",        # Teks terang
        "text_dim": "#a0a0a0",          # Teks redup
        "hover_button": "#1a4a7a",      # Hover tombol angka
        "hover_operator": "#ff6b7a",    # Hover tombol operator
    }

    def __init__(self, client: NetworkClient):
        """
        Inisialisasi UI Kalkulator.
        
        Args:
            client (NetworkClient): Instance NetworkClient untuk komunikasi server
        """
        self.client = client
        
        # State untuk menyimpan input user
        self.current_input = ""      # Input yang sedang diketik
        self.first_operand = None    # Operand pertama
        self.current_operator = None # Operator yang dipilih
        self.should_reset = False    # Flag untuk reset setelah hasil

        # Setup window utama
        self.root = tk.Tk()
        self.root.title("Kalkulator Client-Server")
        self.root.geometry("380x580")
        self.root.resizable(False, False)
        self.root.configure(bg=self.COLORS["bg_main"])

        # Coba koneksi awal ke server
        self.client.connect()

        # Build UI components
        self._create_header()
        self._create_display()
        self._create_buttons()
        self._create_footer()

        # Bind keyboard events
        self._bind_keyboard()

    def _create_header(self):
        """
        Membuat header aplikasi dengan judul dan status koneksi.
        """
        header_frame = tk.Frame(self.root, bg=self.COLORS["bg_main"])
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        # Judul aplikasi
        title_label = tk.Label(
            header_frame,
            text="🖩 Kalkulator",
            font=("Segoe UI", 24, "bold"),
            fg=self.COLORS["text_light"],
            bg=self.COLORS["bg_main"]
        )
        title_label.pack(anchor="w")

        # Subtitle
        subtitle_label = tk.Label(
            header_frame,
            text="Client-Server | Socket Programming",
            font=("Segoe UI", 10),
            fg=self.COLORS["text_dim"],
            bg=self.COLORS["bg_main"]
        )
        subtitle_label.pack(anchor="w")

    def _create_display(self):
        """
        Membuat area display untuk menampilkan input dan hasil.
        Display terdiri dari dua bagian:
        - Expression label: menampilkan ekspresi yang sedang dihitung
        - Result display: menampilkan angka input/hasil
        """
        display_frame = tk.Frame(
            self.root,
            bg=self.COLORS["bg_display"],
            padx=20,
            pady=15
        )
        display_frame.pack(fill=tk.X, padx=20, pady=10)

        # Label untuk menampilkan ekspresi (operand dan operator)
        self.expression_label = tk.Label(
            display_frame,
            text="",
            font=("Consolas", 14),
            fg=self.COLORS["text_dim"],
            bg=self.COLORS["bg_display"],
            anchor="e"
        )
        self.expression_label.pack(fill=tk.X)

        # Label untuk menampilkan angka input / hasil
        self.result_display = tk.Label(
            display_frame,
            text="0",
            font=("Consolas", 36, "bold"),
            fg=self.COLORS["text_light"],
            bg=self.COLORS["bg_display"],
            anchor="e"
        )
        self.result_display.pack(fill=tk.X)

    def _create_buttons(self):
        """
        Membuat grid tombol kalkulator.
        Layout:
        [C] [±] [%] [÷]
        [7] [8] [9] [×]
        [4] [5] [6] [−]
        [1] [2] [3] [+]
        [0    ] [.] [=]
        """
        buttons_frame = tk.Frame(self.root, bg=self.COLORS["bg_main"])
        buttons_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Konfigurasi grid
        for i in range(5):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            buttons_frame.grid_columnconfigure(i, weight=1)

        # Definisi tombol: (text, row, col, colspan, type)
        button_layout = [
            # Row 0: Clear, sign, percent, divide
            ("C", 0, 0, 1, "clear"),
            ("±", 0, 1, 1, "function"),
            ("⌫", 0, 2, 1, "function"),
            ("÷", 0, 3, 1, "operator"),
            
            # Row 1: 7, 8, 9, multiply
            ("7", 1, 0, 1, "number"),
            ("8", 1, 1, 1, "number"),
            ("9", 1, 2, 1, "number"),
            ("×", 1, 3, 1, "operator"),
            
            # Row 2: 4, 5, 6, subtract
            ("4", 2, 0, 1, "number"),
            ("5", 2, 1, 1, "number"),
            ("6", 2, 2, 1, "number"),
            ("−", 2, 3, 1, "operator"),
            
            # Row 3: 1, 2, 3, add
            ("1", 3, 0, 1, "number"),
            ("2", 3, 1, 1, "number"),
            ("3", 3, 2, 1, "number"),
            ("+", 3, 3, 1, "operator"),
            
            # Row 4: 0 (span 2), decimal, equals
            ("0", 4, 0, 2, "number"),
            (".", 4, 2, 1, "number"),
            ("=", 4, 3, 1, "equal"),
        ]

        # Buat setiap tombol
        for (text, row, col, colspan, btn_type) in button_layout:
            self._create_button(buttons_frame, text, row, col, colspan, btn_type)

    def _create_button(self, parent, text: str, row: int, col: int, 
                       colspan: int, btn_type: str):
        """
        Membuat satu tombol dengan styling sesuai tipe.
        
        Args:
            parent: Widget parent untuk tombol
            text (str): Teks yang ditampilkan di tombol
            row (int): Posisi baris di grid
            col (int): Posisi kolom di grid
            colspan (int): Jumlah kolom yang di-span
            btn_type (str): Tipe tombol ('number', 'operator', 'equal', 'clear', 'function')
        """
        # Tentukan warna berdasarkan tipe
        if btn_type == "number":
            bg_color = self.COLORS["bg_button"]
            hover_color = self.COLORS["hover_button"]
        elif btn_type == "operator":
            bg_color = self.COLORS["bg_operator"]
            hover_color = self.COLORS["hover_operator"]
        elif btn_type == "equal":
            bg_color = self.COLORS["bg_equal"]
            hover_color = "#00d970"
        elif btn_type == "clear":
            bg_color = self.COLORS["bg_clear"]
            hover_color = "#ff8555"
        else:  # function
            bg_color = self.COLORS["bg_button"]
            hover_color = self.COLORS["hover_button"]

        # Buat tombol
        button = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 20, "bold"),
            fg=self.COLORS["text_light"],
            bg=bg_color,
            activebackground=hover_color,
            activeforeground=self.COLORS["text_light"],
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda t=text: self._on_button_click(t)
        )

        # Tempatkan di grid
        button.grid(
            row=row, 
            column=col, 
            columnspan=colspan,
            sticky="nsew",
            padx=3,
            pady=3
        )

        # Bind hover effects
        button.bind("<Enter>", lambda e, btn=button, c=hover_color: btn.configure(bg=c))
        button.bind("<Leave>", lambda e, btn=button, c=bg_color: btn.configure(bg=c))

    def _create_footer(self):
        """
        Membuat footer dengan status koneksi server.
        """
        footer_frame = tk.Frame(self.root, bg=self.COLORS["bg_main"])
        footer_frame.pack(fill=tk.X, padx=20, pady=(5, 15))

        # Status indikator
        status_text = "● Terhubung ke Server" if self.client.is_connected else "○ Tidak Terhubung"
        status_color = "#00bf63" if self.client.is_connected else "#e94560"

        self.status_label = tk.Label(
            footer_frame,
            text=status_text,
            font=("Segoe UI", 9),
            fg=status_color,
            bg=self.COLORS["bg_main"]
        )
        self.status_label.pack(side=tk.LEFT)

        # Info port
        port_label = tk.Label(
            footer_frame,
            text=f"localhost:{self.client.port}",
            font=("Consolas", 9),
            fg=self.COLORS["text_dim"],
            bg=self.COLORS["bg_main"]
        )
        port_label.pack(side=tk.RIGHT)

    def _bind_keyboard(self):
        """
        Mengikat event keyboard untuk input angka dan operasi.
        """
        # Bind angka 0-9
        for i in range(10):
            self.root.bind(str(i), lambda e, n=str(i): self._on_button_click(n))
        
        # Bind operator
        self.root.bind("+", lambda e: self._on_button_click("+"))
        self.root.bind("-", lambda e: self._on_button_click("−"))
        self.root.bind("*", lambda e: self._on_button_click("×"))
        self.root.bind("/", lambda e: self._on_button_click("÷"))
        
        # Bind lainnya
        self.root.bind(".", lambda e: self._on_button_click("."))
        self.root.bind("<Return>", lambda e: self._on_button_click("="))
        self.root.bind("<BackSpace>", lambda e: self._on_button_click("⌫"))
        self.root.bind("<Escape>", lambda e: self._on_button_click("C"))

    def _on_button_click(self, text: str):
        """
        Handler untuk setiap klik tombol.
        
        Args:
            text (str): Teks/simbol tombol yang diklik
        """
        # Jika perlu reset setelah hasil sebelumnya
        if self.should_reset and text not in ["C", "=", "+", "−", "×", "÷"]:
            self.current_input = ""
            self.should_reset = False

        if text == "C":
            # Clear semua
            self._clear_all()

        elif text == "⌫":
            # Backspace - hapus karakter terakhir
            self.current_input = self.current_input[:-1]
            self._update_display()

        elif text == "±":
            # Toggle tanda positif/negatif
            self._toggle_sign()

        elif text in ["+", "−", "×", "÷"]:
            # Operator diklik
            self._handle_operator(text)

        elif text == "=":
            # Hitung hasil
            self._calculate_result()

        elif text == ".":
            # Titik desimal
            if "." not in self.current_input:
                if not self.current_input:
                    self.current_input = "0"
                self.current_input += "."
                self._update_display()

        else:
            # Angka diklik
            if self.should_reset:
                self.current_input = ""
                self.should_reset = False
            
            # Cegah angka terlalu panjang
            if len(self.current_input.replace(".", "").replace("-", "")) < 12:
                self.current_input += text
                self._update_display()

    def _clear_all(self):
        """
        Reset semua state kalkulator ke kondisi awal.
        """
        self.current_input = ""
        self.first_operand = None
        self.current_operator = None
        self.should_reset = False
        self.expression_label.config(text="")
        self.result_display.config(text="0", fg=self.COLORS["text_light"])

    def _toggle_sign(self):
        """
        Toggle tanda positif/negatif pada angka yang sedang diinput.
        """
        if self.current_input:
            if self.current_input.startswith("-"):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = "-" + self.current_input
            self._update_display()

    def _handle_operator(self, operator: str):
        """
        Menangani ketika operator diklik.
        
        Args:
            operator (str): Simbol operator ('+', '−', '×', '÷')
        """
        if self.current_input:
            # Jika sudah ada operand pertama, hitung dulu
            if self.first_operand is not None and self.current_operator:
                self._calculate_result()
            
            # Simpan operand pertama
            try:
                self.first_operand = float(self.current_input)
            except ValueError:
                return
            
            self.current_input = ""
            
        if self.first_operand is not None:
            self.current_operator = operator
            # Update expression label
            display_num = int(self.first_operand) if self.first_operand == int(self.first_operand) else self.first_operand
            self.expression_label.config(text=f"{display_num} {operator}")

        self.should_reset = False

    def _calculate_result(self):
        """
        Mengirim perhitungan ke server dan menampilkan hasil.
        """
        if self.first_operand is None or not self.current_operator:
            return

        # Ambil operand kedua
        try:
            if self.current_input:
                second_operand = float(self.current_input)
            else:
                second_operand = self.first_operand
        except ValueError:
            return

        # Mapping simbol ke kode operasi
        operator_map = {
            "+": "add",
            "−": "sub",
            "×": "mul",
            "÷": "div"
        }
        operation = operator_map.get(self.current_operator)

        # Update expression dengan operand kedua
        display_first = int(self.first_operand) if self.first_operand == int(self.first_operand) else self.first_operand
        display_second = int(second_operand) if second_operand == int(second_operand) else second_operand
        self.expression_label.config(
            text=f"{display_first} {self.current_operator} {display_second} ="
        )

        # Kirim ke server
        response = self.client.send_calculation(operation, self.first_operand, second_operand)

        # Update status koneksi
        self._update_connection_status()

        if response["status"] == "success":
            # Tampilkan hasil
            result = response["result"]
            self.current_input = str(result)
            self.result_display.config(
                text=self._format_number(result),
                fg=self.COLORS["text_light"]
            )
            self.first_operand = result
        else:
            # Tampilkan error
            self.result_display.config(
                text="Error",
                fg=self.COLORS["bg_operator"]
            )
            messagebox.showerror("Error", response.get("message", "Terjadi kesalahan!"))
            self.current_input = ""
            self.first_operand = None

        self.current_operator = None
        self.should_reset = True

    def _update_display(self):
        """
        Update tampilan display dengan input saat ini.
        """
        if self.current_input:
            try:
                num = float(self.current_input)
                self.result_display.config(
                    text=self._format_number(num) if "." not in self.current_input else self.current_input,
                    fg=self.COLORS["text_light"]
                )
            except ValueError:
                self.result_display.config(text=self.current_input)
        else:
            self.result_display.config(text="0", fg=self.COLORS["text_light"])

    def _format_number(self, number) -> str:
        """
        Format angka untuk tampilan yang lebih baik.
        
        Args:
            number: Angka yang akan diformat
            
        Returns:
            str: String angka yang sudah diformat
        """
        if isinstance(number, float) and number == int(number):
            return str(int(number))
        elif isinstance(number, float):
            # Batasi desimal dan hapus trailing zeros
            formatted = f"{number:.10f}".rstrip("0").rstrip(".")
            return formatted
        return str(number)

    def _update_connection_status(self):
        """
        Update label status koneksi berdasarkan state client.
        """
        if self.client.is_connected:
            self.status_label.config(text="● Terhubung ke Server", fg="#00bf63")
        else:
            self.status_label.config(text="○ Tidak Terhubung", fg="#e94560")

    def run(self):
        """
        Menjalankan main loop aplikasi.
        """
        # Center window di layar
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")

        # Jalankan aplikasi
        self.root.mainloop()

        # Tutup koneksi saat aplikasi ditutup
        self.client.disconnect()


# =====================================================================
# MAIN BLOCK
# Deskripsi: Entry point untuk menjalankan aplikasi kalkulator client.
#            Membuat instance NetworkClient dan CalculatorUI, lalu
#            menjalankan main loop GUI.
# =====================================================================
if __name__ == "__main__":
    # Konfigurasi koneksi ke server
    SERVER_HOST = "localhost"
    SERVER_PORT = 5000

    # Buat instance client untuk koneksi ke server
    network_client = NetworkClient(host=SERVER_HOST, port=SERVER_PORT)

    # Buat dan jalankan UI
    calculator = CalculatorUI(client=network_client)
    calculator.run()
