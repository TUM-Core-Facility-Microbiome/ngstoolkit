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


##############################################
# FILE IMPORT ################################
##############################################
COPY app .


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
