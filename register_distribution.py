import os
from tkinter import messagebox

import ngspipeline.cli

tar_path = 'ngstoolkitdist.tar'

if not os.path.exists(tar_path):
    messagebox.showerror('Error',
                         f"File {tar_path} was not found. If you have a tar file please move it to this folder "
                         f"and run the register script again.")
else:
    messagebox.showinfo('Starting...', 'Please click OK to start. This may take a while...')
    try:
        ngspipeline.cli.import_from_tar(tar_path)
        messagebox.showinfo('Finished', 'Registration of WSL distribution finished.')
    except:
        messagebox.showerror("Registration failed",
                             "Error in WSL distribution registration. "
                             "Make sure your WSL installation is version 2 compatible and you have followed the "
                             "installation instructions.")
