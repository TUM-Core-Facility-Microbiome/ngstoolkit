#!/usr/bin/env bash

archive="$1"

tmp_folder="/tmp/ngstoolkit-extract"
mkdir "${tmp_folder}"

path_inside_tar="usr/local/bin/databases/silva"
tar -xvf "${archive}" -C "${tmp_folder}" "${path_inside_tar}"

mv "${tmp_folder}"/"${path_inside_tar}"/silva_* ../wsl_distro_build/build-context/opt

rm -rf "${tmp_folder}"
