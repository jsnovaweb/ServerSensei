import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

class ConnectionDialog:
    """
    Dialog for configuring SSH connection to remote servers.
    Supports password and SSH key authentication.
    """
    
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Connection Settings")
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create the dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Server Type:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        self.server_type = tk.StringVar(value='local')
        ttk.Radiobutton(main_frame, text="Local Server", variable=self.server_type, value='local', command=self.toggle_remote_fields).grid(row=0, column=1, sticky='w')
        ttk.Radiobutton(main_frame, text="Remote Server (SSH)", variable=self.server_type, value='remote', command=self.toggle_remote_fields).grid(row=0, column=2, sticky='w')
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)
        
        ttk.Label(main_frame, text="Host:", font=('Arial', 10)).grid(row=2, column=0, sticky='w', pady=5)
        self.host_entry = ttk.Entry(main_frame, width=30)
        self.host_entry.grid(row=2, column=1, columnspan=2, sticky='ew', pady=5)
        
        ttk.Label(main_frame, text="Port:", font=('Arial', 10)).grid(row=3, column=0, sticky='w', pady=5)
        self.port_entry = ttk.Entry(main_frame, width=10)
        self.port_entry.insert(0, "22")
        self.port_entry.grid(row=3, column=1, sticky='w', pady=5)
        
        ttk.Label(main_frame, text="Username:", font=('Arial', 10)).grid(row=4, column=0, sticky='w', pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=4, column=1, columnspan=2, sticky='ew', pady=5)
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, columnspan=3, sticky='ew', pady=10)
        
        ttk.Label(main_frame, text="Authentication Method:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky='w', pady=(0, 5))
        
        self.auth_method = tk.StringVar(value='password')
        ttk.Radiobutton(main_frame, text="Password", variable=self.auth_method, value='password', command=self.toggle_auth_fields).grid(row=7, column=0, sticky='w')
        ttk.Radiobutton(main_frame, text="SSH Key", variable=self.auth_method, value='key', command=self.toggle_auth_fields).grid(row=7, column=1, sticky='w')
        
        self.password_frame = ttk.Frame(main_frame)
        self.password_frame.grid(row=8, column=0, columnspan=3, sticky='ew', pady=5)
        
        ttk.Label(self.password_frame, text="Password:").grid(row=0, column=0, sticky='w', pady=5)
        self.password_entry = ttk.Entry(self.password_frame, width=30, show='*')
        self.password_entry.grid(row=0, column=1, sticky='ew', pady=5)
        
        self.key_frame = ttk.Frame(main_frame)
        
        ttk.Label(self.key_frame, text="SSH Key Source:", font=('Arial', 9)).grid(row=0, column=0, sticky='w', pady=5)
        
        self.key_source = tk.StringVar(value='secret')
        ttk.Radiobutton(self.key_frame, text="From Secret (SSH_PRIVATE_KEY)", variable=self.key_source, value='secret').grid(row=1, column=0, columnspan=2, sticky='w')
        ttk.Radiobutton(self.key_frame, text="From File", variable=self.key_source, value='file').grid(row=2, column=0, sticky='w')
        
        key_file_frame = ttk.Frame(self.key_frame)
        key_file_frame.grid(row=2, column=1, sticky='ew', padx=(5, 0))
        
        self.key_file_entry = ttk.Entry(key_file_frame, width=25)
        self.key_file_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(key_file_frame, text="Browse", command=self.browse_key_file).pack(side='left', padx=(5, 0))
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=9, column=0, columnspan=3, sticky='ew', pady=10)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Connect", command=self.connect).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side='left', padx=5)
        
        self.toggle_remote_fields()
    
    def toggle_remote_fields(self):
        """Enable/disable remote connection fields based on server type"""
        state = 'normal' if self.server_type.get() == 'remote' else 'disabled'
        
        self.host_entry.config(state=state)
        self.port_entry.config(state=state)
        self.username_entry.config(state=state)
        self.password_entry.config(state=state)
        
        if state == 'disabled':
            self.password_frame.grid_remove()
            self.key_frame.grid_remove()
        else:
            self.toggle_auth_fields()
    
    def toggle_auth_fields(self):
        """Toggle between password and SSH key authentication fields"""
        if self.auth_method.get() == 'password':
            self.key_frame.grid_remove()
            self.password_frame.grid(row=8, column=0, columnspan=3, sticky='ew', pady=5)
        else:
            self.password_frame.grid_remove()
            self.key_frame.grid(row=8, column=0, columnspan=3, sticky='ew', pady=5)
    
    def browse_key_file(self):
        """Browse for SSH key file"""
        filename = filedialog.askopenfilename(
            title="Select SSH Private Key",
            filetypes=[("SSH Keys", "id_rsa id_ed25519 *.pem"), ("All Files", "*.*")]
        )
        if filename:
            self.key_file_entry.delete(0, 'end')
            self.key_file_entry.insert(0, filename)
    
    def connect(self):
        """Validate and return connection settings"""
        if self.server_type.get() == 'local':
            self.result = {'type': 'local'}
            self.dialog.destroy()
            return
        
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        username = self.username_entry.get().strip()
        
        if not host or not username:
            messagebox.showerror("Error", "Host and Username are required")
            return
        
        try:
            port = int(port)
        except ValueError:
            messagebox.showerror("Error", "Port must be a number")
            return
        
        self.result = {
            'type': 'remote',
            'host': host,
            'port': port,
            'username': username,
            'auth_method': self.auth_method.get()
        }
        
        if self.auth_method.get() == 'password':
            password = self.password_entry.get()
            if not password:
                messagebox.showerror("Error", "Password is required")
                return
            self.result['password'] = password
        else:
            if self.key_source.get() == 'secret':
                ssh_key = os.getenv('SSH_PRIVATE_KEY')
                if not ssh_key:
                    messagebox.showerror("Error", "SSH_PRIVATE_KEY secret not found. Please set it in Secrets.")
                    return
                self.result['key_data'] = ssh_key
            else:
                key_file = self.key_file_entry.get().strip()
                if not key_file or not os.path.exists(key_file):
                    messagebox.showerror("Error", "Invalid SSH key file")
                    return
                self.result['key_file'] = key_file
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog"""
        self.result = None
        self.dialog.destroy()
