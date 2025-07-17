import tkinter as tk
from tkinter import ttk, messagebox
import ttkthemes as ttkth
from datetime import datetime
import re

# Custom colors
# Update the color scheme with more vibrant colors
PRIMARY_COLOR = "#2980B9"  # Brighter blue
SECONDARY_COLOR = "#16A085"  # Brighter teal
BACKGROUND_COLOR = "#F5F5F5"  # Light Gray
ACCENT_COLOR = "#E74C3C"  # Brighter red
TEXT_COLOR = "#2C3E50"  # Darker blue-gray
LIGHT_TEXT_COLOR = "#7F8C8D"  # Medium Gray

class ModernButton(ttk.Button):
    """Custom styled button"""
    def __init__(self, parent, **kwargs):
        self.style_name = kwargs.pop('style_name', 'Modern.TButton')
        if 'style' not in kwargs:  # Only set style if not already in kwargs
            kwargs['style'] = self.style_name
        ttk.Button.__init__(self, parent, **kwargs)

class SearchBox(ttk.Frame):
    """Custom search box with icon"""
    def __init__(self, parent, command=None, placeholder="Search...", **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        
        self.command = command
        self.placeholder = placeholder
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        
        self.search_entry = ttk.Entry(self, textvariable=self.search_var, width=30, font=("Helvetica", 10))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Set placeholder
        self.search_entry.insert(0, placeholder)
        self.search_entry.bind("<FocusIn>", self._on_entry_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_entry_focus_out)
        self.search_entry.bind("<Return>", self._on_search)
        
        # Search button with better icon
        self.search_button = ModernButton(self, text="🔍", command=self._on_search, width=3)
        self.search_button.pack(side=tk.RIGHT)
    
    def _on_entry_focus_in(self, event):
        if self.search_var.get() == self.placeholder:
            self.search_entry.delete(0, tk.END)
    
    def _on_entry_focus_out(self, event):
        if not self.search_var.get():
            self.search_entry.insert(0, self.placeholder)
    
    def _on_search_change(self, *args):
        # Auto-search as user types (optional)
        pass
    
    def _on_search(self, event=None):
        search_text = self.search_var.get()
        if search_text and search_text != self.placeholder and self.command:
            self.command(search_text)
    
    def get(self):
        text = self.search_var.get()
        return "" if text == self.placeholder else text
    
    def set(self, text):
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, text if text else self.placeholder)

class MemberForm(ttk.Frame):
    """Form for adding/editing members"""
    def __init__(self, parent, membership_types, on_submit, member_data=None, allow_edit_all=False, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        
        self.membership_types = membership_types
        self.on_submit = on_submit
        self.member_data = member_data
        self.is_edit_mode = member_data is not None
        self.allow_edit_all = allow_edit_all
        
        self._create_widgets()
        
        if self.is_edit_mode:
            self._populate_form()
    
    def _create_widgets(self):
        # Title
        title_text = "Edit Member" if self.is_edit_mode else "Add New Member"
        title = ttk.Label(self, text=title_text, font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Name field
        ttk.Label(self, text="Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.name_var, width=30).grid(row=1, column=1, sticky="ew", pady=5)
        
        # Phone field
        ttk.Label(self, text="Phone:").grid(row=2, column=0, sticky="w", pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.phone_var, width=30).grid(row=2, column=1, sticky="ew", pady=5)
        
        # Email field
        ttk.Label(self, text="Email:").grid(row=3, column=0, sticky="w", pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.email_var, width=30).grid(row=3, column=1, sticky="ew", pady=5)
        
        # Membership type field
        ttk.Label(self, text="Membership:").grid(row=4, column=0, sticky="w", pady=5)
        self.membership_var = tk.StringVar()
        membership_options = [t['name'] for t in self.membership_types]
        ttk.Combobox(self, textvariable=self.membership_var, values=membership_options, state="readonly").grid(
            row=4, column=1, sticky="ew", pady=5)
        
        # Start date and end date fields (only for edit mode with allow_edit_all)
        current_row = 5
        if self.is_edit_mode and self.allow_edit_all:
            ttk.Label(self, text="Start Date (YYYY-MM-DD):").grid(row=current_row, column=0, sticky="w", pady=5)
            self.start_date_var = tk.StringVar()
            ttk.Entry(self, textvariable=self.start_date_var, width=30).grid(row=current_row, column=1, sticky="ew", pady=5)
            current_row += 1
            
            ttk.Label(self, text="End Date (YYYY-MM-DD):").grid(row=current_row, column=0, sticky="w", pady=5)
            self.end_date_var = tk.StringVar()
            ttk.Entry(self, textvariable=self.end_date_var, width=30).grid(row=current_row, column=1, sticky="ew", pady=5)
            current_row += 1
        
        # Extension field (only for edit mode)
        if self.is_edit_mode:
            ttk.Label(self, text="Extend by (days):").grid(row=current_row, column=0, sticky="w", pady=5)
            self.extend_var = tk.StringVar(value="0")
            ttk.Entry(self, textvariable=self.extend_var, width=10).grid(row=current_row, column=1, sticky="w", pady=5)
            current_row += 1
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=current_row, column=0, columnspan=2, pady=(20, 0), sticky="e")
        
        ttk.Button(button_frame, text="Cancel", command=self.master.destroy).pack(side=tk.LEFT, padx=5)
        
        submit_text = "Update" if self.is_edit_mode else "Add Member"
        ModernButton(button_frame, text=submit_text, command=self._submit).pack(side=tk.LEFT)
        
        # Configure grid
        self.columnconfigure(1, weight=1)
    
    def _populate_form(self):
        """Fill form with member data in edit mode"""
        if not self.member_data:
            return
        
        self.name_var.set(self.member_data['name'])
        self.phone_var.set(self.member_data['phone'] or "")
        self.email_var.set(self.member_data['email'] or "")
        self.membership_var.set(self.member_data['membership_type'])
        
        # Set start and end dates if allow_edit_all is True
        if self.allow_edit_all:
            self.start_date_var.set(self.member_data['start_date'])
            self.end_date_var.set(self.member_data['end_date'])
    
    def _validate_form(self):
        """Validate form inputs"""
        errors = []
        
        # Name validation
        name = self.name_var.get().strip()
        if not name:
            errors.append("Name is required")
        
        # Email validation (if provided)
        email = self.email_var.get().strip()
        if email and not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            errors.append("Invalid email format")
        
        # Phone validation (basic)
        phone = self.phone_var.get().strip()
        if phone and not re.match(r"^[0-9+\-() ]+$", phone):
            errors.append("Phone number should contain only digits, +, -, (, ) and spaces")
        
        # Membership type validation
        membership_type = self.membership_var.get()
        if not membership_type:
            errors.append("Please select a membership type")
        
        # Date validation (if editing all fields)
        if self.is_edit_mode and self.allow_edit_all:
            # Validate start date format
            start_date = self.start_date_var.get().strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", start_date):
                errors.append("Start date must be in YYYY-MM-DD format")
            
            # Validate end date format
            end_date = self.end_date_var.get().strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", end_date):
                errors.append("End date must be in YYYY-MM-DD format")
            
            # Validate that end date is after start date
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                if end < start:
                    errors.append("End date must be after start date")
            except ValueError:
                # Date format errors already caught above
                pass
        
        # Extension validation (edit mode only)
        if self.is_edit_mode:
            try:
                extend_days = int(self.extend_var.get())
                if extend_days < 0:
                    errors.append("Extension days cannot be negative")
            except ValueError:
                errors.append("Extension days must be a number")
        
        return errors
    
    def _submit(self):
        """Validate and submit form data"""
        errors = self._validate_form()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return
        
        # Prepare data
        data = {
            "name": self.name_var.get().strip(),
            "phone": self.phone_var.get().strip(),
            "email": self.email_var.get().strip(),
            "membership_type": self.membership_var.get()
        }
        
        # Add member ID and extension days for edit mode
        if self.is_edit_mode:
            data["id"] = self.member_data["id"]
            data["extend_days"] = int(self.extend_var.get())
            
            # Add start and end dates if editing all fields
            if self.allow_edit_all:
                data["start_date"] = self.start_date_var.get().strip()
                data["end_date"] = self.end_date_var.get().strip()
        
        # Call submit callback
        self.on_submit(data)
        self.master.destroy()

class MemberDetailsView(ttk.Frame):
    """View for displaying member details"""
    def __init__(self, parent, member_data, on_edit=None, on_delete=None, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        
        self.member_data = member_data
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Title
        title = ttk.Label(self, text="Member Details", font=("Helvetica", 16, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Member info
        ttk.Label(self, text="Name:", font=("Helvetica", 10, "bold")).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(self, text=self.member_data['name']).grid(row=1, column=1, sticky="w", pady=2)
        
        ttk.Label(self, text="Phone:", font=("Helvetica", 10, "bold")).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(self, text=self.member_data['phone'] or "-").grid(row=2, column=1, sticky="w", pady=2)
        
        ttk.Label(self, text="Email:", font=("Helvetica", 10, "bold")).grid(row=3, column=0, sticky="w", pady=2)
        ttk.Label(self, text=self.member_data['email'] or "-").grid(row=3, column=1, sticky="w", pady=2)
        
        ttk.Label(self, text="Membership:", font=("Helvetica", 10, "bold")).grid(row=4, column=0, sticky="w", pady=2)
        ttk.Label(self, text=self.member_data['membership_type']).grid(row=4, column=1, sticky="w", pady=2)
        
        ttk.Label(self, text="Start Date:", font=("Helvetica", 10, "bold")).grid(row=5, column=0, sticky="w", pady=2)
        ttk.Label(self, text=self.member_data['start_date']).grid(row=5, column=1, sticky="w", pady=2)
        
        ttk.Label(self, text="End Date:", font=("Helvetica", 10, "bold")).grid(row=6, column=0, sticky="w", pady=2)
        ttk.Label(self, text=self.member_data['end_date']).grid(row=6, column=1, sticky="w", pady=2)
        
        ttk.Label(self, text="Days Remaining:", font=("Helvetica", 10, "bold")).grid(row=7, column=0, sticky="w", pady=2)
        
        # Style days remaining based on value
        days = self.member_data.get('days_remaining', 0)
        days_label = ttk.Label(self, text=str(days))
        days_label.grid(row=7, column=1, sticky="w", pady=2)
        
        # Color code days remaining
        if days == 0:
            days_label.configure(foreground="#ff5100")  # Red for expired
        elif days == 1:
            days_label.configure(foreground="#ff5100")  # Red for 1 day
        elif days == 2:
            days_label.configure(foreground="#ff8400")  # Orange for 2 days
        elif days == 3:
            days_label.configure(foreground="#f2ff00")  # Yellow for 3 days
        
        ttk.Label(self, text="Status:", font=("Helvetica", 10, "bold")).grid(row=8, column=0, sticky="w", pady=2)
        status_text = self.member_data['status'].capitalize()
        status_label = ttk.Label(self, text=status_text)
        status_label.grid(row=8, column=1, sticky="w", pady=2)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.grid(row=9, column=0, columnspan=2, pady=(20, 0), sticky="e")
        
        ttk.Button(button_frame, text="Close", command=self.master.destroy).pack(side=tk.LEFT, padx=5)
        
        if self.on_edit:
            ModernButton(button_frame, text="Edit", command=self._on_edit).pack(side=tk.LEFT, padx=5)
        
        if self.on_delete:
            delete_btn = ttk.Button(button_frame, text="Delete", command=self._on_delete)
            delete_btn.pack(side=tk.LEFT)
        
        # Configure grid
        self.columnconfigure(1, weight=1)
    
    def _on_edit(self):
        if self.on_edit:
            self.on_edit(self.member_data)
            self.master.destroy()
    
    def _on_delete(self):
        if self.on_delete:
            confirm = messagebox.askyesno(
                "Confirm Deletion", 
                f"Are you sure you want to delete {self.member_data['name']}?"
            )
            if confirm:
                self.on_delete(self.member_data['id'])
                self.master.destroy()

class StatusBar(ttk.Frame):
    """Status bar for displaying information"""
    def __init__(self, parent, **kwargs):
        ttk.Frame.__init__(self, parent, **kwargs)
        
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self, textvariable=self.status_var, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.set_status("Ready")
    
    def set_status(self, text):
        self.status_var.set(text)