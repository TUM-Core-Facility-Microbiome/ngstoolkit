#!/usr/bin/env bash

archive="$1"
extract_to="$2"  # may often be wsl_distro_build/build-context/opt

tmp_folder="/tmp/ngstoolkit-extract"
mkdir "${tmp_folder}"

path_inside_tar="usr/local/databases/silva/build"
tar -xvf "${archive}" -C "${tmp_folder}" "${path_inside_tar}"

mv "${tmp_folder}"/"${path_inside_tar}"/* "${extract_to}"

rm -rf "${tmp_folder}"
