#!/usr/bin/env python3
import configparser
import os

import ngssdk
from pipeex import *


def wsl_compatible_path(path: str) -> str:
    if path == "":
        return ""

    if path.startswith('/'):
        return path

    drive, path = os.path.splitdrive(path)
    path = path.replace('\\', '/')
    return f"/mnt/{drive.replace(':', '').lower()}{path}"


class Mount(Pump):
    def __init__(self, driver: linAtWin.Driver, win_directory: str):
        super().__init__()
        self.driver = driver
        self.win_directory = win_directory

    def prepare(self):
        pass

    def run(self):
        print(f'Exec {self.__class__.__name__}')
        self.mount(self.win_directory)

    def mount(self, path):
        cmd = f'mount.py "{path}"'
        print(cmd)
        linAtWin.log_output(self.driver.run_cmd(cmd))


class Umount(Pump):
    def __init__(self, driver: linAtWin.Driver, win_directory: str):
        super().__init__()
        self.driver = driver
        self.win_directory = win_directory

    def prepare(self):
        pass

    def run(self):
        print(f'Exec {self.__class__.__name__}')
        self.umount(self.win_directory)

    def umount(self, path):
        cmd = f'umount.py "{path}"'
        print(cmd)
        linAtWin.log_output(self.driver.run_cmd(cmd))


class GunzipPump(Pump):
    def __init__(self, driver: linAtWin.Driver, directory: str, keep_gz_files=True):
        super().__init__()
        self.driver = driver
        self.directory = directory
        self.keep_gz_files = keep_gz_files

    def prepare(self):
        number_of_gzipped_illumina_files = ngssdk.count_files(self.directory, accepted_extensions=('.gz',),
                                                              validator=ngssdk.has_illumina_read_naming_scheme)
        if number_of_gzipped_illumina_files < 1 or ngssdk.each_file_has_decompressed_version(self.directory):
            # we dont need to run
            raise SkipRest("No gunzip needed. No gzipped files found or files already unzipped.")

    def run(self):
        print(f'Exec {self.__class__.__name__}')
        self.driver.run_cmd('set_status.py "Decompressing files"')
        self.gunzip(keep=self.keep_gz_files)

        if not self.driver.success:
            print(self.driver)
            print(self.driver.process)
            print(self.driver.returncode)
            logging.error("Gunzip failed")
            raise ExecutionFailed

    def gunzip(self, keep=True):
        keep_flag = "-k " if keep else ""
        path = self.directory
        input_folder = wsl_compatible_path(path)

        cmd = f'gunzip -f {keep_flag}{input_folder}/*.fastq.gz'
        print(cmd)
        linAtWin.log_output(self.driver.run_cmd(cmd))


class SpikeRemovalPump(Pump):
    def __init__(self, driver: linAtWin.Driver, directory: str, mapping_file: str):
        super().__init__()
        self.driver = driver
        self.directory = directory

        self.spikes_ref = None
        self.mapping_file = mapping_file
        self.input_folder = None
        self.out_samples = None
        self.out_spikes = None
        self.out_stats = None

    def prepare(self):
        pass

    def precheck(self):
        count = ngssdk.count_files(os.path.join(self.directory, 'fastq'), accepted_extensions=('.fastq',),
                                   validator=ngssdk.has_illumina_read_naming_scheme)

        if count < 1:
            logging.error("No input files for spike removal")
            raise ExecutionFailed

    def run(self):
        path = self.directory
        inputpath = wsl_compatible_path(path)

        spikes_ref = f"/usr/local/bin/spikes.fasta"
        input_folder = f"{inputpath}/fastq"
        mapping_file = wsl_compatible_path(self.mapping_file)
        out_samples = f"{inputpath}/fastq_samples"
        out_spikes = f"{inputpath}/fastq_spikes"
        out_file_stats = f"{out_samples}/spikes.stats.tab"
        out_file_reduced_mapping = f"/tmp/spikes_mapping_file.tab"

        cmd = ["rm_spikes.py", spikes_ref, mapping_file,
               input_folder, out_samples, out_spikes,
               out_file_stats, out_file_reduced_mapping]
        linAtWin.log_output(self.driver.run_cmd(' '.join(cmd)))

        if not self.driver.success:
            logging.error("Spike removal failed")
            raise ExecutionFailed


IMNGSConfig = collections.namedtuple('IMNGSConfig',
                                     ['pipeline_reference', 'mapping_file', 'outpath', 'mode', 'isPaired', 'twoIndexes',
                                      'runDemux', 'allow_barcode_mismatch', 'minmergelen', 'maxmergelen',
                                      'forward_trim', 'reverse_trim', 'trim_score', 'expected_error_rate', 'abundance',
                                      'maxdiffpct', 'lowreadsamplecutoff', 'cleanoutput'])


class IMNGSPump(Pump):
    def __init__(self, driver: linAtWin.Driver, directory: str, config: IMNGSConfig):
        super().__init__()
        self.driver = driver
        self.directory = directory
        self.config: IMNGSConfig = config

    def prepare(self):
        self.config_file = os.path.join(self.directory, 'settings.ini')
        self.write_config(self.config_file, self.config)

    def run(self):
        path = wsl_compatible_path(self.directory)

        cmd = ['offline-analysis-runner.py', f'"{path}"', '"' + wsl_compatible_path(self.config_file) + '"']
        logging.info(f"Executing {' '.join(cmd)!r}")
        logging.info(f"Running Analysis. This may take a while...")
        linAtWin.log_output(self.driver.run_cmd(' '.join(cmd)))

    def postcheck(self):
        if not self.driver.success:
            logging.error("IMNGS failed")

            if self.driver.returncode == 1:
                logging.error("Analysis aborted")
                raise ExecutionFailed('Analysis aborted')
            elif self.driver.returncode == 2:
                logging.error("Analysis incomplete")
                raise ExecutionFailed('Analysis incomplete')
            elif self.driver.returncode == 3:
                logging.error("Analysis failed")
                raise ExecutionFailed('Analysis failed')
            elif self.driver.returncode == 4:
                logging.error("System error")
                raise ExecutionFailed('System error')

            raise ExecutionFailed('Uncaught error in analysis')

    @classmethod
    def write_config(cls, config_path: str, configuration: IMNGSConfig):
        pipe_ref = configuration.pipeline_reference
        if configuration.pipeline_reference not in ["16S", "18S"]:
            pipe_ref = wsl_compatible_path(configuration.pipeline_reference)

        config = configparser.ConfigParser()
        config['IMNGS_Settings'] = {
            'pipeline_reference': pipe_ref,  # 16S or 18S pipeline or reference .fasta file
            'mapping_file': 0 if wsl_compatible_path(configuration.mapping_file) == '' else wsl_compatible_path(
                configuration.mapping_file),
            'outpath': wsl_compatible_path(configuration.outpath),
            'mode': configuration.mode,
            'isPaired': configuration.isPaired,
            'twoIndexes': configuration.twoIndexes,
            'runDemux': configuration.runDemux,
            'allow_barcode_mismatch': configuration.allow_barcode_mismatch,
            # the number of allowed mismatches in the barcodes <=2
            'minmergelen': configuration.minmergelen,
            # 200 or 380 or 250 the minimum length allowed after pairing of reads
            'maxmergelen': configuration.maxmergelen,
            # 260 or 440 or 310 the maximum length allowed after pairing of reads

            'forward_trim': configuration.forward_trim,  # length of trimming at the forward side of a read
            'reverse_trim': configuration.reverse_trim,  # length of trimming at the reverse side of a read
            'trim_score': configuration.trim_score,  # the min quality score of the fastq read last position
            'expected_error_rate': configuration.expected_error_rate,
            # the max rate of expected errors allowed in the assembled paired end reads
            'abundance': configuration.abundance,
            # This is the abundance cutoff for an OTU. If no sample in the study has more than this the OTU is removed
            'maxdiffpct': configuration.maxdiffpct,
            # This is the maximum percentage of mismatches during merging of reads allowed.
            'lowreadsamplecutoff': configuration.lowreadsamplecutoff,
            'cleanoutput': configuration.cleanoutput
        }

        logging.debug(f'Write IMNGS config file to {config_path}')
        with open(config_path, 'w') as conf_handle:
            config.write(conf_handle)


class SpikesNormalizerPump(Pump):
    def __init__(self, driver: linAtWin.Driver, directory: str, output_path: str, otu_table_name: str):
        super().__init__()
        self.driver = driver
        self.directory = directory
        self.output_path = output_path
        self.otu_table_name = otu_table_name

    def run(self):
        # copy reduced mapping file
        linAtWin.log_output(self.driver.run_cmd(' '.join(['cp', '/tmp/spikes_mapping_file.tab',
                                                          wsl_compatible_path(
                                                              f'{self.output_path}/spikes_mapping_file.tab')])))

        path = self.directory

        otu_file = f"{wsl_compatible_path(self.output_path)}/{self.otu_table_name}"
        spikes_stats = f"{wsl_compatible_path(path)}/spikes.stats.tab"

        cmd = ["spikes_normalizer.py", otu_file, spikes_stats]
        print(' '.join(cmd))
        linAtWin.log_output(self.driver.run_cmd(' '.join(cmd)))

        if not self.driver.success:
            logging.error("IMNGS failed")
            raise ExecutionFailed

        linAtWin.log_output(self.driver.run_cmd(' '.join(['rm', '/tmp/spikes_mapping_file.tab'])))
