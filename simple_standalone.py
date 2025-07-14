#!/usr/bin/env python3
"""
IHACPA Python Package Review Automation - Simple Standalone Version
This version has minimal dependencies and works with the existing main.py
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import subprocess
import json
from pathlib import Path

class SimpleIHACPAGUI:
    """Simple GUI wrapper for IHACPA automation"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("IHACPA Python Package Review Automation v1.5.0")
        self.root.geometry("800x600")
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.azure_key = tk.StringVar()
        self.azure_endpoint = tk.StringVar(value="https://your-resource-name.openai.azure.com/")
        self.azure_model = tk.StringVar(value="gpt-4")
        self.azure_api_version = tk.StringVar(value="2024-02-01")
        self.is_processing = False
        self.process_queue = queue.Queue()
        self.current_process = None
        
        # Create GUI
        self.create_widgets()
        
        # Load saved settings
        self.load_settings()
        
        # Start queue processor
        self.process_queue_messages()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Title
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = ttk.Label(title_frame, text="IHACPA Python Package Review Automation", 
                               font=('Arial', 16, 'bold'))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="Automated vulnerability scanning for 486 Python packages")
        subtitle_label.pack()
        
        # File Selection Frame
        file_frame = ttk.LabelFrame(self.root, text="File Selection", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Input file
        ttk.Label(file_frame, text="Input Excel File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.input_file, width=60).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_input).grid(row=0, column=2)
        
        # Output file
        ttk.Label(file_frame, text="Output Excel File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_file, width=60).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=1, column=2)
        
        # Azure OpenAI Settings Frame
        azure_frame = ttk.LabelFrame(self.root, text="Azure OpenAI Settings (Optional - for AI Analysis)", padding=10)
        azure_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(azure_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(azure_frame, textvariable=self.azure_key, show="*", width=60).grid(row=0, column=1, padx=5)
        
        ttk.Label(azure_frame, text="Endpoint:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(azure_frame, textvariable=self.azure_endpoint, width=60).grid(row=1, column=1, padx=5)
        
        ttk.Label(azure_frame, text="Model:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(azure_frame, textvariable=self.azure_model, width=60).grid(row=2, column=1, padx=5)
        
        ttk.Label(azure_frame, text="API Version:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(azure_frame, textvariable=self.azure_api_version, width=60).grid(row=3, column=1, padx=5)
        
        # Options Frame
        options_frame = ttk.LabelFrame(self.root, text="Processing Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.format_check_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Run format check and fix", 
                       variable=self.format_check_var).pack(anchor=tk.W)
        
        self.verbose_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Verbose logging", 
                       variable=self.verbose_var).pack(anchor=tk.W)
        
        # Log Frame
        log_frame = ttk.LabelFrame(self.root, text="Processing Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons Frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.process_button = ttk.Button(button_frame, text="Start Processing", 
                                        command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_processing, 
                                     state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
    def browse_input(self):
        """Browse for input Excel file"""
        filename = filedialog.askopenfilename(
            title="Select Input Excel File",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
            # Auto-generate output filename
            if not self.output_file.get():
                base = os.path.splitext(filename)[0]
                self.output_file.set(f"{base}_updated.xlsx")
    
    def browse_output(self):
        """Browse for output Excel file"""
        filename = filedialog.asksaveasfilename(
            title="Select Output Excel File",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
    
    def clear_log(self):
        """Clear the log text"""
        self.log_text.delete(1.0, tk.END)
    
    def log_message(self, message):
        """Add message to log"""
        self.process_queue.put(("log", f"{message}\n"))
    
    def start_processing(self):
        """Start the processing in a separate thread"""
        if not self.input_file.get():
            messagebox.showerror("Error", "Please select an input Excel file")
            return
            
        if not self.output_file.get():
            messagebox.showerror("Error", "Please specify an output Excel file")
            return
        
        if not os.path.exists(self.input_file.get()):
            messagebox.showerror("Error", f"Input file not found: {self.input_file.get()}")
            return
        
        # Check if main.py exists
        main_py_path = os.path.join(os.path.dirname(__file__), 'src', 'main.py')
        if not os.path.exists(main_py_path):
            messagebox.showerror("Error", f"main.py not found at: {main_py_path}")
            return
        
        # Disable controls
        self.is_processing = True
        self.process_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start processing thread
        thread = threading.Thread(target=self.run_automation)
        thread.daemon = True
        thread.start()
    
    def stop_processing(self):
        """Stop the processing"""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.log_message("Process terminated by user")
            except:
                pass
        self.is_processing = False
    
    def run_automation(self):
        """Run the automation using subprocess"""
        try:
            # Set up environment variables
            env = os.environ.copy()
            if self.azure_key.get():
                env['AZURE_OPENAI_KEY'] = self.azure_key.get()
                env['AZURE_OPENAI_ENDPOINT'] = self.azure_endpoint.get()
                env['AZURE_OPENAI_MODEL'] = self.azure_model.get()
                env['AZURE_OPENAI_API_VERSION'] = self.azure_api_version.get()
                self.log_message("Azure OpenAI environment variables set")
            
            # Build command
            cmd = [
                sys.executable, '-m', 'src.main',
                '--input', self.input_file.get(),
                '--output', self.output_file.get()
            ]
            
            if self.format_check_var.get():
                cmd.append('--format-check')
            
            if self.verbose_var.get():
                cmd.append('--verbose')
            
            self.log_message(f"Starting automation with command: {' '.join(cmd)}")
            self.log_message("=" * 60)
            
            # Start process
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                env=env,
                cwd=os.path.dirname(__file__)
            )
            
            # Read output line by line
            while True:
                if not self.is_processing:
                    break
                
                output = self.current_process.stdout.readline()
                if output == '' and self.current_process.poll() is not None:
                    break
                if output:
                    self.log_message(output.strip())
            
            # Get final return code
            return_code = self.current_process.poll()
            
            if return_code == 0:
                self.log_message("=" * 60)
                self.log_message("✅ PROCESSING COMPLETED SUCCESSFULLY!")
                messagebox.showinfo("Success", 
                                  f"Processing completed successfully!\n\n"
                                  f"Output file: {self.output_file.get()}")
            else:
                self.log_message("=" * 60)
                self.log_message(f"❌ Process failed with return code: {return_code}")
                messagebox.showerror("Error", 
                                   f"Processing failed with return code: {return_code}\n"
                                   f"Check the log for details.")
            
        except Exception as e:
            self.log_message(f"❌ Error running automation: {str(e)}")
            messagebox.showerror("Error", f"Failed to start automation:\n{str(e)}")
        
        finally:
            # Re-enable controls
            self.process_queue.put(("complete", None))
    
    def process_queue_messages(self):
        """Process messages from the queue"""
        try:
            while True:
                msg_type, msg_data = self.process_queue.get_nowait()
                
                if msg_type == "log":
                    self.log_text.insert(tk.END, msg_data)
                    self.log_text.see(tk.END)
                    self.root.update_idletasks()  # Update GUI
                elif msg_type == "complete":
                    self.is_processing = False
                    self.process_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.current_process = None
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_queue_messages)
    
    def save_settings(self):
        """Save current settings to file"""
        settings = {
            'azure_endpoint': self.azure_endpoint.get(),
            'azure_model': self.azure_model.get(),
            'azure_api_version': self.azure_api_version.get(),
            'format_check': self.format_check_var.get(),
            'verbose': self.verbose_var.get()
        }
        
        try:
            with open('ihacpa_gui_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            self.log_message("Settings saved to ihacpa_gui_settings.json")
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
        except Exception as e:
            self.log_message(f"Failed to save settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings:\n{e}")
    
    def load_settings(self):
        """Load saved settings from file"""
        try:
            if os.path.exists('ihacpa_gui_settings.json'):
                with open('ihacpa_gui_settings.json', 'r') as f:
                    settings = json.load(f)
                
                self.azure_endpoint.set(settings.get('azure_endpoint', 'https://your-resource-name.openai.azure.com/'))
                self.azure_model.set(settings.get('azure_model', 'gpt-4'))
                self.azure_api_version.set(settings.get('azure_api_version', '2024-02-01'))
                self.format_check_var.set(settings.get('format_check', True))
                self.verbose_var.set(settings.get('verbose', True))
                
                self.log_message("Settings loaded from ihacpa_gui_settings.json")
        except Exception as e:
            self.log_message(f"Could not load settings: {e}")


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set a nice theme if available
    try:
        style = ttk.Style()
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')
    except:
        pass
    
    app = SimpleIHACPAGUI(root)
    
    # Show initial message
    root.after(1000, lambda: app.log_message("IHACPA Python Package Review Automation v1.5.0 Ready"))
    root.after(1100, lambda: app.log_message("Select input Excel file and configure settings to begin"))
    
    root.mainloop()


if __name__ == "__main__":
    main()