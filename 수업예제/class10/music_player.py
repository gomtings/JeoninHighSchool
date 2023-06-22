import pygame
#pip3 install playsound
#pip3 install Pygame
import pygame
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

pygame.init()
pygame.mixer.init()

file_path = filedialog.askopenfilename()

pygame.mixer.music.load(file_path)
pygame.mixer.music.play()
print(file_path)
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)