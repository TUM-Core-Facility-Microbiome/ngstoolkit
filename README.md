# ngspipeline

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
