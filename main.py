import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2
import numpy as np
import csv
import rembg

def cargar_colores_ral(archivo):
    colores = []
    with open(archivo, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 5:
                codigo, nombre, r, g, b = row
                colores.append((codigo.strip(), nombre.strip(), (int(r), int(g), int(b))))
    return colores

def aplicar_color(imagen_base, color_rgb, mascara):
    recoloreada = imagen_base.copy()
    for c in range(3):  # BGR
        recoloreada[:, :, c] = np.where(mascara == 255, color_rgb[2 - c], recoloreada[:, :, c])
    return recoloreada

def cv2_to_pil(cv_img):
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGRA2RGBA)
    return Image.fromarray(cv_img)

class RecoloreadorRALApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Recoloreador RAL")
        self.root.geometry("800x600")
        self.imagen_original = None
        self.mascara = None
        self.colores_ral = cargar_colores_ral("ral_colores.csv")
        self.build_ui()
        self.cargar_imagen()  # 👉 Lanza el selector automáticamente

    def build_ui(self):
        btn_cargar = tk.Button(self.root, text="Cargar imagen", command=self.cargar_imagen)
        btn_cargar.pack(pady=10)

        self.frame_colores = tk.Frame(self.root)
        self.frame_colores.pack(fill="both", expand=True)

        self.checkboxes = []
        for i, (codigo, nombre, _) in enumerate(self.colores_ral):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.frame_colores, text=f"{codigo} - {nombre}", variable=var)
            chk.grid(row=i//3, column=i%3, sticky='w')
            self.checkboxes.append((var, codigo, nombre))

        btn_generar = tk.Button(self.root, text="Generar variaciones", command=self.generar_variaciones)
        btn_generar.pack(pady=10)

        self.canvas = tk.Canvas(self.root, width=300, height=300)
        self.canvas.pack()

    def cargar_imagen(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        with open(path, 'rb') as f:
            contenido = f.read()
            salida = rembg.remove(contenido)
        with open("temp_output.png", 'wb') as f:
            f.write(salida)
        imagen = cv2.imread("temp_output.png", cv2.IMREAD_UNCHANGED)
        self.imagen_original = imagen
        self.generar_mascara()
        self.previsualizar(imagen)

    def generar_mascara(self):
        gris = cv2.cvtColor(self.imagen_original, cv2.COLOR_BGRA2GRAY)
        _, self.mascara = cv2.threshold(gris, 30, 255, cv2.THRESH_BINARY)

    def previsualizar(self, imagen_cv):
        img = cv2_to_pil(imagen_cv)
        img.thumbnail((300, 300))
        imgtk = ImageTk.PhotoImage(img)
        self.canvas.create_image(150, 150, image=imgtk)
        self.canvas.image = imgtk

    def generar_variaciones(self):
        seleccionados = [i for i, (var, _, _) in enumerate(self.checkboxes) if var.get()]
        if not seleccionados:
            messagebox.showwarning("Sin colores", "Selecciona al menos un color RAL.")
            return

        os.makedirs("output", exist_ok=True)

        for idx in seleccionados:
            codigo, nombre, rgb = self.colores_ral[idx]
            recoloreada = aplicar_color(self.imagen_original, rgb, self.mascara)
            nombre_archivo = f"output/producto_{codigo}.png"
            cv2.imwrite(nombre_archivo, recoloreada)

        messagebox.showinfo("Listo", "Imágenes generadas en carpeta 'output/'.")

if __name__ == "__main__":
    root = tk.Tk()
    app = RecoloreadorRALApp(root)
    root.mainloop()

