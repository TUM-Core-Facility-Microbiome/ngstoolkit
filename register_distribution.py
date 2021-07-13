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
    ngspipeline.cli.import_from_tar(tar_path)
    messagebox.showinfo('Finished', 'Registration of WSL distribution finished.')
