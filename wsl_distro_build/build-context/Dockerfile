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
# GETTING SINA ###############################
##############################################
RUN  curl -L https://github.com/epruesse/SINA/releases/download/v1.7.2/sina-1.7.2-linux.tar.gz -o sina.tar.gz \
  && if [ $(md5sum ./sina.tar.gz) != "aa1aeffaf71a05cb764b0fbe80e4818b ./sina.tar.gz" ]; then echo "sina hash mismatch"; exit 1; fi \
  && tar -zxvf ./sina.tar.gz \
  && ln -s sina-*-linux/sina sina \
  && rm -rf ./sina.tar.gz


##############################################
# GETTING FASTTREE ###########################
##############################################
RUN  curl -L http://www.microbesonline.org/fasttree/FastTree -o FastTree \
  && if [ $(md5sum ./FastTree) != "e218e38103fa841295b315f24e9a2b9f ./FastTree" ]; then echo "FastTree hash mismatch"; exit 1; fi


##############################################
# GETTING DRIVE5 PYTHON SCRIPTS ##############
##############################################
RUN  curl -L https://drive5.com/python/python_scripts.tar.gz -o python_scripts.tar.gz \
  && if [ $(md5sum ./python_scripts.tar.gz) != "e40101abf5d17110dcc6a391eccbbef3 ./python_scripts.tar.gz" ]; then echo "drive5 python scripts hash mismatch"; exit 1; fi \
  # decompress
  && mkdir ./drive5_python_scripts \
  && tar -zxvf ./python_scripts.tar.gz -C ./drive5_python_scripts \
  # remove compressed
  && rm -rf ./python_scripts.tar.gz

RUN  echo "export PATH=/usr/local/bin/drive5_python_scripts:$PATH" >> ~/.profile


##############################################
# GETTING RDP CLASSIFIER #####################
##############################################
RUN  curl -L https://sourceforge.net/projects/rdp-classifier/files/rdp-classifier/rdp_classifier_2.13.zip -o rdp_classifier.zip \
  && if [ $(md5sum ./rdp_classifier.zip) != "027b54d65e9fbabf8b001dca0baffad2 ./rdp_classifier.zip" ]; then echo "rdp_classifier hash mismatch"; exit 1; fi \
  && unzip rdp_classifier.zip \
  && ln -s rdp_classifier_*/dist/classifier.jar rdp_classifier.jar \
  && rm -rf rdp_classifier.zip


##############################################
# GETTING BOWTIE2 ############################
##############################################
RUN  curl -L https://downloads.sourceforge.net/project/bowtie-bio/bowtie2/2.4.2/bowtie2-2.4.2-linux-x86_64.zip -o bowtie2.zip \
  && if [ $(md5sum ./bowtie2.zip) != "47600916f5c49e0c7b644975d55f1b38 ./bowtie2.zip" ]; then echo "bowtie2 hash mismatch"; exit 1; fi \
  && unzip bowtie2.zip \
  && ln -s bowtie2-*-linux-x86_64/bowtie2 bowtie2 \
  && rm -rf bowtie2.zip


##############################################
# GETTING SORTMERNA ##########################
##############################################
ARG sortmerna_version="4.3.2"
RUN  curl -L https://github.com/biocore/sortmerna/archive/refs/tags/v${sortmerna_version}.tar.gz -o sortmerna_source_code.tar.gz \
  && if [ $(md5sum ./sortmerna_source_code.tar.gz) != "22ac570cd7a00cb4d09cd29bbbec05c4 ./sortmerna_source_code.tar.gz" ]; then echo "sortmerna hash mismatch"; exit 1; fi \
  && tar -zxvf ./sortmerna_source_code.tar.gz \
  && rm -rf ./sortmerna_source_code.tar.gz \
  # executable
  && ln -s sortmerna-${sortmerna_version}/sortmerna sortmerna


##############################################
# DATABASES ##################################
##############################################
RUN  mkdir databases \
  && ls -al \
  && ln -s sortmerna-${sortmerna_version}/data/rRNA_databases/silva-*.fasta databases


##############################################
# FILE IMPORT ################################
##############################################
COPY app/entry.sh ./src/entry.sh
COPY app/offline_analysis_conf_runner.py ./src/offline_analysis_conf_runner.py
COPY app/offline-analysis-imngs-docker.pl ./src/offline-analysis.pl
COPY app/Analysis-readme.pdf ./src/Analysis-readme.pdf
COPY app/runDeMux.pl ./src/runDeMux.pl
COPY app/gold_refdb_usearch8.1_32.udb ./src/gold_refdb_usearch8.1.udb
COPY app/rm_spikes.py ./src/rm_spikes.py
COPY app/spikes_normalizer.py ./src/spikes_normalizer.py
COPY app/readcount.py ./src/readcount.py


##############################################
# WRITE VERSION INFO #########################
##############################################
ARG ngstoolkit_version
RUN  echo "${ngstoolkit_version}" > wsl_distro_version.txt


##############################################
# CLEAN APT-GET ##############################
##############################################
RUN rm -rf /var/lib/apt/lists/*


##############################################
# PREPARING FOR RUNNER #######################
##############################################
# execution rights for scripts
RUN  chmod -R +x /usr/local/bin
