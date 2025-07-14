#!/usr/bin/env python3
"""
Quick test to verify button layout in GUI
"""

import tkinter as tk
from tkinter import ttk

def test_button():
    print("Test button clicked!")

def main():
    root = tk.Tk()
    root.title("Button Layout Test")
    root.geometry("800x600")
    
    # Test the exact button layout from our app
    button_frame = ttk.LabelFrame(root, text="Actions", padding=15)
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    # Configure grid columns
    button_frame.grid_columnconfigure(0, weight=0)
    button_frame.grid_columnconfigure(1, weight=0)
    button_frame.grid_columnconfigure(2, weight=0)
    button_frame.grid_columnconfigure(3, weight=1)
    button_frame.grid_columnconfigure(4, weight=0)
    
    print("Creating START PROCESSING button...")
    
    # Create buttons using grid layout
    process_button = ttk.Button(button_frame, text="START PROCESSING", 
                               command=test_button)
    process_button.grid(row=0, column=0, padx=5, pady=5, sticky='w')
    
    print(f"Button created: {process_button}")
    print(f"Button text: {process_button.cget('text')}")
    
    stop_button = ttk.Button(button_frame, text="STOP", command=test_button, 
                            state=tk.DISABLED)
    stop_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')
    
    save_button = ttk.Button(button_frame, text="Save Settings", command=test_button)
    save_button.grid(row=0, column=2, padx=5, pady=5, sticky='w')
    
    exit_button = ttk.Button(button_frame, text="Exit", command=root.quit)
    exit_button.grid(row=0, column=4, padx=5, pady=5, sticky='e')
    
    # Add some content above to test layout
    content_frame = ttk.LabelFrame(root, text="Test Content", padding=10)
    content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    ttk.Label(content_frame, text="This is test content to verify button placement").pack(pady=20)
    
    print("GUI created, starting mainloop...")
    root.mainloop()

if __name__ == "__main__":
    main()