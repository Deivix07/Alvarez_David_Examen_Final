import tkinter as tk
from tkinter import messagebox, ttk
import os
import webbrowser
from reportlab.pdfgen import canvas
from supabase_config import supabase
import time
from datetime import datetime

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Pedidos")
        self.root.geometry("900x600")
        self.usuario_actual = None
        self.mostrar_login()

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpiar_ventana()

        tk.Label(self.root, text="Inicio de Sesión", font=("Arial", 16)).pack(pady=20)

        tk.Label(self.root, text="Email:").pack(pady=5)
        email_entry = tk.Entry(self.root)
        email_entry.pack(pady=5)

        tk.Label(self.root, text="Contraseña:").pack(pady=5)
        password_entry = tk.Entry(self.root, show="*")
        password_entry.pack(pady=5)

        def login():
            email = email_entry.get()
            password = password_entry.get()
            try:
                respuesta = supabase.auth.sign_in_with_password({"email": email, "password": password})
                self.usuario_actual = respuesta.user
                messagebox.showinfo("Éxito", f"Bienvenido, {self.usuario_actual.email}")
                self.mostrar_menu_principal()
            except Exception as e:
                messagebox.showerror("Error", "Inicio de sesión fallido")

        tk.Button(self.root, text="Iniciar Sesión", command=login).pack(pady=10)
        tk.Button(self.root, text="Registrarse", command=self.mostrar_registro).pack(pady=10)

    def mostrar_registro(self):
        self.limpiar_ventana()

        tk.Label(self.root, text="Registro de Usuario", font=("Arial", 16)).pack(pady=20)

        tk.Label(self.root, text="Email:").pack(pady=5)
        email_entry = tk.Entry(self.root)
        email_entry.pack(pady=5)

        tk.Label(self.root, text="Contraseña:").pack(pady=5)
        password_entry = tk.Entry(self.root, show="*")
        password_entry.pack(pady=5)

        def registrar():
            email = email_entry.get()
            password = password_entry.get()
            try:
                respuesta = supabase.auth.sign_up({"email": email, "password": password})
                messagebox.showinfo("Éxito", "Usuario registrado correctamente")
                self.mostrar_login()
            except Exception as e:
                messagebox.showerror("Error", "No se pudo registrar el usuario")

        tk.Button(self.root, text="Registrar", command=registrar).pack(pady=10)
        tk.Button(self.root, text="Volver", command=self.mostrar_login).pack(pady=10)

    def mostrar_menu_principal(self):
        self.limpiar_ventana()

        tk.Label(self.root, text=f"Bienvenido, {self.usuario_actual.email}", font=("Arial", 16)).pack(pady=20)

        tk.Button(self.root, text="Registrar Pedido", command=self.mostrar_registro_pedido).pack(pady=10)
        tk.Button(self.root, text="Ver Pedidos", command=self.mostrar_lista_pedidos).pack(pady=10)
        tk.Button(self.root, text="Cerrar Sesión", command=self.mostrar_login).pack(pady=10)

    def mostrar_registro_pedido(self):
        self.limpiar_ventana()
        self.root.grid_columnconfigure(1, weight=1)

        tk.Label(self.root, text="Registrar Pedido", font=("Arial", 16)).grid(row=0, column=0, columnspan=4, pady=10)

        # Campos principales
        tk.Label(self.root, text="Cliente:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        cliente_entry = tk.Entry(self.root)
        cliente_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        tk.Label(self.root, text="Teléfono:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        telefono_entry = tk.Entry(self.root)
        telefono_entry.grid(row=1, column=3, padx=5, pady=5, sticky=tk.EW)

        tk.Label(self.root, text="Fecha de Entrega (dd/mm/aaaa):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        fecha_entry = tk.Entry(self.root)
        fecha_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        # Treeview para productos
        tree = ttk.Treeview(self.root, columns=("Cantidad", "Descripción", "Valor Unitario", "Valor Total"), show="headings")
        tree.heading("Cantidad", text="Cantidad")
        tree.heading("Descripción", text="Descripción")
        tree.heading("Valor Unitario", text="Valor Unitario")
        tree.heading("Valor Total", text="Valor Total")
        tree.grid(row=3, column=0, columnspan=4, padx=5, pady=10, sticky=tk.NSEW)

        # Botones para productos
        tk.Label(self.root, text="Cantidad:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        cantidad_entry = tk.Entry(self.root)
        cantidad_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)

        tk.Label(self.root, text="Descripción:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        descripcion_entry = tk.Entry(self.root)
        descripcion_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.EW)

        tk.Label(self.root, text="Valor Unitario:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
        valor_unitario_entry = tk.Entry(self.root)
        valor_unitario_entry.grid(row=6, column=1, padx=5, pady=5, sticky=tk.EW)

        def agregar_producto():
            cantidad = cantidad_entry.get()
            descripcion = descripcion_entry.get()
            valor_unitario = valor_unitario_entry.get()

            if not (cantidad and descripcion and valor_unitario):
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return

            valor_total = int(cantidad) * float(valor_unitario)
            # Formatear los valores con dos decimales
            tree.insert("", "end", values=(cantidad, descripcion, f"{float(valor_unitario):.2f}", f"{valor_total:.2f}"))
            actualizar_totales()

        def eliminar_producto():
            selected_item = tree.selection()
            if selected_item:
                tree.delete(selected_item)
                actualizar_totales()
            else:
                messagebox.showerror("Error", "Selecciona un producto para eliminar")

        def actualizar_totales():
            total = sum(float(tree.item(item, "values")[3]) for item in tree.get_children())
            total_label.config(text=f"Total: {total:.2f}")
            saldo_label.config(text=f"Saldo: {total - float(abono_entry.get() or 0):.2f}")

        tk.Button(self.root, text="Agregar Producto", command=agregar_producto).grid(row=7, column=1, padx=5, pady=10, sticky=tk.EW)
        tk.Button(self.root, text="Eliminar Producto", command=eliminar_producto).grid(row=7, column=2, padx=5, pady=10, sticky=tk.EW)

        # Totales y abono
        tk.Label(self.root, text="Abono:").grid(row=8, column=0, padx=5, pady=5, sticky=tk.W)
        abono_entry = tk.Entry(self.root)
        abono_entry.grid(row=8, column=1, padx=5, pady=5, sticky=tk.EW)
        abono_entry.bind("<KeyRelease>", lambda e: actualizar_totales())

        total_label = tk.Label(self.root, text="Total: 0")
        total_label.grid(row=9, column=0, padx=5, pady=5, sticky=tk.W)

        saldo_label = tk.Label(self.root, text="Saldo: 0")
        saldo_label.grid(row=9, column=1, padx=5, pady=5, sticky=tk.W)

        def guardar_pedido():
            cliente = cliente_entry.get()
            telefono = telefono_entry.get()
            fecha_ingresada = fecha_entry.get()
            abono = abono_entry.get() or 0

            # Convertir fecha al formato aaaa-mm-dd
            try:
                fecha_formateada = datetime.strptime(fecha_ingresada, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "La fecha debe estar en formato dd/mm/aaaa")
                return

            productos = [tree.item(item, "values") for item in tree.get_children()]
            if not (cliente and telefono and fecha_formateada and productos):
                messagebox.showerror("Error", "Completa todos los campos y agrega productos")
                return

            # Generar el PDF y obtener su URL
            pdf_url = generar_pdf(cliente, telefono, fecha_formateada, productos, abono)

            # Guardar los datos en la base de datos
            supabase.table("pedidos").insert({
                "cliente": cliente,
                "telefono": telefono,
                "fecha_entrega": fecha_formateada,  # Formato aaaa-mm-dd
                "pdf_url": pdf_url
            }).execute()

            messagebox.showinfo("Éxito", "Pedido guardado correctamente")
            self.mostrar_menu_principal()

        tk.Button(self.root, text="Guardar Pedido", command=guardar_pedido).grid(row=10, column=1, padx=5, pady=10, sticky=tk.EW)
        tk.Button(self.root, text="Volver", command=self.mostrar_menu_principal).grid(row=10, column=2, padx=5, pady=10, sticky=tk.EW)

        def generar_pdf(cliente, telefono, fecha_entrega, productos, abono):
            
            fecha_formateada = datetime.strptime(fecha_entrega, "%Y-%m-%d").strftime("%d/%m/%Y")
            
            timestamp = int(time.time())
            pdf_filename = f"pedido_{cliente}_{timestamp}.pdf"
           
            c = canvas.Canvas(pdf_filename)
            c.drawString(100, 750, f"Cliente: {cliente}")
            c.drawString(100, 730, f"Teléfono: {telefono}")
            c.drawString(100, 710, f"Fecha de Entrega: {fecha_formateada}")

            y = 680
            for producto in productos:
                cantidad, descripcion, valor_unitario, valor_total = producto
                c.drawString(100, y, f"{cantidad} - {descripcion} - ${float(valor_unitario):.2f} - ${float(valor_total):.2f}")
                y -= 20

            total = sum(float(p[3]) for p in productos)
            c.drawString(100, y, f"Total: ${total:.2f}")
            y -= 20
            c.drawString(100, y, f"Abono: ${float(abono):.2f}")
            y -= 20
            c.drawString(100, y, f"Saldo: ${total - float(abono):.2f}")
            c.save()

            # Subir el archivo a Supabase Storage
            with open(pdf_filename, "rb") as f:
                response = supabase.storage.from_("pedidos_pdfs").upload(
                    f"pedidos/{pdf_filename}",
                    f,
                    {"content-type": "application/pdf"}
        )

            # Eliminar el archivo local
            os.remove(pdf_filename)

            # Retornar la URL pública del archivo
            return supabase.storage.from_("pedidos_pdfs").get_public_url(f"pedidos/{pdf_filename}")

    def mostrar_lista_pedidos(self):
        self.limpiar_ventana()
        tk.Label(self.root, text="Lista de Pedidos", font=("Arial", 16)).pack(pady=20)

        # Treeview con una nueva columna "Estado"
        tree = ttk.Treeview(self.root, columns=("Pedido", "Cliente", "Fecha Entrega", "Estado"), show="headings")
        tree.heading("Pedido", text="Número Pedido")
        tree.heading("Cliente", text="Cliente")
        tree.heading("Fecha Entrega", text="Fecha Entrega")
        tree.heading("Estado", text="Estado")
        tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Cargar los pedidos desde la base de datos
        pedidos = supabase.table("pedidos").select("*").execute()
        for pedido in pedidos.data:
            # Convertir la fecha al formato dd/mm/aaaa
            fecha_formateada = datetime.strptime(pedido["fecha_entrega"], "%Y-%m-%d").strftime("%d/%m/%Y")
            estado_texto = "Listo" if pedido["estado"] else "Pendiente"
            # Insertar los datos en el Treeview
            tree.insert("", "end", values=(pedido["id"], pedido["cliente"], fecha_formateada, estado_texto))

        def marcar_como_listo():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Selecciona un pedido para marcar como listo")
                return

            pedido_id = tree.item(selected_item, "values")[0]
            # Actualizar el estado en la base de datos
            supabase.table("pedidos").update({"estado": True}).eq("id", pedido_id).execute()

            # Refrescar la lista de pedidos
            self.mostrar_lista_pedidos()

        def abrir_pdf():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "Selecciona un pedido para abrir el PDF")
                return

            pedido_id = tree.item(selected_item, "values")[0]
            pedido = supabase.table("pedidos").select("*").eq("id", pedido_id).execute()
            pdf_url = pedido.data[0]["pdf_url"]

            # Abre la URL en el navegador
            webbrowser.open(pdf_url)

        # Botones para interactuar con los pedidos
        tk.Button(self.root, text="Marcar como Listo", command=marcar_como_listo).pack(pady=10)
        tk.Button(self.root, text="Abrir PDF", command=abrir_pdf).pack(pady=10)
        tk.Button(self.root, text="Volver", command=self.mostrar_menu_principal).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()