import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
import ttkthemes as ttkth
from datetime import datetime
import os
import sys
from functools import cmp_to_key

from database import Database
from ui_components import (
    ModernButton, SearchBox, MemberForm, MemberDetailsView, StatusBar,
    PRIMARY_COLOR, SECONDARY_COLOR, BACKGROUND_COLOR, ACCENT_COLOR, TEXT_COLOR, LIGHT_TEXT_COLOR
)

# Define additional colors for better UI
HEADER_BG = "#2C3E50"  # Dark blue for header
TABLE_HEADER_BG = "#34495E"  # Slightly lighter blue for table headers
TABLE_ROW_EVEN = "#ECF0F1"  # Light gray for even rows
TABLE_ROW_ODD = "#FFFFFF"  # White for odd rows
BUTTON_ADD_BG = "#27AE60"  # Green for add button
BUTTON_REFRESH_BG = "#3498DB"  # Blue for refresh button

class FitGymApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FitGym Membership Manager")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # Initialize database
        self.db = Database()
        
        # Apply theme
        self.style = ttkth.ThemedStyle(self.root)
        self.style.set_theme("arc")
        
        # Configure custom styles
        self._configure_styles()
        
        # Create UI
        self._create_widgets()
        
        # Load initial data
        self._load_members()
    
    def _configure_styles(self):
        """Configure custom ttk styles"""
        # Configure colors
        self.root.configure(background=BACKGROUND_COLOR)
        
        # Configure button styles
        self.style.configure(
            "Modern.TButton",
            background=PRIMARY_COLOR,
            foreground="white",
            padding=5,
            font=("Helvetica", 10, "bold")
        )
        
        # Add button style
        self.style.configure(
            "Add.TButton",
            background=BUTTON_ADD_BG,
            foreground="white",
            padding=5,
            font=("Helvetica", 10, "bold")
        )
        
        # Refresh button style
        self.style.configure(
            "Refresh.TButton",
            background=BUTTON_REFRESH_BG,
            foreground="white",
            padding=5,
            font=("Helvetica", 10, "bold")
        )
        
        # Configure treeview
        self.style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground="black",  # Changed from TEXT_COLOR to black
            rowheight=30,  # Increased row height
            font=("Helvetica", 10)
        )
        self.style.configure(
            "Treeview.Heading",
            background=TABLE_HEADER_BG,
            foreground="white",
            font=("Helvetica", 11, "bold"),
            padding=5
        )
        
        # Configure other widgets
        self.style.configure("TLabel", background=BACKGROUND_COLOR, foreground=TEXT_COLOR)
        self.style.configure("Header.TLabel", background=HEADER_BG, foreground="white", font=("Helvetica", 12))
        self.style.configure("Title.TLabel", background=HEADER_BG, foreground="white", font=("Helvetica", 18, "bold"))
        self.style.configure("TFrame", background=BACKGROUND_COLOR)
        self.style.configure("Header.TFrame", background=HEADER_BG)
        self.style.configure("TNotebook", background=BACKGROUND_COLOR)
        self.style.configure("TNotebook.Tab", background=BACKGROUND_COLOR, padding=[10, 5])
    
    def _create_widgets(self):
        """Create main application widgets"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header frame - limit to 20% of vertical space
        header_frame = ttk.Frame(main_container, style="Header.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10), ipady=10)
        header_frame.pack_propagate(False)  # Don't shrink
        # Set the height to 20% of the window height
        self.root.update()
        header_height = int(self.root.winfo_height() * 0.15)  # 15% of window height
        header_frame.configure(height=header_height)
        
        # Left side of header (logo and title)
        left_header = ttk.Frame(header_frame, style="Header.TFrame")
        left_header.pack(side=tk.LEFT, fill=tk.Y)
        
        # Load and display logo
        try:
            logo_path = "c:/Users/barcl/Documents/fitgym/logo.png"
            self.logo_img = PhotoImage(file=logo_path)
            # Resize to fit header height
            logo_height = header_height - 20  # Padding
            ratio = logo_height / self.logo_img.height()
            new_width = int(self.logo_img.width() * ratio)
            self.logo_img = self.logo_img.subsample(int(self.logo_img.width() / new_width))
            logo_label = ttk.Label(left_header, image=self.logo_img, background=HEADER_BG)
            logo_label.pack(side=tk.LEFT, padx=(20, 10), pady=5)
        except Exception as e:
            print(f"Error loading logo: {e}")
        
        # App title
        title_label = ttk.Label(
            left_header, 
            text="FitGym Membership Manager", 
            style="Title.TLabel"
        )
        title_label.pack(side=tk.LEFT, padx=10)
        
        # Right side of header (search and filter)
        right_header = ttk.Frame(header_frame, style="Header.TFrame")
        right_header.pack(side=tk.RIGHT, fill=tk.Y, padx=20)
        
        # Filter by days left
        filter_frame = ttk.Frame(right_header, style="Header.TFrame")
        filter_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        
        ttk.Label(filter_frame, text="Filter by days left:", style="Header.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        
        self.days_filter_var = tk.StringVar(value="All")
        days_filter = ttk.Combobox(filter_frame, textvariable=self.days_filter_var, 
                                  values=["All", "Expired (0)", "Critical (1-3)", "This Week (1-7)", "This Month (1-30)"], 
                                  width=15, state="readonly")
        days_filter.pack(side=tk.LEFT)
        days_filter.bind("<<ComboboxSelected>>", self._apply_filter)
        
        # Search box
        self.search_box = SearchBox(right_header, command=self._search_members, placeholder="Search by name...")
        self.search_box.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        # Content frame
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview for members
        self._create_treeview(content_frame)
        
        # Button frame
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Add member button - with icon and more visible
        add_button = ModernButton(
            button_frame, 
            text="➕ Add New Member", 
            command=self._show_add_member_form,
            style="Add.TButton"
        )
        add_button.pack(side=tk.LEFT, padx=(0, 5), pady=5)
        
        # Refresh button
        refresh_button = ModernButton(
            button_frame, 
            text="🔄 Refresh", 
            command=self._load_members,
            style="Refresh.TButton"
        )
        refresh_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status bar
        self.status_bar = StatusBar(main_container)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def _create_treeview(self, parent):
        """Create and configure the treeview for displaying members"""
        # Create a frame with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = (
            "id", "name", "phone", "email", "membership_type", 
            "start_date", "end_date", "days_remaining", "status"
        )
        self.tree = ttk.Treeview(
            tree_frame, 
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set
        )
        
        # Configure scrollbar
        scrollbar.config(command=self.tree.yview)
        
        # Define column widths and headings with improved names
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("name", width=150)
        self.tree.column("phone", width=120)
        self.tree.column("email", width=180)
        self.tree.column("membership_type", width=100, anchor=tk.CENTER)
        self.tree.column("start_date", width=100, anchor=tk.CENTER)
        self.tree.column("end_date", width=100, anchor=tk.CENTER)
        self.tree.column("days_remaining", width=100, anchor=tk.CENTER)
        self.tree.column("status", width=80, anchor=tk.CENTER)
        
        self.tree.heading("id", text="Member ID")
        self.tree.heading("name", text="Member Name")
        self.tree.heading("phone", text="Phone Number")
        self.tree.heading("email", text="Email Address")
        self.tree.heading("membership_type", text="Plan")
        self.tree.heading("start_date", text="Start Date")
        self.tree.heading("end_date", text="End Date")
        self.tree.heading("days_remaining", text="Days Left")
        self.tree.heading("status", text="Status")
        
        # Pack the treeview
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event
        self.tree.bind("<Double-1>", self._on_member_double_click)
        
        # Configure row colors for alternating rows
        self.tree.tag_configure("evenrow", background=TABLE_ROW_EVEN)
        self.tree.tag_configure("oddrow", background=TABLE_ROW_ODD)
    
    def _load_members(self):
        """Load all members from database into treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get members from database
        members = self.db.get_all_members()
        
        # Apply days filter if set
        members = self._filter_by_days(members)
        
        # Sort members: first by days_remaining (ascending), then by name
        # Members with 0 days should appear at the bottom
        def compare_members(a, b):
            # Put expired members (0 days) at the bottom
            if a["days_remaining"] == 0 and b["days_remaining"] > 0:
                return 1
            elif a["days_remaining"] > 0 and b["days_remaining"] == 0:
                return -1
            # For non-expired members, sort by days remaining (ascending)
            elif a["days_remaining"] != b["days_remaining"]:
                return a["days_remaining"] - b["days_remaining"]
            # If days remaining are equal, sort by name
            else:
                return -1 if a["name"].lower() < b["name"].lower() else 1
        
        members.sort(key=cmp_to_key(compare_members))
        
        # Insert into treeview with alternating row colors
        for i, member in enumerate(members):
            values = (
                member["id"],
                member["name"],
                member["phone"] or "",
                member["email"] or "",
                member["membership_type"],
                member["start_date"],
                member["end_date"],
                member["days_remaining"],
                member["status"].capitalize()
            )
            
            # Set tag based on days remaining
            if member["days_remaining"] == 0:
                tag = "expired"
            elif member["days_remaining"] == 1:
                tag = "one_day"
            elif member["days_remaining"] == 2:
                tag = "two_days"
            elif member["days_remaining"] == 3:
                tag = "three_days"
            else:
                tag = "evenrow" if i % 2 == 0 else "oddrow"
            
            self.tree.insert("", tk.END, values=values, tags=(tag,))
        
        # Configure row colors with more vibrant colors and black text
        self.tree.tag_configure("expired", background="#FFCCCC", foreground="black")  # Changed text color to black
        self.tree.tag_configure("one_day", background="#FFAA99", foreground="black")  # Changed text color to black
        self.tree.tag_configure("two_days", background="#FFD699", foreground="black")  # Changed text color to black
        self.tree.tag_configure("three_days", background="#FFFFAA", foreground="black")  # Changed text color to black
        
        # Update status
        self.status_bar.set_status(f"Loaded {len(members)} members")
    
    def _filter_by_days(self, members):
        """Filter members by days remaining based on selected filter"""
        filter_value = self.days_filter_var.get()
        
        if filter_value == "All":
            return members
        elif filter_value == "Expired (0)":
            return [m for m in members if m["days_remaining"] == 0]
        elif filter_value == "Critical (1-3)":
            return [m for m in members if 1 <= m["days_remaining"] <= 3]
        elif filter_value == "This Week (1-7)":
            return [m for m in members if 1 <= m["days_remaining"] <= 7]
        elif filter_value == "This Month (1-30)":
            return [m for m in members if 1 <= m["days_remaining"] <= 30]
        else:
            return members
    
    def _apply_filter(self, event=None):
        """Apply the days filter when changed"""
        self._load_members()
    
    def _search_members(self, search_term):
        """Search members by name, phone, or email"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get search results
        members = self.db.search_members(search_term)
        
        # Apply days filter if set
        members = self._filter_by_days(members)
        
        # Sort members: first by days_remaining (ascending), then by name
        # Members with 0 days should appear at the bottom
        def compare_members(a, b):
            # Put expired members (0 days) at the bottom
            if a["days_remaining"] == 0 and b["days_remaining"] > 0:
                return 1
            elif a["days_remaining"] > 0 and b["days_remaining"] == 0:
                return -1
            # For non-expired members, sort by days remaining (ascending)
            elif a["days_remaining"] != b["days_remaining"]:
                return a["days_remaining"] - b["days_remaining"]
            # If days remaining are equal, sort by name
            else:
                return -1 if a["name"].lower() < b["name"].lower() else 1
        
        members.sort(key=cmp_to_key(compare_members))
        
        # Insert into treeview with alternating row colors
        for i, member in enumerate(members):
            values = (
                member["id"],
                member["name"],
                member["phone"] or "",
                member["email"] or "",
                member["membership_type"],
                member["start_date"],
                member["end_date"],
                member["days_remaining"],
                member["status"].capitalize()
            )
            
            # Set tag based on days remaining
            if member["days_remaining"] == 0:
                tag = "expired"
            elif member["days_remaining"] == 1:
                tag = "one_day"
            elif member["days_remaining"] == 2:
                tag = "two_days"
            elif member["days_remaining"] == 3:
                tag = "three_days"
            else:
                tag = "evenrow" if i % 2 == 0 else "oddrow"
            
            self.tree.insert("", tk.END, values=values, tags=(tag,))
        
        # Update status
        self.status_bar.set_status(f"Found {len(members)} matching '{search_term}'")

    def _on_member_double_click(self, event):
        """Handle double-click on a member row"""
        # Get selected item
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get member ID
        item = self.tree.item(selection[0])
        member_id = item["values"][0]
        
        # Get member details
        member = self.db.get_member(member_id)
        if not member:
            messagebox.showerror("Error", "Member not found")
            return
        
        # Show member details dialog
        self._show_member_details(member)
    
    def _show_member_details(self, member):
        """Show dialog with member details"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Member: {member['name']}")
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create details view
        details_view = MemberDetailsView(
            dialog, 
            member, 
            on_edit=self._show_edit_member_form,
            on_delete=self._delete_member
        )
        details_view.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def _show_add_member_form(self):
        """Show dialog for adding a new member"""
        # Get membership types
        membership_types = self.db.get_membership_types()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Member")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create form
        form = MemberForm(dialog, membership_types, on_submit=self._add_member)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def _show_edit_member_form(self, member):
        """Show dialog for editing a member"""
        # Get membership types
        membership_types = self.db.get_membership_types()
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Member: {member['name']}")
        dialog.geometry("400x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Create form
        form = MemberForm(
            dialog, 
            membership_types, 
            on_submit=self._update_member,
            member_data=member,
            allow_edit_all=True  # Allow editing all fields
        )
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def _add_member(self, data):
        """Add a new member to the database"""
        success, result = self.db.add_member(
            data["name"], 
            data["phone"], 
            data["email"], 
            data["membership_type"]
        )
        
        if success:
            messagebox.showinfo("Success", f"Member {data['name']} added successfully")
            self._load_members()
        else:
            messagebox.showerror("Error", f"Failed to add member: {result}")
    
    def _update_member(self, data):
        """Update an existing member"""
        # If start_date and end_date are provided, update them directly
        if "start_date" in data and "end_date" in data:
            success, result = self.db.update_member_dates(
                data["id"],
                data["name"], 
                data["phone"], 
                data["email"], 
                data["membership_type"],
                data["start_date"],
                data["end_date"],
                data["extend_days"]
            )
        else:
            success, result = self.db.update_member(
                data["id"],
                data["name"], 
                data["phone"], 
                data["email"], 
                data["membership_type"],
                data["extend_days"]
            )
        
        if success:
            messagebox.showinfo("Success", f"Member {data['name']} updated successfully")
            self._load_members()
        else:
            messagebox.showerror("Error", f"Failed to update member: {result}")
    
    def _delete_member(self, member_id):
        """Delete a member from the database"""
        success, result = self.db.delete_member(member_id)
        
        if success:
            messagebox.showinfo("Success", result)
            self._load_members()
        else:
            messagebox.showerror("Error", f"Failed to delete member: {result}")

if __name__ == "__main__":
    # Create root window
    root = tk.Tk()
    
    # Check if ttkthemes is installed
    try:
        import ttkthemes
    except ImportError:
        messagebox.showwarning(
            "Missing Dependency", 
            "The ttkthemes package is not installed. The application will use the default theme.\n\n"
            "To install it, run: pip install ttkthemes"
        )
    
    # Create application
    app = FitGymApp(root)
    
    # Start main loop
    root.mainloop()