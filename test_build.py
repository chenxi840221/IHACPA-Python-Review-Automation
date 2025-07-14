#!/usr/bin/env python3
"""
Test script to verify PyInstaller build works
This is a minimal version to test the build process
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

def main():
    root = tk.Tk()
    root.title("IHACPA Build Test")
    root.geometry("400x300")
    
    label = ttk.Label(root, text="IHACPA Python Package Review Automation", 
                     font=('Arial', 14, 'bold'))
    label.pack(pady=20)
    
    info_text = f"""
Build Test Successful!

Python Version: {sys.version}
Executable: {sys.executable}
Platform: {sys.platform}
Current Dir: {os.getcwd()}

This confirms the PyInstaller build is working.
    """
    
    text_widget = tk.Text(root, height=10, width=50)
    text_widget.pack(padx=20, pady=10)
    text_widget.insert('1.0', info_text)
    text_widget.config(state='disabled')
    
    def show_message():
        messagebox.showinfo("Test", "Build is working correctly!")
    
    button = ttk.Button(root, text="Test Message Box", command=show_message)
    button.pack(pady=10)
    
    ttk.Button(root, text="Exit", command=root.quit).pack()
    
    root.mainloop()

if __name__ == "__main__":
    main()