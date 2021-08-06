# NGS Toolkit

## Download 
Full Download - Please download the zip file of the latest release (on the right side under 'Release')  <br>
Partial Download - Download the zip file under 'Code' (this does not include the wsl distribution file)  <br> <br>
Partial Download is only recommended if the wsl distribution file ('ngstoolkitdist.tar') is already downloaded. Download of this version is much faster. 

## Installation
Full Download
1. Extract the zip file
2. Execute the installation script - register_distribution.py
3. Open the GUI (gui.py)

Partial Download
1. Extract the zip file
2. Copy the wsl distribution file  ('ngstoolkitdist.tar') to the directory 
3. Execute the installation script - register_distribution.py
4. Open the GUI (gui.py)

## Usage 
The input files for the Tool are FASTQ files (zipped files are accespted). Additionally to the FASTQ file a mapping file can be provided (not mandatory).
The mapping file needs to be in a certain format

### Mapping File
Tab seperated text file  <br>
First column = #SampleID <br>
Please avoid to use special characters (no spaces in header names are allowed)

### Spike removal
If your data set include spike controls a mapping file is mandatory 

### Mapping File for Spike Removal
Tab seperated text file  <br>
First column = #SampleID <br>
Mandatory column = total_weight_in_g <br>
Mandatory column = total_amount <br>
If the stool weight is unknwon please write NA <br>
If the amount of added spike is unknown please write NA <br>
Please avoid to use special characters (no spaces in header names are allowed)

## HELP
For installation and useability a README file is provided and can be found in the downloaded folder. 

## Execute
### Get program version
`python3 -m ngspipeline.cli -v`

### Build WSL distribution tar file
`python3 -m ngspipeline.cli --export`

#### Speedup and custom files
##### 64-bit USEARCH
If you have a binary for the 64-bit version of USEARCH, you may put this into the `wsl_distro_build/build-context/opt` 
folder.
Notice that according to the licence, you are only allowed to run one instance of the binary at any time.

The free 32-bit version may be sufficient for small studies; this will be downloaded automatically in the build process 
and does not require you to put the binary in the `opt` folder.

##### pre-build SILVA-derived databases
You can put the SILVA-derived databases in the `wsl_distro_build/build-context/opt` folder, in order to simply copy them 
and skip the resource and time intensive build process.

For extracting these databases from a distribution tar file a helper script exists:

`bash ./helper-scripts/extract-silva-databases-from-tar.sh ngstoolkitdist.tar wsl_distro_build/build-context/opt`
