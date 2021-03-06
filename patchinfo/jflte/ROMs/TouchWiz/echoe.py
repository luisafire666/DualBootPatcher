from multiboot.fileinfo import FileInfo
import multiboot.autopatcher as autopatcher
import re

file_info = FileInfo()

# Didn't check Illusion
# Just so I don't need to redownload, illusion filenames:
#   Echoe_Illusion_RomTHEMED_v7_09Nov_Vzw_v2.zip
#   AT&T_Echoe_Illusion_Rom_v7_09Nov.zip
filename_regex           = [ r"^Echoe[ _]?(Rom|SLIM).*\.zip$",
                             r"^S4_Echoe.*\.zip" ]
file_info.ramdisk        = 'jflte/TouchWiz/TouchWiz.def'
file_info.patch          = autopatcher.auto_patch
file_info.extract        = autopatcher.files_to_auto_patch
file_info.bootimg        = 'boot.img'

def print_message():
  print("Detected Echoe TouchWiz ROM zip")

def matches(filename):
  for regex in filename_regex:
    if re.search(regex, filename):
      return True
  return False

def get_file_info():
  return file_info
