#!/usr/bin/env python3
import datetime
from time import sleep
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Type

from . import __version__
from linAtWin import Driver, WSLDriver
from .pipeline_subprogramms import *

version = __version__


class SkipSubframe(Exception):
    pass


class DenyNextSubframe(Exception):
    pass


class Root:
    def __init__(self, master, driver: Driver):
        self.driver: Driver = driver
        self.values = {}

        self.subframes: List[Type[Subframe]] = [StartScreen, ChoosePipeline, ChoosePipelineReferenceFasta,
                                                ChooseMode, ChooseReadType, ChooseDemultiplexing, ChooseIndexing,
                                                Preprocessing, FolderSelection, MapfileSelection, IMNGSAdvancedOptions,
                                                ProgOptions, Run]
        self.at = -1
        self.app = None

        self.master = master

        self.navigation = tk.Frame(self.master)
        self.btn_back = tk.Button(self.navigation, text='<< Start over', width=25, command=self.start_over)
        self.btn_back.pack(side=tk.LEFT)
        self.btn_next = tk.Button(self.navigation, text='Next >', width=25, command=self.next)
        self.btn_next.pack(side=tk.RIGHT)

        self.frame = tk.Frame(self.master)
        self.next()

        self.navigation.pack(side=tk.BOTTOM)

    def start_over(self):
        self.change_view(0, skip_on_next=True)

    def next(self):
        self.change_view(self.at + 1)

    def change_view(self, subframe_id, skip_on_next=False):
        if self.app is not None:
            if not skip_on_next:
                try:
                    logging.debug(f"calling on_next on {self.app.__class__.__name__!r}")
                    self.app.on_next()
                except DenyNextSubframe:
                    logging.debug(f"got deny next subframe")
                    return
            else:
                logging.debug(f"not calling on_next on {self.app.__class__.__name__!r}")
            self.app.pack_forget()
        self.at = subframe_id
        try:
            self.app = self.subframes[self.at](self, self.frame)
            logging.debug(f'showing frame {self.at}. {self.app.__class__.__name__!r}')
        except SkipSubframe:
            logging.debug(f'skipping frame {self.at}. {self.subframes[self.at].__name__!r}')
            self.change_view(self.at + 1, skip_on_next=True)
            return

        self.update_navigation()

    def update_navigation(self):
        if self.at == 0:
            self.btn_back['state'] = 'disabled'
        else:
            self.btn_back['state'] = 'normal'

        # self.btn_next['text'] = f'({self.at + 1}/{len(self.subframes)}) Next >'
        self.btn_next['text'] = f'Next >'
        if self.at >= len(self.subframes) - 1:
            self.btn_next['state'] = 'disabled'
        else:
            self.btn_next['state'] = 'normal'
        logging.debug(f"updated navigation for self.at={self.at}. "
                      f"self.btn_back['state']={self.btn_back['state']!r}. "
                      f"self.btn_next['state']={self.btn_next['state']!r}")

    def quit(self):
        try:
            logging.debug(f"Destroyed {self.__class__.__name__!r} window.")
        finally:
            self.master.destroy()


class Subframe:
    def __init__(self, master: Root, frame):
        self.master = master
        self.frame = frame

    def pack_forget(self):
        logging.debug(f'Called pack_forget on {self.__class__.__name__!r}')
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.frame.pack_forget()

    def on_next(self):
        pass


class StartScreen(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)
        self.hello_world = tk.Label(self.frame, text='Welcome to NGSToolkit.')
        self.hello_world.pack()
        self.whatsonnext = tk.Label(self.frame, text='Pressing next will run some startup checks.')
        self.whatsonnext.pack()
        self.frame.pack()

    def on_next(self):
        try:
            logging.info('Perform driver self checks')
            self.master.driver.self_check()
        except linAtWin.driver.DriverException:
            logging.error('Driver Error. WSL not prepared properly.')
            messagebox.showerror("Faulty WSL environment",
                                 "Please follow the installation instructions and check if the WSL2 distribution is "
                                 "installed properly.")
            raise

        logging.info('Check wsl distro version')
        logging.info(f'GUI Version: {version}')
        wsl_distro_version = self.get_wsl_distro_version(self.master.driver)
        if version != wsl_distro_version:
            logging.debug(f'wsl_distro_version={wsl_distro_version!r}')
            logging.error('Version Mismatch.')
            messagebox.showerror("Version Mismatch",
                                 "GUI is in a different version than the registered wsl version. Please confirm the "
                                 "install_distribution.py script completed successfully while upgrading to a new "
                                 "version and that you are using the latest GUI.")

    @classmethod
    def get_wsl_distro_version(cls, driver: Driver):
        output = list(driver.run_cmd(r'cat /usr/local/bin/wsl_distro_version.txt'))
        out = ''
        for line in output:
            out += line.decode().strip()
        logging.info(f'WSL Distro version information: {out}')
        return out


class ChoosePipeline(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        self.pipeline_reference = tk.StringVar()
        self.pipeline_reference.set('16S')

        tk.Label(frame,
                 text="Pipeline Type",
                 justify=tk.CENTER,
                 padx=20).pack()

        tk.Radiobutton(frame,
                       text="16S pipeline",
                       padx=10,
                       variable=self.pipeline_reference,
                       value='16S').pack(anchor=tk.W)
        tk.Radiobutton(frame,
                       text="18S pipeline",
                       padx=10,
                       variable=self.pipeline_reference,
                       value='18S').pack(anchor=tk.W)
        tk.Radiobutton(frame,
                       text="other (provide .fasta file in next step)",
                       padx=10,
                       variable=self.pipeline_reference,
                       value='other').pack(anchor=tk.W)
        self.frame.pack()

    def on_next(self):
        self.master.values['pipeline_reference'] = self.pipeline_reference.get()
        logging.info(f"Pipeline_reference: pipeline_reference={self.master.values['pipeline_reference']}")


class ChoosePipelineReferenceFasta(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        if self.master.values['pipeline_reference'] != 'other':
            raise SkipSubframe

        tk.Label(frame,
                 text="Choose pipeline reference",
                 justify=tk.CENTER,
                 padx=20).pack()

        tk.Label(frame,
                 text=f"Select a .fasta file with used as reference for\n"
                      f"chimera removal, filtering and taxonomy.",
                 justify=tk.LEFT,
                 padx=20).pack()

        tk.Button(frame, text="Select reference file", command=self.browse_file).pack()
        self.file_path = tk.Entry(frame, width=55, state='disabled')
        self.file_path.pack()
        self.frame.pack()

    def on_next(self):
        path = self.file_path.get()
        print(repr(path))

        if path == '':
            messagebox.showerror("Missing reference file",
                                 f"Select another pipeline type if you do not want to provide a reference file.")
            raise DenyNextSubframe

        if not path.endswith(".fasta"):
            messagebox.showerror("Fasta file required",
                                 f"Reference file needs to be a .fasta file.")
            raise DenyNextSubframe

        # overwrite pipeline reference value with path
        self.master.values['pipeline_reference'] = self.file_path.get()
        logging.info(f"Pipeline_reference: pipeline_reference={self.master.values['pipeline_reference']}")

    def browse_file(self):
        filename = filedialog.askopenfilename()
        self.file_path['state'] = 'normal'
        self.file_path.delete(0, 'end')
        self.file_path.insert(0, filename)
        self.file_path['state'] = 'disabled'
        logging.info(f"selected reference file path path: {filename}")


class ChooseMode(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        self.mode = tk.StringVar()
        self.mode.set('zotu')

        tk.Label(frame,
                 text="Mode",
                 justify=tk.CENTER,
                 padx=20).pack()

        tk.Radiobutton(frame,
                       text="generate OTUs",
                       padx=10,
                       variable=self.mode,
                       value='otu').pack(anchor=tk.W)
        tk.Radiobutton(frame,
                       text="generate ZOTUs",
                       padx=10,
                       variable=self.mode,
                       value='zotu').pack(anchor=tk.W)
        self.frame.pack()

    def on_next(self):
        self.master.values['mode'] = self.mode.get()
        logging.info(f"Mode: mode={self.master.values['mode']}")


class ChooseReadType(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        self.studyType = tk.IntVar()
        self.studyType.set(1)

        tk.Label(frame,
                 text="Read Type",
                 justify=tk.CENTER,
                 padx=20).pack()

        tk.Radiobutton(frame,
                       text="Paired-End (R1 and R2 file)",
                       padx=10,
                       variable=self.studyType,
                       value=1).pack(anchor=tk.W)
        tk.Radiobutton(frame,
                       text="Single-End (R1 file)",
                       padx=10,
                       variable=self.studyType,
                       value=0).pack(anchor=tk.W)
        self.frame.pack()

    def on_next(self):
        self.master.values['isPaired'] = self.studyType.get()
        logging.info(f"Read type: isPaired={self.master.values['isPaired']}")


class ChooseDemultiplexing(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        self.run_demux = tk.IntVar()
        self.run_demux.set(0)

        if self.master.values['isPaired'] == 0:
            self.on_next()
            raise SkipSubframe

        tk.Label(frame,
                 text="Demultiplexing",
                 justify=tk.CENTER,
                 padx=20).pack()

        tk.Radiobutton(frame,
                       text=f"I have {'one' if self.master.values['isPaired'] == 0 else 'two'} files per sample. "
                            f"Don't run demultiplexing.",
                       padx=10,
                       variable=self.run_demux,
                       value=0).pack(anchor=tk.W)
        tk.Radiobutton(frame,
                       text=f"I have {'one' if self.master.values['isPaired'] == 0 else 'two'} fastq files.  "
                            f"Run demultiplexing.",
                       padx=10,
                       variable=self.run_demux,
                       value=1).pack(anchor=tk.W)
        self.frame.pack()

    def on_next(self):
        self.master.values['run_demux'] = self.run_demux.get()
        logging.info(f"Demultiplexing: run_demux={self.master.values['run_demux']}")


class ChooseIndexing(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        self.twoIndexes = tk.IntVar()
        self.twoIndexes.set(0)

        if self.master.values['run_demux'] == 0:
            self.on_next()
            raise SkipSubframe

        tk.Label(frame,
                 text="Indexing",
                 justify=tk.CENTER,
                 padx=20).pack()

        tk.Radiobutton(frame,
                       text="Single-Indexed (I1 file)",
                       padx=10,
                       variable=self.twoIndexes,
                       value=0).pack(anchor=tk.W)
        tk.Radiobutton(frame,
                       text="Double-Indexed (I1 and I2 file)",
                       padx=10,
                       variable=self.twoIndexes,
                       value=1).pack(anchor=tk.W)
        self.frame.pack()

    def on_next(self):
        self.master.values['twoIndexes'] = self.twoIndexes.get()
        logging.info(f"Indexing: twoIndexes={self.master.values['twoIndexes']}")


class Preprocessing(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        self.run_spike_removal = tk.IntVar()
        self.run_spike_removal.set(0)

        if self.master.values['isPaired'] == 0 or self.master.values['run_demux'] == 1:
            self.on_next()
            raise SkipSubframe

        tk.Label(frame,
                 text="Preprocessing",
                 justify=tk.CENTER,
                 padx=20).pack()

        tk.Checkbutton(frame, text='Run spike removal',
                       variable=self.run_spike_removal,
                       onvalue=1, offvalue=0).pack(anchor=tk.W)
        tk.Label(frame,
                 text="For spike removal please provide a mapping file \n"
                      "with weights in the next steps. \n",
                 justify=tk.LEFT,
                 padx=20).pack()
        self.frame.pack()

    def on_next(self):
        self.master.values['run_spike_removal'] = self.run_spike_removal.get()
        logging.info(f"Preprocessing: run_spike_removal={self.master.values['run_spike_removal']}")


class FolderSelection(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        tk.Label(frame,
                 text="Folder selection",
                 justify=tk.CENTER,
                 padx=20).pack()

        tk.Label(frame,
                 text="Please select a folder containing your files now.\n"
                      "Folder must contain:\n"
                      f"- A subfolder named 'fastq' containing \n{'R1' if self.master.values['isPaired'] == 0 else 'R1 and R2'} "
                      f"{'files per sample' if self.master.values['run_demux'] == 0 else 'file'}\n"
                      f"{'- The fastq subfolder must also contain I1 ' if self.master.values['run_demux'] == 1 else ''}"
                      f"{'and I2' if self.master.values['run_demux'] == 1 and self.master.values['twoIndexes'] == 1 else ''}",
                 justify=tk.LEFT,
                 padx=20).pack()

        tk.Button(frame, text="Select data folder", command=self.browse_folder).pack()
        self.folder_path = tk.Entry(frame, width=55, state='disabled')
        self.folder_path.pack()
        self.frame.pack()

    def on_next(self):
        path = self.folder_path.get()
        if path == "":
            messagebox.showerror("Required option missing", "Please select a folder. This is required.")
            raise DenyNextSubframe

        # check if we have a fastq subfolder with sample files
        if not os.path.isdir(os.path.join(path, 'fastq')):
            messagebox.showerror("Missing subfolder 'fastq'",
                                 f"Missing a subfolder named {os.path.join(path, 'fastq')} at {path}.")
            raise DenyNextSubframe

        if self.master.values['run_demux'] == 0:
            fitting_files = ngssdk.count_files(os.path.join(path, 'fastq'),
                                               accepted_extensions=('.fastq', '.fastq.gz'),
                                               validator=ngssdk.has_illumina_read_naming_scheme)
            if fitting_files < 1:
                messagebox.showerror("No fastq or fastq.gz files at folder 'fastq'",
                                     f"Could not identify illumina files at {os.path.join(path, 'fastq')}")
                raise DenyNextSubframe

        if self.master.values['run_demux'] == 1:
            if not (os.path.isfile(os.path.join(path, 'fastq', 'I1.fastq')) or os.path.isfile(
                    os.path.join(path, 'fastq', 'I1.fastq.gz'))):
                messagebox.showerror("Missing file 'I1.fastq'",
                                     f"Missing a file called I1.fastq at {os.path.join(path, 'fastq')}.")
                raise DenyNextSubframe

            if self.master.values['twoIndexes'] == 1:
                if not (os.path.isfile(os.path.join(path, 'fastq', 'I2.fastq')) or os.path.isfile(
                        os.path.join(path, 'fastq', 'I2.fastq.gz'))):
                    messagebox.showerror("Missing file 'I2.fastq'",
                                         f"Missing a file called I2.fastq at {os.path.join(path, 'fastq')}.")
                    raise DenyNextSubframe

        self.master.values['folder_path'] = self.folder_path.get()
        logging.info(f"Folder: folder={self.master.values['folder_path']}")

    def browse_folder(self):
        filename = filedialog.askdirectory()
        self.folder_path['state'] = 'normal'
        self.folder_path.delete(0, 'end')
        self.folder_path.insert(0, filename)
        self.folder_path['state'] = 'disabled'
        logging.info(f"selected folder path: {filename}")


class MapfileSelection(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        tk.Label(frame,
                 text="Mapping File selection",
                 justify=tk.CENTER,
                 padx=20).pack()

        tk.Label(frame,
                 text=f"Mapping file is {'required.' if self.is_mapfile_required() else 'optional.'}\n" +
                      f"Only files listed in the mapping file will be processed." +
                      f"\nYou may only study a subset of your files by giving\na reduced mapping file.\n" +
                      f"{'For spike removal this additional columns are required:' if self.master.values['run_spike_removal'] == 1 else ''}\n" +
                      f"{'- total_weight_in_g' if self.master.values['run_spike_removal'] == 1 else ''}\n" +
                      f"{'- amount_spike' if self.master.values['run_spike_removal'] == 1 else ''}\n",
                 justify=tk.LEFT,
                 padx=20).pack()

        tk.Button(frame, text="Select mapping file", command=self.browse_file).pack()
        self.file_path = tk.Entry(frame, width=55, state='disabled')
        self.file_path.pack()
        self.frame.pack()

    def on_next(self):
        path = self.file_path.get()

        if self.is_mapfile_required():
            if path == '':
                messagebox.showerror("Missing mapping file",
                                     f"Please provide a mapping file. "
                                     f"A mapping file is required when demultiplexing or spike removal is selected.")
                raise DenyNextSubframe

        # verify weights column for spike removal
        if self.master.values['run_spike_removal'] == 1:
            ok, reason = self.check_spike_mapfile(path)
            if not ok:
                messagebox.showerror("Faulty mapping file",
                                     f"Please provide a mapping file for spike removal. "
                                     f"{reason}")
                raise DenyNextSubframe

        self.master.values['mapping_file'] = self.file_path.get()
        logging.info(f"Mapping file: mapfile={self.master.values['mapping_file']}")

    def browse_file(self):
        filename = filedialog.askopenfilename()
        self.file_path['state'] = 'normal'
        self.file_path.delete(0, 'end')
        self.file_path.insert(0, filename)
        self.file_path['state'] = 'disabled'
        logging.info(f"selected mapping file path path: {filename}")

    def is_mapfile_required(self):
        if self.master.values['run_spike_removal'] == 1:
            return True
        if self.master.values['run_demux'] == 1:
            return True
        return False

    @classmethod
    def check_spike_mapfile(cls, mapfilepath):
        sample_col_name = "SampleID"
        weight_col_name = "total_weight_in_g"
        amount_col_name = "amount_spike"
        with open(mapfilepath, 'r') as mapping_file_h:
            header: str = next(mapping_file_h)

            if not header.startswith('#'):
                return False, 'No header in mapping file'

            columns = header.split('\t')
            index_of_sample_id_col = None
            index_of_weight_col = None
            index_of_amount_col = None
            for i, col in enumerate(columns):
                colname = col.strip().lstrip('#')

                if colname == sample_col_name:
                    index_of_sample_id_col = i
                elif colname == weight_col_name:
                    index_of_weight_col = i
                elif colname == amount_col_name:
                    index_of_amount_col = i

            if index_of_sample_id_col is None:
                return False, f'Column {sample_col_name!r} missing in header'

            if index_of_weight_col is None:
                return False, f'Column {weight_col_name!r} missing in header'

            if index_of_amount_col is None:
                return False, f'Column {amount_col_name!r} missing in header'

            return True, ''


class IMNGSAdvancedOptions(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        self.run_spike_removal = tk.IntVar()
        self.run_spike_removal.set(0)

        tk.Label(frame,
                 text="Advanced IMNGS Options",
                 justify=tk.CENTER,
                 padx=20).pack()

        self.is_uint = (frame.register(self.validate_unsigned_int), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.is_int = (frame.register(self.validate_int), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')

        self.bcmismatch = tk.StringVar()
        self.bcmismatch.set('1')
        tk.Label(frame,
                 text="Allowed mismatches (default=1):",
                 justify=tk.LEFT).pack()
        tk.Entry(frame,
                 width=5,
                 textvariable=self.bcmismatch,
                 validate='key', validatecommand=self.is_uint).pack()

        self.minmergelen = tk.StringVar()
        self.minmergelen.set('300')
        tk.Label(frame,
                 text="Min. read length (default=300):",
                 justify=tk.LEFT).pack()
        tk.Entry(frame,
                 width=5,
                 textvariable=self.minmergelen,
                 validate='key', validatecommand=self.is_uint).pack()

        self.maxmergelen = tk.StringVar()
        self.maxmergelen.set('600')
        tk.Label(frame,
                 text="Max. read length (default=600):",
                 justify=tk.LEFT).pack()
        tk.Entry(frame,
                 width=5,
                 textvariable=self.maxmergelen,
                 validate='key', validatecommand=self.is_uint).pack()

        self.fwdtrim = tk.StringVar()
        self.fwdtrim.set('17')
        tk.Label(frame,
                 text="Forward trim (default=17):",
                 justify=tk.LEFT).pack()
        tk.Entry(frame,
                 width=5,
                 textvariable=self.fwdtrim,
                 validate='key', validatecommand=self.is_uint).pack()

        self.rwtrim = tk.StringVar()
        self.rwtrim.set('21')
        tk.Label(frame,
                 text="Reverse trim (default=21):",
                 justify=tk.LEFT).pack()
        tk.Entry(frame,
                 width=5,
                 textvariable=self.rwtrim,
                 validate='key', validatecommand=self.is_uint).pack()

        self.abund = tk.StringVar()
        self.abund.set('0.0025')
        tk.Label(frame,
                 text="Abundance Filter (default=0.0025):",
                 justify=tk.LEFT).pack()
        tk.Entry(frame,
                 width=6,
                 textvariable=self.abund).pack()

        self.lowreadsamplecutoff = tk.StringVar()
        self.lowreadsamplecutoff.set('-1')
        tk.Label(frame,
                 text="Filter low read samples. Give cutoff or -1 to disable. (default=-1=off):",
                 justify=tk.LEFT).pack()
        tk.Entry(frame,
                 width=9,
                 textvariable=self.lowreadsamplecutoff).pack()

        self.frame.pack()

    def on_next(self):
        self.master.values['bcmismatch'] = int(self.bcmismatch.get() if self.bcmismatch.get() != '' else 1)
        logging.info(f"IMNGS Settings: bcmismatch={self.master.values['bcmismatch']}")

        self.master.values['minmergelen'] = int(self.minmergelen.get() if self.minmergelen.get() != '' else 0)
        logging.info(f"IMNGS Settings: minmergelen={self.master.values['minmergelen']}")

        self.master.values['maxmergelen'] = int(self.maxmergelen.get() if self.maxmergelen.get() != '' else 600)
        logging.info(f"IMNGS Settings: maxmergelen={self.master.values['maxmergelen']}")

        self.master.values['forward_trim'] = int(self.fwdtrim.get() if self.fwdtrim.get() != '' else 5)
        logging.info(f"IMNGS Settings: forward_trim={self.master.values['forward_trim']}")

        self.master.values['reverse_trim'] = int(self.rwtrim.get() if self.rwtrim.get() != '' else 5)
        logging.info(f"IMNGS Settings: reverse_trim={self.master.values['reverse_trim']}")

        try:
            self.master.values['lowreadsamplecutoff'] = int(
                self.lowreadsamplecutoff.get() if self.lowreadsamplecutoff.get() != '' else -1)
        except:
            self.master.values['lowreadsamplecutoff'] = -1
        logging.info(f"IMNGS Settings: lowreadsamplecutoff={self.master.values['lowreadsamplecutoff']}")

        self.master.values['abundance'] = float(self.abund.get() if self.abund.get() != '' else 0.0025)
        logging.info(f"IMNGS Settings: abundance={self.master.values['abundance']}")

        self.master.values['trim_score'] = 20
        logging.info(f"IMNGS Settings: trim_score={self.master.values['trim_score']}")

        self.master.values['expected_error_rate'] = 0.02
        logging.info(f"IMNGS Settings: expected_error_rate={self.master.values['expected_error_rate']}")

        self.master.values['maxdiffpct'] = 10
        logging.info(f"IMNGS Settings: maxdiffpct={self.master.values['maxdiffpct']}")

    @classmethod
    def validate_int(cls, action, index, value_if_allowed,
                     prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed == '':
            return True  # allow deleting full entry
        if value_if_allowed is not None:
            try:
                int(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False

    @classmethod
    def validate_unsigned_int(cls, action, index, value_if_allowed,
                              prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed == '':
            return True  # allow deleting full entry
        if value_if_allowed is not None:
            try:
                return int(value_if_allowed) >= 0
            except ValueError:
                return False
        else:
            return False

    @classmethod
    def validate_between_0_and_1(cls, action, index, value_if_allowed,
                                 prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed == '':
            return True  # allow deleting full entry
        if value_if_allowed is not None:
            try:
                return 0 <= float(value_if_allowed) <= 1
            except ValueError:
                return False
        else:
            return False


class ProgOptions(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        tk.Label(frame,
                 text="Program Options",
                 justify=tk.CENTER,
                 padx=20).pack()

        self.clean_output = tk.IntVar()
        self.clean_output.set(1)

        tk.Checkbutton(frame, text='Keep intermediate output',
                       variable=self.clean_output,
                       onvalue=0, offvalue=1).pack(anchor=tk.W)
        tk.Label(frame,
                 text="If you want to keep intermediate files the output\n"
                      "folder will be several times larger!",
                 justify=tk.LEFT,
                 padx=20).pack()
        self.frame.pack()

    def on_next(self):
        self.master.values['cleanoutput'] = int(self.clean_output.get())


def execute_pipeline(pl):
    t = Thread(target=pl.execute)
    try:
        t.start()
    except ExecutionFailed as e:
        messagebox.showerror("Failed", e)
        raise e

    return t, pl


def check_warning_msg(msg):
    if msg == 'WARNING: Readcount failed for a file. Process continues...':
        messagebox.showinfo('WARNING!',
                            'Readcounting, a subprocess of the pipeline, identified faulty files (e.g. truncated). '
                            'The pipeline will continue but some files may not be processed. You may check the readcount_failed.tab file for probematic files. '
                            'To continue running simply close this message. If you want to quit, close the main GUI.')


def status(d: WSLDriver, main_thread: Thread, status_text_var: tk.Variable):
    cmd = 'cat /usr/local/bin/status.txt'
    old_msg = ""
    while main_thread.is_alive():
        try:
            stat = list(linAtWin.decoded_stream(d.run_cmd(cmd)))
            msg = stat[0]
            status_text_var.set(msg)
            if msg != old_msg:
                check_warning_msg(msg)
                logging.info(f'Status: {msg}')
                old_msg = msg
        except IndexError:
            pass
        sleep(0.5)


def check_finished(pl: Pipeline, f: Subframe):
    while True:
        if pl.finished:
            if pl.return_code == 0:
                logging.info('Success')
                logging.info(f"Created an output folder at {f.master.values['outpath']!r}")
                f.status_text.set('Finished. To run another analysis please restart the GUI.')
                messagebox.showinfo("Success", f"Created an output folder at {f.master.values['outpath']!r}")
            else:
                logging.error('Failure')
                f.status_text.set('Analysis failed. To run another analysis please restart the GUI.')
                messagebox.showerror("Failed", "Subprocess failed")
            break
        sleep(3)


class Run(Subframe):
    def __init__(self, master, frame):
        super().__init__(master, frame)

        tk.Label(frame,
                 text="Summary",
                 justify=tk.CENTER,
                 padx=20).pack()
        self.run_btn = tk.Button(frame, text="Run", command=self.run)
        self.run_btn['state'] = 'normal'
        self.run_btn.pack()

        self.status_text = tk.Variable()
        self.status_text.set('Press run to start. Status will be shown here.')

        tk.Label(frame,
                 textvariable=self.status_text,
                 justify=tk.CENTER,
                 padx=20).pack()

        self.frame.pack()

    def prepare_pipeline(self):
        path_containing_fastq_folder = self.master.values['folder_path']
        logging.debug(f'path_containing_fastq_folder={path_containing_fastq_folder}')

        working_dir = path_containing_fastq_folder
        logging.debug(f'working_dir={working_dir}')

        logging.debug(f'mapping_file={self.master.values["mapping_file"]}')

        # construct output folder name
        timestmp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        mode = self.master.values['mode']
        self.master.values['outpath'] = os.path.join(working_dir, f'out_{mode.upper()}_{timestmp}')
        logging.debug(f'output_folder={self.master.values["outpath"]}')

        pl = Pipeline()

        # try to mount network shares; allowed to fail with non network drives
        pl.add_work(Mount(self.master.driver, path_containing_fastq_folder))

        # unzip files in folder; needing Linux commands, so attach a fitting driver
        pl.add_work(GunzipPump(self.master.driver, os.path.join(working_dir, 'fastq'), keep_gz_files=False))

        if self.master.values['run_spike_removal'] == 1:
            # remove spikes
            pl.add_work(SpikeRemovalPump(self.master.driver, working_dir, self.master.values['mapping_file']))
            self.master.values['mapping_file'] = '/tmp/spikes_mapping_file.tab'
            working_dir = os.path.join(working_dir, 'fastq_samples')
        else:
            working_dir = os.path.join(working_dir, 'fastq')

        # run imngs
        imngs_conf = IMNGSConfig(pipeline_reference=self.master.values['pipeline_reference'],
                                 mapping_file=self.master.values['mapping_file'],
                                 outpath=self.master.values['outpath'],
                                 mode=self.master.values['mode'],
                                 isPaired=self.master.values['isPaired'],
                                 twoIndexes=self.master.values['twoIndexes'],
                                 runDemux=self.master.values['run_demux'],
                                 allow_barcode_mismatch=self.master.values['bcmismatch'],
                                 minmergelen=self.master.values['minmergelen'],
                                 maxmergelen=self.master.values['maxmergelen'],
                                 forward_trim=self.master.values['forward_trim'],
                                 reverse_trim=self.master.values['reverse_trim'],
                                 trim_score=self.master.values['trim_score'],
                                 expected_error_rate=self.master.values['expected_error_rate'],
                                 abundance=self.master.values['abundance'],
                                 maxdiffpct=self.master.values['maxdiffpct'],
                                 lowreadsamplecutoff=self.master.values['lowreadsamplecutoff'],
                                 cleanoutput=self.master.values['cleanoutput'])
        logging.info(imngs_conf)
        pl.add_work(IMNGSPump(self.master.driver, working_dir, imngs_conf))

        # normalize otus for spikes
        if self.master.values['run_spike_removal'] == 1:
            otu_table_name = 'OTUs-Table.tab' if self.master.values['mode'] == 'otu' else 'zOTUs-Table.tab'
            pl.add_work(
                SpikesNormalizerPump(self.master.driver, working_dir, self.master.values['outpath'], otu_table_name))

        # try to unmount network shares; allowed to fail with non network drives
        pl.add_work(Umount(self.master.driver, path_containing_fastq_folder))

        logging.debug(pl)
        return pl

    def run(self):
        self.run_btn['state'] = 'disabled'
        self.master.btn_next['state'] = 'disabled'
        self.master.btn_back['state'] = 'disabled'

        pl = self.prepare_pipeline()
        t, pl = execute_pipeline(pl)

        t2 = Thread(target=status, args=(self.master.driver, t, self.status_text))
        t2.start()

        Thread(target=check_finished, args=(pl, self)).start()


def main():
    driver: Driver = WSLDriver()

    root = tk.Tk()
    root.title(f'NGSToolkit {version}')
    app = Root(root, driver)
    root.protocol("WM_DELETE_WINDOW", app.quit)
    root.mainloop()


def logrotate():
    debug_file = 'debug.log'
    debug_old_file = 'debug_old.log'
    # check if debug.log is existent in folder and rename file to debug_old.log
    if os.path.isfile(debug_file):
        if os.path.isfile(debug_old_file):
            os.remove(debug_old_file)
        os.rename(debug_file, debug_old_file)


if __name__ == '__main__':
    # log file rotation
    # keep last 2 log files
    # rename existing log file to debug_old.log
    logrotate()

    # create new log file
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler("debug.log"),
            logging.StreamHandler()
        ]
    )

    main()
