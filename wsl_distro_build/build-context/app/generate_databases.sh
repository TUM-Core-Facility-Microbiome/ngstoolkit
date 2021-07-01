#!/usr/bin/env bash

# Generate subdatabases for filtering with sortmeRna

ref_db=$1  # SILVA ref database as FASTA file
subunit=$2  # SSU or LSU
max_cpu=48


target_domains=( "Bacteria" "Eukaryota" "Archaea" )
source="silva"
if [ "${subunit}" = "SSU" ]; then
  filenames=( "${source}-bac-16s" "${source}-euk-18s" "${source}-arc-16s" )
  ident=( 0.90 0.95 0.95 )
elif [ "${subunit}" = "LSU" ]; then
  filenames=( "${source}-bac-23s" "${source}-euk-28s" "${source}-arc-23s" )
  ident=( 0.98 0.98 0.98 )
else
  >&2 echo -e "Unknown value for subunit. Can be SSU or LSU"
  exit 1
fi

# Generate sub-databases
for i in "${!target_domains[@]}"; do
  target_domain="${target_domains[i]}"
  filename="${filenames[i]}"
  id="${ident[i]}"
  echo "> Creating reference file for ${target_domain} clustered at ${id}"

  regex=" ${target_domain};"
  awk -v var="$regex" '/^>/ { p = ($0 ~ var)} p' "${ref_db}" > "${filename}"_U.fasta

  # check if filtering was successful
  echo ">>> Filtering for domain ${target_domain}"
  actual_domains=$(grep -e ">" "${filename}"_U.fasta | cut -f2 -d' ' | cut -f1 -d';' | sort -u)
  if [ "${actual_domains}" != "${target_domain}" ]; then
    >&2 echo -e "Filtering failed. The file contains none or unexpected domains:\n${actual_domains}"
    exit 128
  else
    echo "Filtering check OK."
  fi

  # convert U to T
  echo ">>> Converting U to T in sequences"
  awk '/^[^>]/{ seq=$1; gsub("U", "T", seq); print seq; next } 1' "${filename}"_U.fasta > "${filename}".fasta
  rm "${filename}"_U.fasta

  # clustering
  pct=${id:2:3}
  echo ">>> Clustering at ${pct}%"
  sumaclust -l -p ${max_cpu} -t "${id}" -F "${filename}"_sumaclust_"${pct}".fasta "${filename}".fasta

  # extracting cluster centroids
  echo ">>> Extracting cluster centroid sequences"
  awk '/^>/ {printf("\n%s\t",$0);next;} {printf("%s",$0);} END {printf("\n");}' "${filename}"_sumaclust_"${pct}".fasta \
           | egrep -v '^$' \
           | grep "cluster_center=True;" \
           | tr "\t" "\n" \
           > "${filename}"-id"${pct}".fasta
done
