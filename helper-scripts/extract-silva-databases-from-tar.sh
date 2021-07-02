#!/usr/bin/env bash

archive="$1"

tmp_folder="/tmp/ngstoolkit-extract"
mkdir "${tmp_folder}"

path_inside_tar="usr/local/databases/silva/build"
tar -xvf "${archive}" -C "${tmp_folder}" "${path_inside_tar}"

mv "${tmp_folder}"/"${path_inside_tar}"/* ../wsl_distro_build/build-context/opt

rm -rf "${tmp_folder}"
