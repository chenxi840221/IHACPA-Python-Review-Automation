#!/usr/bin/env python3
"""
IHACPA Python Package Review Automation - Standalone Windows Application
This is a self-contained version with GUI interface for Windows users
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import time
from pathlib import Path
import json

# Add src directory to path for imports
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = os.path.dirname(sys.executable)
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(application_path, 'src'))

# Import our modules
try:
    from src.excel_handler import ExcelHandler
    from src.pypi_client import PyPIClient
    from src.vulnerability_scanner import VulnerabilityScanner, SynchronousVulnerabilityScanner
    from src.config_manager import ConfigManager
except ImportError as e:
    # Fallback for development
    from excel_handler import ExcelHandler
    from pypi_client import PyPIClient
    from vulnerability_scanner import VulnerabilityScanner, SynchronousVulnerabilityScanner
    from config_manager import ConfigManager


class IHACPAAutomationGUI:
    """GUI Application for IHACPA Python Package Review Automation"""
    
    def __init__(self, root):
        self.root = root
        
        # Initialize configuration manager
        self.config = ConfigManager()
        
        # Validate configuration
        validation = self.config.validate_config()
        if validation['errors']:
            messagebox.showerror("Configuration Error", 
                               "Configuration errors found:\n" + "\n".join(validation['errors']))
        
        # Apply configuration to environment
        self.config.apply_to_environment()
        
        # Get GUI configuration
        gui_config = self.config.get_gui_config()
        app_config = self.config.get_nested_value('app', {})
        
        # Set window properties from config
        app_name = app_config.get('name', 'IHACPA Python Package Review Automation')
        app_version = app_config.get('version', '1.5.0')
        self.root.title(f"{app_name} v{app_version}")
        
        window_width = gui_config.get('window_width', 900)
        window_height = gui_config.get('window_height', 800)  # Increased height
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.minsize(800, 600)  # Set minimum size
        
        # Set icon if available
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Variables - initialize from config
        files_config = self.config.get_files_config()
        azure_config = self.config.get_azure_openai_config()
        
        self.input_file = tk.StringVar(value=files_config.get('default_input_path', ''))
        self.output_file = tk.StringVar(value=files_config.get('default_output_path', ''))
        self.azure_key = tk.StringVar(value=azure_config.get('api_key', ''))
        self.azure_endpoint = tk.StringVar(value=azure_config.get('endpoint', 'https://your-resource-name.openai.azure.com/'))
        self.azure_model = tk.StringVar(value=azure_config.get('model', 'gpt-4'))
        self.progress = tk.DoubleVar()
        self.is_processing = False
        self.process_queue = queue.Queue()
        
        # Processing options from config
        processing_config = self.config.get_processing_config()
        self.format_check_var = tk.BooleanVar(value=processing_config.get('format_check', True))
        self.backup_var = tk.BooleanVar(value=files_config.get('create_backup', True))
        
        # Create GUI
        self.create_widgets()
        
        # Load saved settings (if auto-save is enabled)
        if gui_config.get('auto_save_settings', True):
            self.load_settings()
        
        # Start queue processor
        self.process_queue_messages()
        
        # Bind keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Show configuration warnings if any
        if validation['warnings']:
            self.log_message("Configuration warnings:", "WARNING")
            for warning in validation['warnings']:
                self.log_message(f"  - {warning}", "WARNING")
        
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
        ttk.Entry(file_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_input).grid(row=0, column=2)
        
        # Output file
        ttk.Label(file_frame, text="Output Excel File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_file, width=50).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output).grid(row=1, column=2)
        
        # Azure OpenAI Settings Frame
        azure_frame = ttk.LabelFrame(self.root, text="Azure OpenAI Settings (Optional - for AI Analysis)", padding=10)
        azure_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(azure_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(azure_frame, textvariable=self.azure_key, show="*", width=50).grid(row=0, column=1, padx=5)
        
        ttk.Label(azure_frame, text="Endpoint:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(azure_frame, textvariable=self.azure_endpoint, width=50).grid(row=1, column=1, padx=5)
        
        ttk.Label(azure_frame, text="Model:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(azure_frame, textvariable=self.azure_model, width=50).grid(row=2, column=1, padx=5)
        
        # Options Frame
        options_frame = ttk.LabelFrame(self.root, text="Processing Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(options_frame, text="Run format check and fix", 
                       variable=self.format_check_var).pack(anchor=tk.W)
        
        ttk.Checkbutton(options_frame, text="Create backup before processing", 
                       variable=self.backup_var).pack(anchor=tk.W)
        
        # Add configuration button
        ttk.Button(options_frame, text="Edit Configuration", 
                  command=self.edit_configuration).pack(anchor=tk.W, pady=5)
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready to process")
        self.status_label.pack()
        
        # Keyboard shortcuts help
        shortcuts_label = ttk.Label(progress_frame, 
                                   text="Shortcuts: F5/Ctrl+R=Start, Esc=Stop, Ctrl+O=Open File, Ctrl+S=Save Settings",
                                   font=('Arial', 8), foreground='gray')
        shortcuts_label.pack(pady=(5, 0))
        
        # Buttons Frame - place before log frame to ensure visibility
        button_frame = ttk.LabelFrame(self.root, text="Actions", padding=15)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Configure grid columns
        button_frame.grid_columnconfigure(0, weight=0)
        button_frame.grid_columnconfigure(1, weight=0)
        button_frame.grid_columnconfigure(2, weight=0)
        button_frame.grid_columnconfigure(3, weight=1)
        button_frame.grid_columnconfigure(4, weight=0)
        
        # Create buttons using grid layout
        self.process_button = ttk.Button(button_frame, text="START PROCESSING", 
                                        command=self.start_processing)
        self.process_button.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.stop_button = ttk.Button(button_frame, text="STOP", command=self.stop_processing, 
                                     state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        save_button = ttk.Button(button_frame, text="Save Settings", command=self.save_settings)
        save_button.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        exit_button = ttk.Button(button_frame, text="Exit", command=self.root.quit)
        exit_button.grid(row=0, column=4, padx=5, pady=5, sticky='e')
        
        # Log Frame
        log_frame = ttk.LabelFrame(self.root, text="Processing Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for the application"""
        # F5 or Ctrl+R to start processing
        self.root.bind('<F5>', lambda e: self.start_processing())
        self.root.bind('<Control-r>', lambda e: self.start_processing())
        
        # Escape to stop processing
        self.root.bind('<Escape>', lambda e: self.stop_processing())
        
        # Ctrl+S to save settings
        self.root.bind('<Control-s>', lambda e: self.save_settings())
        
        # Ctrl+O to browse input file
        self.root.bind('<Control-o>', lambda e: self.browse_input())
        
        # Ctrl+Q to quit
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        
        # Focus on root window to ensure shortcuts work
        self.root.focus_set()
        
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
    
    def log_message(self, message, level="INFO"):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        self.process_queue.put(("log", f"[{timestamp}] {level}: {message}\n"))
    
    def update_progress(self, current, total, message=""):
        """Update progress bar"""
        if total > 0:
            progress = (current / total) * 100
            self.process_queue.put(("progress", progress))
            self.process_queue.put(("status", message))
    
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
        
        # Disable controls
        self.is_processing = True
        self.process_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start processing thread
        thread = threading.Thread(target=self.process_packages)
        thread.daemon = True
        thread.start()
    
    def stop_processing(self):
        """Stop the processing"""
        self.is_processing = False
        self.log_message("Stopping processing...", "WARNING")
    
    def process_packages(self):
        """Main processing function - runs in separate thread"""
        try:
            self.log_message("Starting IHACPA Python Package Review Automation v1.5.0")
            self.log_message(f"Input file: {self.input_file.get()}")
            self.log_message(f"Output file: {self.output_file.get()}")
            
            # Set up environment for AI if configured
            azure_config = self.config.get_azure_openai_config()
            if self.azure_key.get():
                os.environ['AZURE_OPENAI_KEY'] = self.azure_key.get()
                os.environ['AZURE_OPENAI_ENDPOINT'] = self.azure_endpoint.get()
                os.environ['AZURE_OPENAI_MODEL'] = self.azure_model.get()
                os.environ['AZURE_OPENAI_API_VERSION'] = azure_config.get('api_version', '2024-02-01')
                self.log_message("Azure OpenAI configured for AI analysis")
            else:
                self.log_message("No Azure OpenAI key provided - AI analysis disabled", "WARNING")
            
            # Copy input to output
            import shutil
            shutil.copy2(self.input_file.get(), self.output_file.get())
            self.log_message(f"Created working copy: {self.output_file.get()}")
            
            # Load Excel file
            self.log_message("Loading Excel file...")
            handler = ExcelHandler(self.output_file.get())
            
            if not handler.load_workbook():
                raise Exception("Failed to load Excel file")
            
            # Get all packages
            packages = handler.get_all_packages()
            total_packages = len(packages)
            self.log_message(f"Found {total_packages} packages to process")
            
            # Initialize clients
            self.log_message("Initializing PyPI client...")
            pypi_client = PyPIClient()
            
            self.log_message("Initializing vulnerability scanner...")
            
            # Use faster timeout and disable AI if no API key
            use_ai = bool(self.azure_key.get())
            timeout = 15 if not use_ai else 30  # Faster without AI
            
            vuln_scanner = SynchronousVulnerabilityScanner(
                timeout=timeout,
                max_retries=2,  # Fewer retries for faster processing
                openai_api_key=self.azure_key.get() if self.azure_key.get() else None,
                azure_endpoint=self.azure_endpoint.get() if self.azure_endpoint.get() else None,
                azure_model=self.azure_model.get() if self.azure_model.get() else None
            )
            
            if use_ai:
                self.log_message("AI analysis enabled with Azure OpenAI")
            else:
                self.log_message("Running in fast mode without AI analysis")
            
            # Process packages
            processed = 0
            updated = 0
            failed = 0
            
            for package in packages:
                if not self.is_processing:
                    self.log_message("Processing stopped by user", "WARNING")
                    break
                
                package_name = package.get('package_name', '')
                current_version = package.get('current_version', '')
                row_number = package.get('row_number', 0)
                
                self.update_progress(processed + 1, total_packages, 
                                   f"Processing {package_name} ({processed + 1}/{total_packages})")
                
                try:
                    # Check if package needs update
                    needs_update = False
                    automated_fields = ['latest_version', 'latest_release_date', 'github_url',
                                      'nist_nvd_result', 'mitre_cve_result', 'recommendation']
                    
                    for field in automated_fields:
                        if not package.get(field):
                            needs_update = True
                            break
                    
                    if not needs_update:
                        self.log_message(f"Skipping {package_name} - already complete")
                        processed += 1
                        continue
                    
                    self.log_message(f"Processing {package_name} v{current_version}")
                    
                    # Get PyPI info
                    pypi_info = pypi_client.get_package_info(package_name)
                    if pypi_info and pypi_info != "Not Available":
                        updates = {}
                        
                        # Only add non-None values to avoid Excel issues
                        if pypi_info.get('latest_version'):
                            updates['latest_version'] = pypi_info.get('latest_version')
                        if pypi_info.get('package_url'):
                            updates['pypi_latest_link'] = pypi_info.get('package_url')
                        if pypi_info.get('latest_release_date'):
                            updates['latest_release_date'] = pypi_info.get('latest_release_date')
                        if pypi_info.get('requires_python'):
                            updates['requires'] = pypi_info.get('requires_python')
                        if pypi_info.get('development_status'):
                            updates['development_status'] = pypi_info.get('development_status')
                        if pypi_info.get('github_url'):
                            updates['github_url'] = pypi_info.get('github_url')
                        
                        # Also get date published for current version
                        if current_version:
                            date_published = pypi_client.get_version_publication_date(package_name, str(current_version))
                            if date_published:
                                updates['date_published'] = date_published
                    else:
                        updates = {'latest_version': 'Not Available'}
                    
                    # Scan vulnerabilities
                    self.log_message(f"  Scanning vulnerabilities for {package_name}...")
                    try:
                        vuln_results = vuln_scanner.scan_package(
                            package_name, 
                            github_url=updates.get('github_url'),
                            current_version=str(current_version) if current_version else None
                        )
                        self.log_message(f"  Vulnerability scan completed for {package_name}")
                    except Exception as scan_error:
                        self.log_message(f"  ✗ Vulnerability scan failed for {package_name}: {str(scan_error)}", "ERROR")
                        # Continue with limited data instead of failing completely
                        vuln_results = {'scan_results': {}}
                    
                    # Process vulnerability results
                    scan_results = vuln_results.get('scan_results', {})
                    
                    # GitHub Advisory
                    if 'github_advisory' in scan_results:
                        result = scan_results['github_advisory']
                        if result.get('search_url'):
                            updates['github_advisory_url'] = result.get('search_url', '')
                        if result.get('summary'):
                            updates['github_advisory_result'] = result.get('summary', '')
                    
                    # NIST NVD
                    if 'nist_nvd' in scan_results:
                        result = scan_results['nist_nvd']
                        if result.get('search_url'):
                            updates['nist_nvd_url'] = result.get('search_url', '')
                        if result.get('summary'):
                            updates['nist_nvd_result'] = result.get('summary', '')
                    
                    # MITRE CVE
                    if 'mitre_cve' in scan_results:
                        result = scan_results['mitre_cve']
                        if result.get('search_url'):
                            updates['mitre_cve_url'] = result.get('search_url', '')
                        if result.get('summary'):
                            updates['mitre_cve_result'] = result.get('summary', '')
                    
                    # SNYK
                    if 'snyk' in scan_results:
                        result = scan_results['snyk']
                        if result.get('search_url'):
                            updates['snyk_url'] = result.get('search_url', '')
                        if result.get('summary'):
                            updates['snyk_result'] = result.get('summary', '')
                    
                    # Exploit DB
                    if 'exploit_db' in scan_results:
                        result = scan_results['exploit_db']
                        if result.get('search_url'):
                            updates['exploit_db_url'] = result.get('search_url', '')
                        if result.get('summary'):
                            updates['exploit_db_result'] = result.get('summary', '')
                    
                    # Generate recommendation
                    latest_version = updates.get('latest_version', '')
                    if latest_version and latest_version != 'Not Available':
                        recommendation = vuln_scanner.scanner.generate_recommendations(
                            package_name, 
                            str(current_version) if current_version else '',
                            latest_version,
                            vuln_results
                        )
                        updates['recommendation'] = recommendation
                    else:
                        updates['recommendation'] = 'Unable to determine - manual review required'
                    
                    # Update Excel
                    try:
                        if handler.update_package_data(row_number, updates):
                            updated += 1
                            self.log_message(f"  ✓ Updated {package_name} successfully")
                        else:
                            failed += 1
                            # Try to get more details about the failure
                            error_msg = getattr(handler, 'last_update_error', 'Unknown error')
                            self.log_message(f"  ✗ Failed to update {package_name}: {error_msg}", "ERROR")
                    except Exception as update_error:
                        failed += 1
                        self.log_message(f"  ✗ Exception updating {package_name}: {str(update_error)}", "ERROR")
                    
                except Exception as e:
                    failed += 1
                    self.log_message(f"  ✗ Error processing {package_name}: {str(e)}", "ERROR")
                
                processed += 1
            
            # Run format check if enabled
            if self.format_check_var.get() and self.is_processing:
                self.log_message("Running format check and fix...")
                format_results = handler.check_and_fix_formatting(dry_run=False)
                if 'fixes_applied' in format_results:
                    self.log_message(f"Fixed {format_results['fixes_applied']} formatting issues")
            
            # Save workbook
            if self.is_processing:
                self.log_message("Saving Excel file...")
                if handler.save_workbook(backup=self.backup_var.get()):
                    self.log_message("✓ Excel file saved successfully")
                else:
                    self.log_message("✗ Failed to save Excel file", "ERROR")
            
            # Close resources
            handler.close()
            vuln_scanner.close()
            
            # Final summary
            self.log_message("=" * 50)
            self.log_message(f"Processing complete!")
            self.log_message(f"Total packages: {total_packages}")
            self.log_message(f"Processed: {processed}")
            self.log_message(f"Updated: {updated}")
            self.log_message(f"Failed: {failed}")
            self.log_message(f"Success rate: {((processed-failed)/processed*100):.1f}%")
            
            if self.is_processing:
                messagebox.showinfo("Complete", 
                                  f"Processing complete!\n\n"
                                  f"Packages processed: {processed}\n"
                                  f"Packages updated: {updated}\n"
                                  f"Failed: {failed}")
            
        except Exception as e:
            self.log_message(f"Fatal error: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Processing failed:\n{str(e)}")
        
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
                elif msg_type == "progress":
                    self.progress.set(msg_data)
                elif msg_type == "status":
                    self.status_label.config(text=msg_data)
                elif msg_type == "complete":
                    self.is_processing = False
                    self.process_button.config(state=tk.NORMAL)
                    self.stop_button.config(state=tk.DISABLED)
                    self.progress.set(100)
                    self.status_label.config(text="Processing complete")
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_queue_messages)
    
    def edit_configuration(self):
        """Open configuration editor window"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Configuration Editor")
        config_window.geometry("600x500")
        config_window.transient(self.root)
        config_window.grab_set()
        
        # Configuration text area
        text_frame = ttk.Frame(config_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(text_frame, text="Configuration File (config.yaml)", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        config_text = scrolledtext.ScrolledText(text_frame, height=20, wrap=tk.WORD, 
                                               font=('Consolas', 9))
        config_text.pack(fill=tk.BOTH, expand=True)
        
        # Load current configuration
        try:
            if os.path.exists(self.config.config_file):
                with open(self.config.config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
            else:
                # Show default configuration
                import yaml
                config_content = yaml.dump(self.config.get_default_config(), 
                                         default_flow_style=False, indent=2)
            
            config_text.insert('1.0', config_content)
        except Exception as e:
            config_text.insert('1.0', f"Error loading configuration: {e}")
        
        # Buttons frame
        button_frame = ttk.Frame(config_window)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def save_config():
            try:
                content = config_text.get('1.0', tk.END).strip()
                
                # Validate YAML
                import yaml
                yaml.safe_load(content)
                
                # Save to file
                with open(self.config.config_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Reload configuration
                self.config.load_config()
                self.config.apply_to_environment()
                
                messagebox.showinfo("Success", "Configuration saved and reloaded successfully!")
                config_window.destroy()
                
                # Update GUI with new values
                self.update_from_config()
                
            except yaml.YAMLError as e:
                messagebox.showerror("YAML Error", f"Invalid YAML syntax:\n{e}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration:\n{e}")
        
        def reset_config():
            if messagebox.askyesno("Reset Configuration", 
                                 "Reset to default configuration? This will lose all custom settings."):
                import yaml
                default_config = self.config.get_default_config()
                config_content = yaml.dump(default_config, default_flow_style=False, indent=2)
                config_text.delete('1.0', tk.END)
                config_text.insert('1.0', config_content)
        
        ttk.Button(button_frame, text="Save", command=save_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Default", command=reset_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=config_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def update_from_config(self):
        """Update GUI values from current configuration"""
        azure_config = self.config.get_azure_openai_config()
        files_config = self.config.get_files_config()
        processing_config = self.config.get_processing_config()
        
        # Only update if current values are empty/default
        if not self.azure_key.get() and azure_config.get('api_key'):
            self.azure_key.set(azure_config['api_key'])
        
        if self.azure_endpoint.get() == 'https://your-resource-name.openai.azure.com/':
            self.azure_endpoint.set(azure_config.get('endpoint', 'https://your-resource-name.openai.azure.com/'))
        
        if self.azure_model.get() == 'gpt-4':
            self.azure_model.set(azure_config.get('model', 'gpt-4'))
        
        if not self.input_file.get() and files_config.get('default_input_path'):
            self.input_file.set(files_config['default_input_path'])
        
        if not self.output_file.get() and files_config.get('default_output_path'):
            self.output_file.set(files_config['default_output_path'])
        
        # Update checkboxes
        self.format_check_var.set(processing_config.get('format_check', True))
        self.backup_var.set(files_config.get('create_backup', True))
        
        self.log_message("Configuration updated from config file")
    
    def save_settings(self):
        """Save current settings to file"""
        settings = {
            'azure_endpoint': self.azure_endpoint.get(),
            'azure_model': self.azure_model.get(),
            'format_check': self.format_check_var.get(),
            'backup': self.backup_var.get()
        }
        
        try:
            with open('ihacpa_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            self.log_message("Settings saved successfully")
        except Exception as e:
            self.log_message(f"Failed to save settings: {e}", "ERROR")
    
    def load_settings(self):
        """Load saved settings from file"""
        try:
            if os.path.exists('ihacpa_settings.json'):
                with open('ihacpa_settings.json', 'r') as f:
                    settings = json.load(f)
                
                self.azure_endpoint.set(settings.get('azure_endpoint', 'https://your-resource-name.openai.azure.com/'))
                self.azure_model.set(settings.get('azure_model', 'gpt-4'))
                self.format_check_var.set(settings.get('format_check', True))
                self.backup_var.set(settings.get('backup', True))
                
                self.log_message("Settings loaded from file")
        except Exception as e:
            self.log_message(f"Could not load settings: {e}", "WARNING")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = IHACPAAutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()