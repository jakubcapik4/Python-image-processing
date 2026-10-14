# -*- coding: utf-8 -*-
"""
Created on Fri May 10 11:31:58 2024

@author: Jakub Capík, 3ZIG10
"""
                           # Semestrálna Práca
# =============================================================================
# 1. Úloha: Automatické vyhľadanie súborov v priečinku zvoleného typu
# 3. Úloha: Watermark/Logo/Preview
# 4. Úloha: Vylepšenie obrazu (Bilateral filter)
# 5. Úloha: Vyváženie histogramu
# =============================================================================

import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import cv2
import numpy as np

applied_filter = False
applied_watermark = False
applied_histogram_equalization = False
apply_filter_on_open = False
apply_watermark_on_open = False
apply_histogram_equalization_on_open = False
current_image = None
photo = None  # Globálna premenná pre PhotoImage objekt
label = None  # Globálna premenná pre Label widget
photo_list = []  # Globálny zoznam pre udržiavanie PhotoImage objektov
image_files = []  # Zoznam súborov obrázkov

def load_image(image_path):
    try:
        image = Image.open(image_path)
        return image  # Úspešne načítaný obrázok
    except IOError:
        print("Nepodarilo sa načítať obrázok.")
        return None  # Neúspešné načítanie obrázka

def search_files(directory, extension):
    found_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                found_files.append(os.path.join(root, file))
    return found_files

def browse_directory():
    directory = filedialog.askdirectory()
    entry_directory.delete(0, tk.END)
    entry_directory.insert(0, directory)

def search():
    directory = entry_directory.get()
    extension = entry_extension.get()

    global image_files
    image_files = search_files(directory, extension)

    result_text.delete(0, tk.END)  # Odstrániť obsah pred aktualizáciou výsledkov

    if image_files:
        for file in image_files:
            result_text.insert(tk.END, file + "\n")
    else:
        result_text.insert(tk.END, "Žiadne súbory s daným typom neboli nájdené.")

def open_file():
    selected_index = result_text.curselection()  # Získať index(y) vybraného(y) súboru(y)
    if selected_index:
        selected_file = result_text.get(selected_index[0])  # Získať názov vybraného súboru
        selected_file = selected_file.strip()  # Odstrániť biele znaky na konci reťazca
        show_image(selected_file)
        update_image()  # Aktualizovať zobrazenie obrázka

def apply_filter():
    global current_image, applied_filter
    if current_image:
        enhanced_image = bilateral_filter(current_image)
        current_image = enhanced_image
        applied_filter = True
        update_image()

def add_watermark():
    global current_image, applied_watermark
    if current_image:
        watermarked_image = apply_watermark(current_image)
        current_image = watermarked_image
        applied_watermark = True
        update_image()

def apply_histogram_equalization():
    global current_image, applied_histogram_equalization
    if current_image:
        equalized_image = histogram_equalization(current_image)
        current_image = equalized_image
        applied_histogram_equalization = True
        update_image()

def apply_watermark(image):
    # Pridanie vlastného watermarku
    watermark_text = "Watermark"
    text_font = ImageFont.load_default()
    
    # Zmena veľkosti watermarku
    text_size = 60
    text_font = ImageFont.truetype("arial.ttf", text_size)
    
    text_width, text_height = text_font.getsize(watermark_text) if hasattr(text_font, "getsize") else (100, 100)
    watermark_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(watermark_layer)
    text_draw.text(((image.width - text_width) // 2, (image.height - text_height) // 2), watermark_text, fill=(255, 255, 255, 128), font=text_font)
    
    # Kombinovanie obrázkov
    watermarked_image = Image.alpha_composite(image.convert("RGBA"), watermark_layer)
    
    return watermarked_image

def histogram_equalization(image):
    np_image = np.array(image)
    equalized_channels = []
    for channel in cv2.split(np_image):
        equalized_channel = cv2.equalizeHist(channel)
        equalized_channels.append(equalized_channel)
    equalized_image = cv2.merge(equalized_channels)
    return Image.fromarray(equalized_image)

def update_image():
    global current_image, photo, label
    if current_image and label:  # Kontrola, či label je definovaný
        photo = ImageTk.PhotoImage(current_image)
        label.configure(image=photo)
        label.image = photo

def show_image(image_path):
    global label, current_image, applied_filter, applied_watermark, applied_histogram_equalization, apply_filter_on_open, apply_watermark_on_open, apply_histogram_equalization_on_open
    image = Image.open(image_path)
    original_image = image.copy()  # Kópia pôvodného obrázka bez akýchkoľvek zmien
    image = image.resize((1280, 720))
    current_image = image
    
    if apply_filter_on_open and not applied_filter:
        current_image = bilateral_filter(current_image)
    if apply_watermark_on_open and not applied_watermark:
        current_image = apply_watermark(current_image)
    if apply_histogram_equalization_on_open and not applied_histogram_equalization:
        current_image = histogram_equalization(current_image)

    # Zmenšená verzia obrázka pre zobrazenie ako náhľad
    thumbnail_image = original_image.copy()
    thumbnail_image.thumbnail((200, 200))  # Zmenšenie na veľkosť 200x200
    thumbnail_photo = ImageTk.PhotoImage(thumbnail_image)

    # Vytvorenie alebo aktualizácia okna a zobrazenie obrázkov v novom okne
    if 'label' in globals():
        if not label:
            image_window = tk.Toplevel()
            image_window.title("Obrázok")
            label = tk.Label(image_window)
            label.pack()

            # Zobraziť zmenšenú verziu obrázka
            thumbnail_label = tk.Label(image_window, image=thumbnail_photo)
            thumbnail_label.pack()

        update_image()
    else:
        image_window = tk.Toplevel()
        image_window.title("Obrázok")
        label = tk.Label(image_window)
        label.pack()

        # Zobraziť zmenšenú verziu obrázka
        thumbnail_label = tk.Label(image_window, image=thumbnail_photo)
        thumbnail_label.pack()

def bilateral_filter(image):
    np_image = np.array(image)
    np_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
    filtered_image = cv2.bilateralFilter(np_image, 9, 75, 75)
    filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(filtered_image)

def start_slideshow(image_folder):
    global photo_list  # Globálna premenná pre zoznam PhotoImage objektov
    image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    image_files = [os.path.join(image_folder, f) for f in image_files]
    root = tk.Tk()
    root.title("Slideshow")

    def show_image_slideshow(index):
        image_path = image_files[index]
        image = Image.open(image_path)
        image = image.resize((1280, 720))
        photo = ImageTk.PhotoImage(image)
        label.configure(image=photo)
        label.image = photo
        photo_list.append(photo)  # Pridať PhotoImage objekt do zoznamu
        label.after(3000, lambda: show_image_slideshow((index + 1) % len(image_files)))

    label = tk.Label(root)
    label.pack()
    show_image_slideshow(0)
    root.mainloop()

# Vytvorenie hlavného okna
root = tk.Tk()
root.title("Vyhľadávanie súborov")

# Vytvorenie a umiestnenie widgetov
label_directory = tk.Label(root, text="Priečinok:")
label_directory.grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_directory = tk.Entry(root, width=50)
entry_directory.grid(row=0, column=1, padx=5, pady=5)
button_browse = tk.Button(root, text="Prehľadávať...", command=browse_directory)
button_browse.grid(row=0, column=2, padx=5, pady=5)

label_extension = tk.Label(root, text="Typ súboru:")
label_extension.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_extension = tk.Entry(root, width=50)
entry_extension.grid(row=1, column=1, padx=5, pady=5)

button_search = tk.Button(root, text="Vyhľadať", command=search)
button_search.grid(row=2, column=1, padx=5, pady=5)

result_text = tk.Listbox(root, width=60, height=10)
result_text.grid(row=3, columnspan=3, padx=5, pady=5)

button_open = tk.Button(root, text="Otvoriť obrázok", command=open_file)
button_open.grid(row=4, column=1, padx=5, pady=5)

button_filter = tk.Button(root, text="Aplikovať filter", command=apply_filter)
button_filter.grid(row=5, column=1, padx=5, pady=5)

button_watermark = tk.Button(root, text="Pridať watermark", command=add_watermark)
button_watermark.grid(row=5, column=2, padx=5, pady=5)

button_histogram_equalization = tk.Button(root, text="Vyvážiť histogram", command=apply_histogram_equalization)
button_histogram_equalization.grid(row=6, column=1, padx=5, pady=5)

button_slideshow = tk.Button(root, text="Spustiť Slideshow", command=lambda: start_slideshow("C:/Users/User/Desktop/SEMESTRAL/images"))
button_slideshow.grid(row=6, column=2, padx=5, pady=5)

root.mainloop()

# =============================================================================
# 6. Úloha: Vytvorenie preview videa (Slideshow)
# =============================================================================

import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

image_files = []  # Zoznam súborov obrázkov
slideshow_index = 0  # Index aktuálneho obrázka v slideshow

def search_files(directory, extension):
    found_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                found_files.append(os.path.join(root, file))
    return found_files

def browse_directory():
    directory = filedialog.askdirectory()
    entry_directory.delete(0, tk.END)
    entry_directory.insert(0, directory)

def search():
    directory = entry_directory.get()
    extension = entry_extension.get()

    global image_files
    image_files = search_files(directory, extension)

    result_text.delete(0, tk.END)  # Odstrániť obsah pred aktualizáciou výsledkov

    if image_files:
        for file in image_files:
            result_text.insert(tk.END, file + "\n")
    else:
        result_text.insert(tk.END, "Žiadne súbory s daným typom neboli nájdené.")

def open_file():
    selected_index = result_text.curselection()  # Získať index(y) vybraného(y) súboru(y)
    if selected_index:
        selected_file = result_text.get(selected_index[0])  # Získať názov vybraného súboru
        selected_file = selected_file.strip()  # Odstrániť biele znaky na konci reťazca
        show_image(selected_file)

def next_image():
    global slideshow_index
    if slideshow_index < len(image_files) - 1:
        slideshow_index += 1
    else:
        slideshow_index = 0
    show_image(image_files[slideshow_index])

def show_image(image_path):
    image = Image.open(image_path)
    image = image.resize((1280, 720))
    photo = ImageTk.PhotoImage(image)
    label.configure(image=photo)
    label.image = photo

# Vytvorenie hlavného okna
root = tk.Tk()
root.title("Slideshow")

# Vytvorenie a umiestnenie widgetov
label_directory = tk.Label(root, text="Priečinok:")
label_directory.grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_directory = tk.Entry(root, width=50)
entry_directory.grid(row=0, column=1, padx=5, pady=5)
button_browse = tk.Button(root, text="Prehľadávať...", command=browse_directory)
button_browse.grid(row=0, column=2, padx=5, pady=5)

label_extension = tk.Label(root, text="Typ súboru:")
label_extension.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_extension = tk.Entry(root, width=50)
entry_extension.grid(row=1, column=1, padx=5, pady=5)

button_search = tk.Button(root, text="Vyhľadať", command=search)
button_search.grid(row=2, column=1, padx=5, pady=5)

result_text = tk.Listbox(root, width=60, height=10)
result_text.grid(row=3, columnspan=3, padx=5, pady=5)

button_open = tk.Button(root, text="Otvoriť obrázok", command=open_file)
button_open.grid(row=4, column=1, padx=5, pady=5)

button_next_image = tk.Button(root, text="Ďalší obrázok", command=next_image)
button_next_image.grid(row=5, column=1, padx=5, pady=5)

label = tk.Label(root)
label.grid(row=6, columnspan=3, padx=5, pady=5)

root.mainloop()

# =============================================================================
# 7. Úloha: Galéria náhľadov obrázkov v priečinku (Thumbnails)
# =============================================================================

import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class ImageBrowser:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Browser")
        self.current_image_index = 0
        self.images = []

        self.label_image = tk.Label(self.master)
        self.label_image.grid(row=0, column=0, columnspan=2)

        self.button_prev = tk.Button(self.master, text="Previous", command=self.show_previous_image)
        self.button_prev.grid(row=1, column=0, padx=5, pady=5)

        self.button_next = tk.Button(self.master, text="Next", command=self.show_next_image)
        self.button_next.grid(row=1, column=1, padx=5, pady=5)

        self.button_open = tk.Button(self.master, text="Open Folder", command=self.open_folder)
        self.button_open.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.load_images(folder_path)
            if self.images:
                self.show_image()

    def load_images(self, folder_path):
        self.images.clear()
        for filename in os.listdir(folder_path):
            if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image_path = os.path.join(folder_path, filename)
                image = Image.open(image_path)
                image.thumbnail((200, 200))
                self.images.append((image, image_path))

    def show_image(self):
        image, _ = self.images[self.current_image_index]
        photo = ImageTk.PhotoImage(image)
        self.label_image.configure(image=photo)
        self.label_image.image = photo

    def show_previous_image(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.show_image()

    def show_next_image(self):
        if self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.show_image()

def main():
    root = tk.Tk()
    app = ImageBrowser(root)
    root.mainloop()

if __name__ == "__main__":
    main()
    
# =============================================================================
# 2. Úloha: Zmena rozlíšenia, pozn. (Podľa môjho výberu)
# =============================================================================


import cv2 as cv
 
img = cv.imread("F:/SEMESTRAL/images/1Hellfire Peninsula TRUE.jpg")
cv.imshow("Overwatch", img)
width = img.shape[0]
height = img.shape[1]
img2 = cv.resize(img, (height//4, width//4))
cv.imshow("Iná Veľkosť", img2)
 
cv.waitKey(0)
cv.destroyAllWindows()
