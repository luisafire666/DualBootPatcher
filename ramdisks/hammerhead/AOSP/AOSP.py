#!/usr/bin/env python3

import multiboot.fileio as fileio

import os
import re
import shutil
import sys

def modify_init_rc(directory):
  lines = fileio.all_lines('init.rc', directory = directory)

  f = fileio.open_file('init.rc', fileio.WRITE, directory = directory)
  for line in lines:
    if 'export ANDROID_ROOT' in line:
      fileio.write(f, line)
      fileio.write(f, fileio.whitespace(line) + "export ANDROID_CACHE /cache\n")

    elif re.search(r"mkdir /system(\s|$)", line):
      fileio.write(f, line)
      fileio.write(f, re.sub("/system", "/raw-system", line))

    elif re.search(r"mkdir /data(\s|$)", line):
      fileio.write(f, line)
      fileio.write(f, re.sub("/data", "/raw-data", line))

    elif re.search(r"mkdir /cache(\s|$)", line):
      fileio.write(f, line)
      fileio.write(f, re.sub("/cache", "/raw-cache", line))

    else:
      fileio.write(f, line)

  f.close()

def modify_fstab(directory, partition_config):
  lines = fileio.all_lines('fstab.hammerhead', directory = directory)

  system_fourth = 'ro,barrier=1'
  system_fifth = 'wait'
  cache_fourth = 'noatime,nosuid,nodev,barrier=1,data=ordered,noauto_da_alloc,journal_async_commit,errors=panic'
  cache_fifth = 'wait,check'

  f = fileio.open_file('fstab.hammerhead', fileio.WRITE, directory = directory)
  for line in lines:
    if re.search(r"^/dev[a-zA-Z0-9/\._-]+\s+/system\s+.*$", line):
      temp = re.sub("\s/system\s", " /raw-system ", line)

      if '/raw-system' in partition_config.target_cache:
        r = re.search(r"^([^\ ]+)\s+([^\ ]+)\s+([^\ ]+)\s+([^\ ]+)\s+([^\ ]+)", temp)
        temp = "%s %s %s %s %s\n" % (r.groups()[0], r.groups()[1], r.groups()[2],
                                     cache_fourth, cache_fifth)

      fileio.write(f, temp)

    elif re.search(r"^/dev[^\s]+\s+/cache\s+.*$", line):
      temp = re.sub("\s/cache\s", " /raw-cache ", line)

      if '/raw-cache' in partition_config.target_system:
        r = re.search(r"^([^\ ]+)\s+([^\ ]+)\s+([^\ ]+)\s+([^\ ]+)\s+([^\ ]+)", temp)
        temp = "%s %s %s %s %s\n" % (r.groups()[0], r.groups()[1], r.groups()[2],
                                     system_fourth, system_fifth)

      fileio.write(f, temp)

    elif re.search(r"^/dev[^\s]+\s+/data\s+.*$", line):
      temp = re.sub("\s/data\s", " /raw-data ", line)

      if '/raw-data' in partition_config.target_system:
        r = re.search(r"^([^\ ]+)\s+([^\ ]+)\s+([^\ ]+)\s+([^\ ]+)\s+([^\ ]+)", temp)
        temp = "%s %s %s %s %s\n" % (r.groups()[0], r.groups()[1], r.groups()[2],
                                     system_fourth, system_fifth)

      fileio.write(f, temp)

    else:
      fileio.write(f, line)

  f.close()

def modify_init_hammerhead_rc(directory):
  lines = fileio.all_lines('init.hammerhead.rc', directory = directory)

  previous_line = ""

  f = fileio.open_file('init.hammerhead.rc', fileio.WRITE, directory = directory)
  for line in lines:
    if re.search(r"^\s+mount_all\s+./fstab.hammerhead.*$", line) and \
        re.search(r"^on\s+fs\s*$", previous_line):
      fileio.write(f, line)
      fileio.write(f, fileio.whitespace(line) + "exec /sbin/busybox-static sh /init.multiboot.mounting.sh\n")

    # Change /data/media to /raw-data/media
    elif re.search(r"/data/media(\s|$)", line):
      fileio.write(f, re.sub('/data/media', '/raw-data/media', line))

    else:
      fileio.write(f, line)

    previous_line = line

  f.close()

def patch_ramdisk(directory, partition_config):
  modify_init_rc(directory)
  modify_fstab(directory, partition_config)
  modify_init_hammerhead_rc(directory)
