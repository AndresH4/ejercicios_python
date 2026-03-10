import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

def conectar_db():
    conexion = sqlite3.connect("finanzas.db")
    cursor = conexion.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS movimientos 
                   (id INTEGER PRIMARY KEY, fecha TEXT, concepto TEXT, monto REAL, tipo TEXT)''')
    conexion.commit()
    return conexion

class FinanzasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Finanzas - Sin Sobregiro")
        self.root.geometry("700x550")

        self.var_concepto = tk.StringVar()
        self.var_monto = tk.StringVar()
        self.var_tipo = tk.StringVar(value="Ingreso")
        self.saldo_actual_num = 0.0  # Variable numérica para validación interna

        # --- Interfaz ---
        header_frame = tk.Frame(self.root, bg="#2c3e50", pady=10)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="Disponible:", font=("Arial", 14), bg="#2c3e50", fg="white").pack(side="left", padx=20)
        self.label_saldo = tk.Label(header_frame, text="$0.00", font=("Arial", 18, "bold"), bg="#2c3e50", fg="#2ecc71")
        self.label_saldo.pack(side="left")

        frame = tk.LabelFrame(self.root, text="Registrar Movimiento", padx=10, pady=10)
        frame.pack(pady=20, fill="x", padx=20)

        tk.Label(frame, text="Concepto:").grid(row=0, column=0)
        tk.Entry(frame, textvariable=self.var_concepto).grid(row=0, column=1, padx=5)

        tk.Label(frame, text="Monto:").grid(row=0, column=2)
        tk.Entry(frame, textvariable=self.var_monto, width=10).grid(row=0, column=3, padx=5)

        tk.OptionMenu(frame, self.var_tipo, "Ingreso", "Gasto").grid(row=0, column=4, padx=5)
        tk.Button(frame, text="Guardar", command=self.agregar, bg="#2980b9", fg="white").grid(row=0, column=5, padx=10)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Fecha", "Concepto", "Monto", "Tipo"), show='headings')
        self.tree.heading("ID", text="ID"); self.tree.heading("Monto", text="Monto")
        self.tree.heading("Concepto", text="Concepto"); self.tree.heading("Tipo", text="Tipo")
        self.tree.pack(pady=10, fill="both", expand=True, padx=20)

        self.actualizar_vista()

    def agregar(self):
        try:
            concepto = self.var_concepto.get()
            monto = float(self.var_monto.get())
            tipo = self.var_tipo.get()

            if monto <= 0:
                messagebox.showwarning("Error", "El monto debe ser mayor a 0")
                return

            # --- VALIDACIÓN DE SALDO NEGATIVO ---
            if tipo == "Gasto" and monto > self.saldo_actual_num:
                messagebox.showerror("Fondos Insuficientes", 
                    f"No puedes gastar ${monto:,.2f} porque tu saldo actual es ${self.saldo_actual_num:,.2f}")
                return
            # ------------------------------------

            conn = conectar_db()
            cursor = conn.cursor()
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            cursor.execute("INSERT INTO movimientos (fecha, concepto, monto, tipo) VALUES (?, ?, ?, ?)",
                           (fecha, concepto, monto, tipo))
            conn.commit()
            conn.close()

            self.var_concepto.set(""); self.var_monto.set("")
            self.actualizar_vista()
            
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número válido en el monto")

    def actualizar_vista(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movimientos ORDER BY id DESC")
        
        total = 0.0
        for fila in cursor.fetchall():
            self.tree.insert("", "end", values=fila)
            if fila[4] == "Ingreso": total += fila[3]
            else: total -= fila[3]
        
        conn.close()
        self.saldo_actual_num = total # Guardamos el valor para la próxima validación
        self.label_saldo.config(text=f"${total:,.2f}")

if __name__ == "__main__":
    conectar_db()
    root = tk.Tk()
    app = FinanzasApp(root)
    root.mainloop()