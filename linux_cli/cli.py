import datetime
import enum
import logging
import os
import subprocess
from typing import Optional

import click

import linAtWin
from linAtWin import Driver, DockerDriver
from ngspipeline.pipeline_subprogramms import GunzipPump, SpikeRemovalPump, IMNGSConfig, IMNGSPump, SpikesNormalizerPump
from pipeex import Pipeline

logging.basicConfig(level=logging.DEBUG)


@click.group()
def group():
    pass


@group.command('init')
@click.option('--tar-file-path', default='ngstoolkitdist.tar',
              help='Path from which to import docker image. Expecting tar file.')
@click.option('--docker-image-name', default='ngstoolkitdist:latest', help='Name of the docker image.')
@click.option('--docker-executable', default='docker',
              help='Name/Path of the docker executable. Allows for using the drop in replacement podman.')
def load_docker(tar_file_path, docker_image_name, docker_executable):
    """Load the distribution to a docker image."""
    logging.info(f"Importing {tar_file_path} as docker image {docker_image_name}")

    cmd = [docker_executable, 'import', tar_file_path, docker_image_name]
    logging.debug(f"Running {' '.join(cmd)}")
    process = subprocess.Popen(cmd)
    process.communicate()

    if process.returncode == 0:
        click.echo(click.style(f'Successfully imported docker image {docker_image_name}', fg='green'))
    else:
        click.echo(f'Failed importing docker image {docker_image_name} from {tar_file_path}', err=True)


@group.command('version')
@click.option('--docker-image-name', default='ngstoolkitdist:latest', help='Name of the docker image.')
@click.option('--docker-executable', default='docker',
              help='Name/Path of the docker executable. Allows for using the drop in replacement podman.')
def show_versions(docker_image_name, docker_executable):
    """Print version of distribution."""
    driver: Driver = DockerDriver(image_name=docker_image_name, docker_executable=docker_executable)

    cmd = 'report_versions.sh'
    logging.debug(f"Running {cmd} using {driver}")
    linAtWin.stream_output(driver.run_cmd(cmd))


class Mode(enum.Enum):
    OTU = 'otu'
    zOTU = 'zotu'


# def prepare_pipeline(
#         driver: DockerDriver,
#         working_dir: str,
#         mapping_file: Optional[str] = None,
#         output_folder: Optional[str] = None,
#         mode: Mode = Mode.zOTU,
#         is_run_spike_removal: bool = False,
# ):
#     # construct output folder name
#     if not output_folder:
#         _timestmp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
#         output_folder = os.path.join(working_dir, f'out_{mode.value.upper()}_{_timestmp}')
#
#     pl = Pipeline()
#
#     # unzip files in folder
#     pl.add_work(GunzipPump(driver, os.path.join(working_dir, 'fastq'), keep_gz_files=False))
#
#     if is_run_spike_removal:
#         # remove spikes
#         pl.add_work(SpikeRemovalPump(driver, working_dir, mapping_file))
#         mapping_file = '/tmp/spikes_mapping_file.tab'  # use mapping file generated by spikes step from now on
#         fq_path = os.path.join(working_dir, 'fastq_samples')
#     else:
#         fq_path = os.path.join(working_dir, 'fastq')
#
#     # run imngs
#     imngs_conf = IMNGSConfig(pipeline_reference=self.master.values['pipeline_reference'],
#                              mapping_file=self.master.values['mapping_file'],
#                              outpath=self.master.values['outpath'],
#                              mode=self.master.values['mode'],
#                              isPaired=self.master.values['isPaired'],
#                              twoIndexes=self.master.values['twoIndexes'],
#                              runDemux=self.master.values['run_demux'],
#                              allow_barcode_mismatch=self.master.values['bcmismatch'],
#                              minmergelen=self.master.values['minmergelen'],
#                              maxmergelen=self.master.values['maxmergelen'],
#                              forward_trim=self.master.values['forward_trim'],
#                              reverse_trim=self.master.values['reverse_trim'],
#                              trim_score=self.master.values['trim_score'],
#                              expected_error_rate=self.master.values['expected_error_rate'],
#                              abundance=self.master.values['abundance'],
#                              maxdiffpct=self.master.values['maxdiffpct'],
#                              lowreadsamplecutoff=self.master.values['lowreadsamplecutoff'],
#                              cleanoutput=self.master.values['cleanoutput'])
#     logging.info(imngs_conf)
#     pl.add_work(IMNGSPump(driver, fq_path, imngs_conf))
#
#     # normalize otus for spikes
#     if is_run_spike_removal:
#         otu_table_name = 'OTUs-Table.tab' if mode.value == 'otu' else 'zOTUs-Table.tab'
#         pl.add_work(SpikesNormalizerPump(driver, fq_path, output_folder, otu_table_name))
#
#     logging.debug(pl)
#     return pl
#
#
# @group.command('run')
# @click.argument('working_directory', help='Working dir. Path containing ./fastq sub-folder.')
# @click.option('--mapping-file', default=None, help='Path of mapping file.')
# @click.option('--output-folder', default=None, help='Name for output folder. Will be created in working dir.')
# @click.option('--zotu/--otu', 'is_zotu', default=True)
# @click.option('--spikes', is_flag=True, help='Run spike removal.')
# @click.option('--docker-image-name', default='ngstoolkitdist:latest', help='Name of the docker image.')
# @click.option('--docker-executable', default='docker',
#               help='Name/Path of the docker executable. Allows for using the drop in replacement podman.')
# def run(
#         working_directory,
#         mapping_file,
#         output_folder,
#         is_zotu,
#         spikes,
#         docker_image_name, docker_executable
# ):
#     logging.debug(f"working_directory={working_directory}")
#     logging.debug(f"mapping_file={mapping_file}")
#     logging.debug(f"output_folder={output_folder}")
#     logging.debug(f"is_zotu={is_zotu}")
#     logging.debug(f"spikes={spikes}")
#     # mounts: VolumeMountMap = VolumeMountMap()
#     #
#     #
#     # mounts.add()
#     # driver: Driver = DockerDriver(image_name=docker_image_name, docker_executable=docker_executable,
#     #                               volume_mount_map=mounts)
#     #
#     # pl: Pipeline = prepare_pipeline(driver, volume)
#     # pl.execute()


if __name__ == '__main__':
    group()
