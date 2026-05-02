import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import os
import requests
from io import BytesIO
from PIL import Image

# Configuración Matrix Rosa
ctk.set_appearance_mode("Dark")

PINK = "#FF1493" # DeepPink
DARK_PINK = "#C71585" # MediumVioletRed
BLACK = "#050505"
FONT_MATRIX = ("Courier New", 14, "bold")
FONT_TITLE = ("Courier New", 24, "bold")

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MATR!X D0WNL0AD3R")
        self.geometry("600x500")
        self.configure(fg_color=BLACK)
        self.download_path = ""
        self.info_video = None

        # Título
        self.title_label = ctk.CTkLabel(self, text="YT DOWNLOADER", font=FONT_TITLE, text_color=PINK)
        self.title_label.pack(pady=(30, 20))

        # URL
        self.url_label = ctk.CTkLabel(self, text="> INGRESA LA URL:", font=FONT_MATRIX, text_color=PINK)
        self.url_label.pack(pady=(10, 0))
        self.url_entry = ctk.CTkEntry(self, placeholder_text="https://...", width=500, font=FONT_MATRIX, 
                                      fg_color="#111", border_color=PINK, text_color=PINK)
        self.url_entry.pack(pady=(5, 15))

        # Formato
        self.format_var = ctk.StringVar(value="MP3 (Audio)")
        self.format_combo = ctk.CTkComboBox(self, values=["MP3 (Audio)", "MP4 (Video)"], variable=self.format_var, 
                                            width=250, font=FONT_MATRIX, dropdown_font=FONT_MATRIX,
                                            fg_color="#111", border_color=PINK, text_color=PINK, button_color=DARK_PINK, button_hover_color=PINK)
        self.format_combo.pack(pady=(0, 15))

        # Carpeta de destino
        self.folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.folder_frame.pack(pady=(0, 20))
        
        self.folder_btn = ctk.CTkButton(self.folder_frame, text="> EXAMINAR DIR", command=self.seleccionar_carpeta, 
                                        width=150, font=FONT_MATRIX, fg_color=DARK_PINK, hover_color=PINK, border_width=1, border_color=PINK)
        self.folder_btn.pack(side="left", padx=10)

        self.folder_label = ctk.CTkLabel(self.folder_frame, text="[NINGÚN DIRECTORIO]", text_color=DARK_PINK, font=FONT_MATRIX)
        self.folder_label.pack(side="left")

        # Botón de Descarga
        self.download_btn = ctk.CTkButton(self, text="[ INICIAR EXTRACCIÓN ]", command=self.buscar_informacion, 
                                          fg_color=BLACK, hover_color="#330033", border_width=2, border_color=PINK,
                                          font=ctk.CTkFont(family="Courier New", size=18, weight="bold"), text_color=PINK)
        self.download_btn.pack(pady=20)

        # Estado
        self.status_label = ctk.CTkLabel(self, text="> ESPERANDO COMANDOS...", text_color=DARK_PINK, font=FONT_MATRIX)
        self.status_label.pack(pady=10)

    def seleccionar_carpeta(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path = folder
            self.folder_label.configure(text=f"[{self.download_path}]", text_color=PINK)

    def buscar_informacion(self):
        url = self.url_entry.get().strip()

        if not url:
            self.mostrar_error("ERROR: URL NO ENCONTRADA")
            return

        if not self.download_path:
            self.mostrar_error("ERROR: DIRECTORIO VACÍO")
            return

        self.download_btn.configure(state="disabled")
        self.status_label.configure(text="> OBTENIENDO DATOS...", text_color=PINK)

        thread = threading.Thread(target=self._hilo_buscar_info, args=(url,))
        thread.start()

    def mostrar_error(self, msg):
        messagebox.showerror("SYSTEM FAILURE", msg)

    def _hilo_buscar_info(self, url):
        try:
            ydl_opts = {'quiet': True, 'noplaylist': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            title = info.get('title', 'Desconocido')
            thumbnail_url = info.get('thumbnail', None)
            
            img = None
            if thumbnail_url:
                try:
                    response = requests.get(thumbnail_url)
                    img = Image.open(BytesIO(response.content))
                except:
                    pass

            self.after(0, self.mostrar_popup_info, title, img, url)
        except Exception as e:
            self.after(0, self.status_label.configure, {"text": "> ERROR DE EXTRACCIÓN", "text_color": "red"})
            self.after(0, self.download_btn.configure, {"state": "normal"})
            self.after(0, self.mostrar_error, f"Fallo al obtener info:\n{str(e)}")

    def mostrar_popup_info(self, title, img, url):
        popup = ctk.CTkToplevel(self)
        popup.title("DATA INTERCEPTADA")
        popup.geometry("400x550")
        popup.configure(fg_color=BLACK)
        popup.attributes("-topmost", True)
        popup.grab_set()
        
        lbl_title = ctk.CTkLabel(popup, text="> OBJETIVO ENCONTRADO:", font=FONT_MATRIX, text_color=PINK)
        lbl_title.pack(pady=(20,10))
        
        lbl_name = ctk.CTkLabel(popup, text=title, font=ctk.CTkFont(family="Courier New", size=16, weight="bold"), text_color="white", wraplength=350)
        lbl_name.pack(pady=(0,20))

        if img:
            # Resize image
            img.thumbnail((300, 300))
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            img_label = ctk.CTkLabel(popup, image=ctk_img, text="")
            img_label.pack(pady=10)
            
        def confirmar():
            popup.destroy()
            self.iniciar_descarga(url)

        def cancelar():
            popup.destroy()
            self.status_label.configure(text="> OPERACIÓN ABORTADA.", text_color=DARK_PINK)
            self.download_btn.configure(state="normal")

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        btn_conf = ctk.CTkButton(btn_frame, text="> PROCEDER", font=FONT_MATRIX, fg_color=DARK_PINK, hover_color=PINK, command=confirmar)
        btn_conf.pack(side="left", padx=10)
        
        btn_canc = ctk.CTkButton(btn_frame, text="> CANCELAR", font=FONT_MATRIX, fg_color=BLACK, border_color=PINK, border_width=1, hover_color="#330033", command=cancelar)
        btn_canc.pack(side="left", padx=10)

    def iniciar_descarga(self, url):
        formato = self.format_var.get()
        self.status_label.configure(text="> DESCARGANDO DATOS... NO DESCONECTAR.", text_color=PINK)
        thread = threading.Thread(target=self._hilo_descargar, args=(url, formato, self.download_path))
        thread.start()

    def _hilo_descargar(self, url, formato, ruta):
        try:
            ydl_opts = {
                'outtmpl': os.path.join(ruta, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True
            }

            if "MP3" in formato:
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                ydl_opts['merge_output_format'] = 'mp4'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.after(0, self.mostrar_popup_terminado)

        except Exception as e:
            msg = f"Error crítico:\n{str(e)}"
            if "ffmpeg" in str(e).lower() or "ffprobe" in str(e).lower():
                msg = "FFmpeg no encontrado. Esquema de audio corrupto."
            
            self.after(0, self.status_label.configure, {"text": "> DESCARGA FALLIDA", "text_color": "red"})
            self.after(0, self.download_btn.configure, {"state": "normal"})
            self.after(0, self.mostrar_error, msg)

    def mostrar_popup_terminado(self):
        self.status_label.configure(text="> SECUENCIA COMPLETADA.", text_color=PINK)
        self.download_btn.configure(state="normal")
        self.url_entry.delete(0, 'end')

        end_popup = ctk.CTkToplevel(self)
        end_popup.title("SYSTEM ALERT")
        end_popup.geometry("800x400")
        end_popup.configure(fg_color=BLACK)
        end_popup.attributes("-topmost", True)
        end_popup.overrideredirect(True) # Sin bordes de ventana, puro estilo peli
        end_popup.grab_set() # Bloquea interacción con la ventana principal
        
        # Borde rosa simulado con un frame
        border_frame = ctk.CTkFrame(end_popup, fg_color=BLACK, border_color=PINK, border_width=5)
        border_frame.pack(fill="both", expand=True)

        lbl = ctk.CTkLabel(border_frame, text="DESCARGA TERMINADA", font=ctk.CTkFont(family="Courier New", size=55, weight="bold"), text_color=PINK)
        lbl.place(relx=0.5, rely=0.4, anchor="center")
        
        # Efecto parpadeo
        self.blink_count = 0
        def blink():
            if not end_popup.winfo_exists():
                return
            current_color = lbl.cget("text_color")
            next_color = BLACK if current_color == PINK else PINK
            lbl.configure(text_color=next_color)
            self.blink_count += 1
            if self.blink_count < 12:
                end_popup.after(400, blink)
            else:
                lbl.configure(text_color=PINK)
                
        blink()

        btn_close = ctk.CTkButton(border_frame, text="> CERRAR CONEXIÓN", font=FONT_MATRIX, fg_color=DARK_PINK, hover_color=PINK, command=end_popup.destroy)
        btn_close.place(relx=0.5, rely=0.75, anchor="center")

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
