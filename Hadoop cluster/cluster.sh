#!/usr/bin/env bash

set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

usage() {
  cat <<EOF
Usage: $(basename "${BASH_SOURCE[0]}") [-h] [-v] [-f] -p 

Hadoop cluster run script.

You need to choose an option:

With -p FD the script will create files for mount them as disks.
Key -f can be used for choosing size of the files.
All process is automatic. Size must be set as number, not the word.
The units of the filesize are MEGABYTES! Desired input is 5 000.
  ---------------------------------------------------------------------------
  | IMPORTANT: The cluster needs 2 disks for correct work, so you must have | 
  | enough space on your filesystem, at least twice of your input.          |
  ---------------------------------------------------------------------------
*** You must have SUDO rights if you prefer that way of disks mounting. ***
             The files will be created in /opt directory


With -p FULLSTART the script will create HDFS formatting first.
You have to have 2 disks, mounted at /mnt mount point.
    ******************************************************************
    * WARNING! In this case all data on mounted disks may be erased! *
    ******************************************************************


With -p START the script will start with accessing to folders on mounted disks (formatted earlier)
-------------------------------------------------------------------------------------------------------
| IMPORTANT: In this case the names of the mounted (at /mnt) disks should be /namenode and /datanode! |
| And you need to change folder owners with command "chown 2001:2100" on both disks for correct work! |
-------------------------------------------------------------------------------------------------------


With -p CLEAR the script will delete the cluster completely



Two parameters  union is not support, please start script second time with other parameter

Available options:

-h, --help      Print this help and exit
-v, --verbose   Print script debug info
-f, --file      File creation and mount
-p, --part      Part of desired cluster task(SETUP or WORK)
--no-color      No color output

EOF
  exit
}

cleanup() {
  trap - SIGINT SIGTERM ERR EXIT
  # script cleanup here
}

setup_colors() {
  if [[ -t 2 ]] && [[ -z "${NO_COLOR-}" ]] && [[ "${TERM-}" != "dumb" ]]; then
    NOFORMAT='\033[0m' RED='\033[0;31m' GREEN='\033[0;32m' ORANGE='\033[0;33m' BLUE='\033[0;34m' PURPLE='\033[0;35m' CYAN='\033[0;36m' YELLOW='\033[1;33m'
  else
    NOFORMAT='' RED='' GREEN='' ORANGE='' BLUE='' PURPLE='' CYAN='' YELLOW=''
  fi
}

msg() {
  echo >&2 -e "${1-}"
}

die() {
  local msg=$1
  local code=${2-1} # default exit status 1
  msg "$msg"
  exit "$code"
}

parse_params() {
  # default values of variables set from params
  file=0
  part=''

  while :; do
    case "${1-}" in
    -h | --help) usage ;;
    -v | --verbose) set -x ;;
    --no-color) NO_COLOR=1 ;;
    -f | --file) file=$2 ;; # File size
    -p | --part) # Part of script
      part="${2-}"
      shift
      ;;
    -?*) die "Unknown option: $1" ;;
    *) break ;;
    esac
    shift
  done

  # check required params and arguments
  [[ -z "${part-}" ]] && echo "Run me with -h key for help" && die "Missing required parameter: part of the script!"
  return 0
}

parse_params "$@"
setup_colors

msg "${RED}Read parameters:${NOFORMAT}"
msg "- filesize: ${file}"
msg "- part of the script: ${part}"

case "$part" in
FD) echo "Creating two files with size: " $file ;
    if [[ $file -gt 0 ]]
     then 
      sudo mkdir /opt/NodeFiles
      sudo touch /opt/NodeFiles/first /opt/NodeFiles/second
      sudo truncate -s ${file}M /opt/NodeFiles/first
      sudo truncate -s ${file}M /opt/NodeFiles/second
      sudo mke2fs -t ext4 -F /opt/NodeFiles/first
      sudo mke2fs -t ext4 -F /opt/NodeFiles/second
      sudo losetup /dev/loop5 /opt/NodeFiles/first
      sudo losetup /dev/loop6 /opt/NodeFiles/second
      lsblk -f
      sudo mkdir /mnt/namenode
      sudo mkdir /mnt/datanode
      sudo mount -t ext4 /dev/loop5 /mnt/namenode
      sudo mount -t ext4 /dev/loop6 /mnt/datanode
      sudo chown 2001:2100 /mnt/namenode/
      sudo chown 2001:2100 /mnt/datanode/
      sudo chmod -R g+sw /mnt/datanode/
      echo "Done"
      echo "Now you have to start the script with -p FULLSTART for formatting and running the cluster."
      exit
    else
      echo "You have to set size of the files (as disks) with key -f and number"
      exit 1
    fi ;;
FULLSTART) docker-compose up -d;
           echo "Start formatting..."; docker exec -u hdfs -it namenode_namenode_1 /bin/bash -c "/opt/hadoop-3.1.2/bin/hdfs namenode -format cluster1"; 
           docker exec -u hdfs -d namenode_namenode_1 /bin/bash -c "/opt/hadoop-3.1.2/bin/hdfs namenode";
           echo "Namenode service on namenode is up"; sleep 3;
           docker exec -u yarn -d namenode_namenode_1 /bin/bash -c "/opt/hadoop-3.1.2/bin/yarn resourcemanager";
           echo "Resourcemanager on namenode is up"; sleep 3;
           docker exec -u hdfs -d namenode_datanode_1 /bin/bash -c "/opt/hadoop-3.1.2/bin/hdfs datanode";
           echo "Datanode service on datanode is up"; sleep 3;
           docker exec -u yarn -d namenode_datanode_1 /bin/bash -c "/opt/hadoop-3.1.2/bin/yarn nodemanager";
           echo "Nodemanager on datanode is up";
           echo "Cluster is ready" ;;
START)
       echo "Start on prepared cluster..."; 
       docker exec -u hdfs -d namenode_namenode_1 /bin/bash -c "/opt/hadoop-3.1.2/bin/hdfs namenode"; 
       echo "Namenode service on namenode is up"; sleep 3; 
       docker exec -u yarn -d namenode_namenode_1 /bin/bash -c "/opt/hadoop-3.1.2/bin/yarn resourcemanager"; 
       echo "Resourcemanager on namenode is up"; sleep 3;
       docker exec -u hdfs -d namenode_datanode_1 /bin/bash -c "/opt/hadoop-3.1.2/bin/hdfs datanode"; 
       echo "Datanode service on datanode is up"; sleep 3;  
       docker exec -u yarn -d namenode_datanode_1 /bin/bash -c "/opt/hadoop-3.1.2/bin/yarn nodemanager"; 
       echo "Nodemanager on datanode is up"; 
       echo "Cluster is ready"  ;;
CLEAR) echo "Deleting cluster...";
       docker-compose down ;;      
esac

