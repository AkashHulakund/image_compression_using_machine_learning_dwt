import tkinter as tk
from tkinter import filedialog
import numpy as np
import pywt
from PIL import Image,ImageTk
import os

class ImageCompressionUI:
    def __init__(self, master):
        self.master = master
        master.title("Image Compression with DWT")

        self.image_path = ""
        self.original_image = None
        self.compressed_image = None

        # Create widgets
        self.choose_image_button = tk.Button(master, text="Choose Image",command=self.choose_image, height=4, width=30)
        self.save_button = tk.Button(master, text="Compress and save Image", command=self.save_image,height=2, width=20)
        self.original_image_label = tk.Label(master)
        self.compressed_image_label = tk.Label(master)
        self.original_size_label = tk.Label(master, text="Original Image Size: ")
        self.compressed_size_label = tk.Label(master, text="Compressed Image Size: ")
        self.quality_scale = tk.Scale(master, from_=0, to=100, orient=tk.HORIZONTAL, label="Quality")
        self.quality_scale.set(50)  # default quality value
        self.quality_scale.pack(side=tk.TOP, padx=10, pady=10)
        

        # Add widgets to layout
        self.choose_image_button.pack(side=tk.TOP)
        self.original_image_label.pack(side=tk.LEFT ,padx=10, pady=10)
        self.compressed_image_label.pack(side=tk.RIGHT, padx=10, pady=10)
        self.save_button.pack(side=tk.TOP)
        self.original_size_label.pack(side=tk.LEFT, padx=10, pady=10)
        self.compressed_size_label.pack(side=tk.RIGHT, padx=10, pady=10)

    def choose_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.bmp")])
        self.show_image()

    def show_image(self):
        if self.image_path:
            image = Image.open(self.image_path)
            self.original_image = np.array(image)
            self.compressed_image = self.original_image.copy()
            self.display_image(image, self.original_image_label)
            size_kb = os.path.getsize(self.image_path) / 1024
            if size_kb >= 1024:
                size_kb = size_kb / 1024
                size_unit = "MB"
            else:
                size_unit = "KB"
            self.original_size_label.config(text=f"Compressed Image Size: {size_kb:.2f} {size_unit}")
            

    def display_image(self, image, label):
        image.thumbnail((400, 350))
        photo_image = ImageTk.PhotoImage(image)
        label.config(image=photo_image)
        label.image = photo_image

    def compress_image(self):
        if self.original_image is not None:
        # Split color channels
          if len(self.original_image.shape) == 3:
            r = self.original_image[:, :, 0]
            g = self.original_image[:, :, 1]
            b = self.original_image[:, :, 2]
        else:
            r = g = b = self.original_image
        # Apply DWT to each channel
        r_coeffs = pywt.dwt2(r, 'haar')
        r_cA, (r_cH, r_cV, r_cD) = r_coeffs
        g_coeffs = pywt.dwt2(g, 'haar')
        g_cA, (g_cH, g_cV, g_cD) = g_coeffs
        b_coeffs = pywt.dwt2(b, 'haar')
        b_cA, (b_cH, b_cV, b_cD) = b_coeffs
        # Compress each channel
        r_threshold = (self.quality_scale.get() / 100) * np.max(np.abs(r_cD))
        r_cD_thresholded = pywt.threshold(r_cD, r_threshold, 'soft')
        g_threshold = (self.quality_scale.get() / 100) * np.max(np.abs(g_cD))
        g_cD_thresholded = pywt.threshold(g_cD, g_threshold, 'soft')
        b_threshold = (self.quality_scale.get() / 100) * np.max(np.abs(b_cD))
        b_cD_thresholded = pywt.threshold(b_cD, b_threshold, 'soft')
        # Reconstruct each channel
        r_coeffs_thresholded = (r_cA, (r_cH, r_cV, r_cD_thresholded))
        g_coeffs_thresholded = (g_cA, (g_cH, g_cV, g_cD_thresholded))
        b_coeffs_thresholded = (b_cA, (b_cH, b_cV, b_cD_thresholded))
        compressed_r = pywt.idwt2(r_coeffs_thresholded, 'haar')
        compressed_g = pywt.idwt2(g_coeffs_thresholded, 'haar')
        compressed_b = pywt.idwt2(b_coeffs_thresholded, 'haar')
        # Merge channels
        compressed_image = np.zeros_like(self.original_image)
        compressed_image[:, :, 0] = compressed_r
        compressed_image[:, :, 1] = compressed_g
        compressed_image[:, :, 2] = compressed_b

        # Save compressed image
        self.compressed_image = compressed_image



        
    def save_image(self):
        if self.compressed_image is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg")
            if save_path:
                compressed_image_pil = Image.fromarray(np.uint8(self.compressed_image))
                compressed_image_pil.save(save_path)
                compressed_image_size = os.path.getsize(save_path) / 1024
                if compressed_image_size >= 1024:
                    compressed_image_size = compressed_image_size / 1024
                    size_unit = "MB"
                else:
                    size_unit = "KB"
                self.compressed_size_label.config(text=f"Compressed Image Size: {compressed_image_size:.2f} {size_unit}")
                self.display_image(compressed_image_pil, self.compressed_image_label)



    

root = tk.Tk()
app = ImageCompressionUI(root)
root.mainloop()
