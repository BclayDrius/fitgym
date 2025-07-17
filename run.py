import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ["ttkthemes"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(packages):
    """Install missing dependencies"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    """Main entry point"""
    # Check dependencies
    missing_packages = check_dependencies()
    
    if missing_packages:
        # Create a simple GUI for installing dependencies
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        message = (
            f"The following required packages are missing:\n\n"
            f"{', '.join(missing_packages)}\n\n"
            f"Would you like to install them now?"
        )
        
        install = messagebox.askyesno("Missing Dependencies", message)
        
        if install:
            success = install_dependencies(missing_packages)
            if not success:
                messagebox.showerror(
                    "Installation Failed",
                    "Failed to install dependencies. Please install them manually:\n\n"
                    f"pip install {' '.join(missing_packages)}"
                )
                return
        else:
            messagebox.showwarning(
                "Dependencies Required",
                "The application may not work correctly without the required dependencies."
            )
    
    # Run the main application
    try:
        from main import FitGymApp
        root = tk.Tk()
        app = FitGymApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()