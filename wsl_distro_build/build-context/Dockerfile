FROM debian:buster

##############################################
# GETTING APT PACKAGES #######################
##############################################
RUN  apt-get update \
  && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
  # build-context dependencies
  build-essential curl unzip \
  # java
  default-jre \
  # python
  python python3 \
  # dependencies for rm_spikes
  gzip \
  # dependencies for spikes_normalization
  python3-pandas \
  # dependencies for database building
  sumaclust \
  # perl modules
  bioperl libswitch-perl \
  # clean
  && rm -rf /var/lib/apt/lists/*


##############################################
# WORKDIR STRUCTURE ##########################
##############################################
WORKDIR /usr/local/bin
RUN  mkdir ./src


##############################################
# DATABASES ##################################
##############################################
RUN  mkdir databases

COPY app/generate_databases.sh generate_databases.sh
RUN  chmod -R +x /usr/local/bin

# databases for filtering
ARG silva_release="release_138_1"
# file without file extension (.fasta.gz)
ARG silva_ssu_nr99_filename="SILVA_138.1_SSURef_NR99_tax_silva"

RUN  cd databases \
  && curl -L https://www.arb-silva.de/fileadmin/silva_databases/${silva_release}/Exports/${silva_ssu_nr99_filename}.fasta.gz -O \
  && gunzip *

COPY Dockerfile silva_${silva_release}-arc-16s-id95.fasta silva_${silva_release}-euk-18s-id95.fasta silva_${silva_release}-bac-16s-id90.fasta databases/

# maximum cpu to use in database generation
ARG max_cpu=48
RUN  cd databases \
  && if [ -f silva_${silva_release}-arc-16s-id95.fasta ] && [ -f silva_${silva_release}-euk-18s-id95.fasta ] && [ -f silva_${silva_release}-bac-16s-id90.fasta ]; then echo "Databases exist"; exit 0; fi \
  && generate_databases.sh ${silva_ssu_nr99_filename}.fasta ${silva_release} SSU ${max_cpu}


# arb
ARG silva_arb_file="SILVA_138.1_SSURef_NR99_12_06_20_opt.arb.gz"
RUN  cd databases \
  && curl -L https://www.arb-silva.de/fileadmin/silva_databases/${silva_release}/ARB_files/${silva_arb_file} -O \
  && gunzip *


# spikes database
COPY app/spikes.fasta databases/spikes.fasta


##############################################
# GETTING USEARCH ############################
##############################################
ARG usearch_version="11.0.667"

# If you have a 64 bit version put the executable in the app folder; 32 bit executable will be not downloaded then
# As docker requires at least one file to be copied, we also copy the dockerfile which must always exist
COPY Dockerfile app/usearch${usearch_version}_i86linux64* ./

RUN  if [ -f usearch${usearch_version}_i86linux64 ]; then mv usearch${usearch_version}_i86linux64 usearch; exit 0; fi \
  && curl -L https://www.drive5.com/downloads/usearch${usearch_version}_i86linux32.gz -o usearch.gz \
  && if [ $(md5sum ./usearch.gz) != "27cc6b779b899daa5d17a95fd0eeb69c ./usearch.gz" ]; then echo "usearch32 hash mismatch"; exit 1; fi \
  && gunzip usearch.gz

# udb database
RUN  usearch -makeudb_usearch databases/${silva_ssu_nr99_filename}.fasta -output ${silva_ssu_nr99_filename}.udb


##############################################
# GETTING SINA ###############################
##############################################
ARG sina_version="1.7.2"
RUN  curl -L https://github.com/epruesse/SINA/releases/download/v${sina_version}/sina-${sina_version}-linux.tar.gz -o sina.tar.gz \
  && if [ $(md5sum ./sina.tar.gz) != "aa1aeffaf71a05cb764b0fbe80e4818b ./sina.tar.gz" ]; then echo "sina hash mismatch"; exit 1; fi \
  && tar -zxvf ./sina.tar.gz \
  && ln -s sina-*-linux/sina sina \
  && rm -rf ./sina.tar.gz


##############################################
# GETTING FASTTREE ###########################
##############################################
ARG fasttree_version="2.1.11"
RUN  curl -L http://www.microbesonline.org/fasttree/FastTree -o FastTree_${fasttree_version} \
  && if [ $(md5sum ./FastTree_${fasttree_version}) != "e218e38103fa841295b315f24e9a2b9f ./FastTree" ]; then echo "FastTree hash mismatch"; exit 1; fi \
  && ln -s FastTree_${fasttree_version} FastTree


##############################################
# GETTING BOWTIE2 ############################
##############################################
ARG bowtie2_version="2.4.4"
RUN  curl -L https://downloads.sourceforge.net/project/bowtie-bio/bowtie2/${bowtie2_version}/bowtie2-${bowtie2_version}-linux-x86_64.zip -o bowtie2.zip \
  && if [ $(md5sum ./bowtie2.zip) != "6b73a78053ce4f30d53bf95c7358d03e ./bowtie2.zip" ]; then echo "bowtie2 hash mismatch"; exit 1; fi \
  && unzip bowtie2.zip \
  && ln -s bowtie2-*-linux-x86_64/bowtie2 bowtie2 \
  && rm -rf bowtie2.zip


##############################################
# GETTING SORTMERNA ##########################
##############################################
ARG sortmerna_version="4.3.3"
RUN  curl -L https://github.com/biocore/sortmerna/releases/download/v${sortmerna_version}/sortmerna-${sortmerna_version}-Linux.tar.gz -o sortmerna.tar.gz \
  && if [ $(md5sum ./sortmerna.tar.gz) != "85b659dc000718e0b3c0de842dd1bb6c ./sortmerna_source_code.tar.gz" ]; then echo "sortmerna hash mismatch"; exit 1; fi \
  && tar -zxvf ./sortmerna.tar.gz \
  && ln -s sortmerna-${sortmerna_version}-*/bin/sortmerna sortmerna \
  && rm -rf ./sortmerna.tar.gz


##############################################
# FILE IMPORT ################################
##############################################
# helper scripts
COPY app/report_versions.sh .
COPY app/mount.py .
COPY app/umount.py .
COPY app/set_status.py .

# readcounting scripts
COPY app/readcount.py .
COPY app/filter_readcount.py .

# offline analysis scripts
COPY app/runDeMux.pl .
COPY app/offline-analysis.pl .
COPY app/offline-analysis-runner.py .

# spike scripts
COPY app/rm_spikes.py .
COPY app/spikes_normalizer.py .


##############################################
# WRITE VERSION INFO #########################
##############################################
ARG ngstoolkit_version
RUN  echo "${ngstoolkit_version}" > wsl_distro_version.txt
RUN  echo "This is a clean install of ${ngstoolkit_version}" > status.txt


##############################################
# CLEAN APT-GET ##############################
##############################################
RUN rm -rf /var/lib/apt/lists/*


##############################################
# PREPARING FOR RUNNER #######################
##############################################
# execution rights for scripts
RUN  chmod -R +x /usr/local/bin
