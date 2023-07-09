# Script to automate audio modding for UE4 games which use Criware audio banks and IoStore, such as AEW FF
# Author: peek6


# Usage:
#  - Point to a JSON config file in which you specify which tracks you want to replace in each AWB, and the new audio you want to replace each track with

# Credits:
# - Assumes Fmodel ( https://github.com/4sval/FModel/ ) was used to extract the uassets, acb, and awb files from the original game's archives
# - Uses https://github.com/blueskythlikesclouds/SonicAudioTools to extract the original game's audio tracks
# - Uses https://github.com/Thealexbarney/VGAudio to encode WAV files to HCA
# - Uses https://github.com/peek6/UEcastoc/ to pack modded uassets into IoStore UE4 containers
# - Uses https://www.fluffyquack.com/tools/unrealpak.rar to pack modded uassets into non-IoStore (legacy pak) UE4 containers
# - My audio track insertion code here is based heavily on https://github.com/TheSoraHD/HCAreplace/, but I added the capability to insert a batch
#   of audio tracks into an AWB, rather than needing to manually insert one at a time


import json
import os
import subprocess
from pathlib import Path
from criware_batch_replace_audio_tracks import batch_replace_tracks_in_awbs
import shutil
import sys

sys.path.append(".\\UEcastoc\\cpp")

from fix_manifest_and_pack_utils import fix_manifest_and_pack_iostore

# from pathlib import Path

#####################################
# EDIT THESE PARAMETERS AS DESIRED #
#####################################

top_level_json_filename = "top_config.json"

# all other configuration info should be in the JSON file

#####################################
# END OF USER-DEFINED PARAMETERS #
#####################################


# Merges the info from the various JSON files for each of the audio mods into a single Python dictionaries.
# TODO:  currently does not check for conflicts (e.g., 2 mods modifing the same track in the same bank) or for file existence
def populate_dictionaries(top_level_config_dict):

    banks_config_json_path = ".\\" + top_level_config_dict["banks_config_json_dir"]

    tracks_dict = {}

    # read in and merge the config files from the various audio mods specified in top_config.json
    for audio_mod in top_level_config_dict["audio_mods"]:
        print("Processing config.json for "+audio_mod)
        mod_config_path = ".\\" + top_level_config_dict['audio_mods_top_level_dir'] + '\\' + audio_mod
        mod_config_filename = mod_config_path + '\\' + "config.json"
        f_config = open(mod_config_filename) #TODO:  check for file existence
        config_dict = json.load(f_config)
        f_config.close()
        for awb_name in config_dict:
            for (original_track, new_track) in config_dict[awb_name].items():
                config_dict[awb_name][original_track] = mod_config_path + "\\" + new_track

        for awb_name in config_dict:
            if awb_name in tracks_dict: # TODO:  check for conflicts if 2 mods touch same track of same bank
                tracks_dict[awb_name] = {**tracks_dict[awb_name], **config_dict[awb_name]}
            else:
                tracks_dict[awb_name] = config_dict[awb_name]

    all_banks_config_dict = {}
    for audio_bank in tracks_dict:
        f_config_bank = open(banks_config_json_path + '\\' + audio_bank + '.json')  # TODO:  check for file existence
        banks_config_dict = json.load(f_config_bank)
        all_banks_config_dict[audio_bank] = banks_config_dict[audio_bank]
        f_config_bank.close()

    return all_banks_config_dict, tracks_dict


# Extract the audio for each of the banks using Sonic Audio Tools
def extract_audio_tracks(top_level_config_dict, banks_config_dict, tracks_dict):

    for audio_bank in tracks_dict:
        # Extract the ACB from the uasset
        acb_path = top_level_config_dict["original_game_asset_root"] + "\\" + top_level_config_dict["game_name"] + \
                   "\\" + banks_config_dict[audio_bank]["relative_path_to_uasset_with_acb"]
        acb_uasset_filename = acb_path + "\\" + audio_bank + ".uasset"
        acb_filename = audio_bank + ".acb"
        local_uasset_filename = audio_bank + ".uasset"

        f_in = open(acb_uasset_filename, "rb")
        uasset_buffer = f_in.read()
        start_acb = uasset_buffer.find(bytes("@UTF", 'UTF-8'))
        acb_buffer = uasset_buffer[start_acb:]
        f_in.close()

        sonic_audio_tools_path = ".\\SonicAudioTools\\Debug\\"

        f_out = open(acb_filename, "wb")
        f_out.write(acb_buffer)
        f_out.close()

        f_out = open(local_uasset_filename, "wb")
        f_out.write(uasset_buffer)
        f_out.close()

        if (banks_config_dict[audio_bank]["has_separate_acb_and_awb"] == True):
            awb_path = top_level_config_dict["original_game_asset_root"] + "\\" + top_level_config_dict["game_name"] + \
                       "\\" + banks_config_dict[audio_bank]["relative_path_to_awb"]
            awb_filename = banks_config_dict[audio_bank]["awb_filename"]
            shutil.copyfile(awb_path + "\\" + awb_filename, ".\\" + awb_filename)

        # Extract the original game's HCA files from the ACB
        # os.chdir(".\\SonicAudioTools\\Debug")
        my_cmd = '".\\SonicAudioTools\\Debug\\AcbEditor.exe" ' + audio_bank + '.acb' \
            # os.chdir('..\\..\\')
        print(my_cmd)
        temp = subprocess.call(my_cmd, shell=True)
        # os.system(my_cmd)


# Package the modded uassets or awbs
def package_mod(top_level_config_dict, all_banks_config_dict):
    for awb_file in all_banks_config_dict:
        if (all_banks_config_dict[awb_file]["found_errors_during_extraction"] or all_banks_config_dict[awb_file]["found_errors_during_insertion"]):  # errors were found, skip pack
            print("Errors encountered when creating " + awb_file + ".  Aborting packing " + awb_file + ".  Please correct the errors and rerun.")
        else:  # No errors found.  Go ahead and pak
            if (all_banks_config_dict[awb_file]["is_iostore"] == True):  # Use menv's tool to pak
                fix_manifest_and_pack_iostore(all_banks_config_dict[awb_file]["output_mod_folder_name"], all_banks_config_dict[awb_file]["menv_utoc_manifest_filename"], top_level_config_dict["menv_utoc_manifest_dir"], top_level_config_dict["uecastoc_executable_path"])
            else:  # Legacy pak based on Fluffyquack's tool
                filelist = open('filelist.txt', 'w+')
                filelist.write('\"' + all_banks_config_dict[awb_file]["output_mod_folder_name"] + '\*.*\" \"..\..\..\*.*\" ')
                filelist.close()
                os.system('UnrealPak.exe packed\\' + all_banks_config_dict[awb_file]["output_mod_folder_name"] + '.pak ' + '-create=filelist.txt --compress')

            if (top_level_config_dict["game_name"] == "AEWFightForever") and (awb_file == "ra"):  # prefetch hack for AEW ring announcer bank
                fix_manifest_and_pack_iostore(all_banks_config_dict[awb_file]["prefetch_output_mod_folder_name"],
                                              all_banks_config_dict[awb_file]["menv_utoc_manifest_filename"],
                                              top_level_config_dict["menv_utoc_manifest_dir"],
                                              top_level_config_dict["uecastoc_executable_path"])



def cleanup(all_banks_config_dict):
    print("Cleaning up...")
    Path('output.hca').unlink(missing_ok=True)
    Path('filelist.txt').unlink(missing_ok=True)
    for awb_file in all_banks_config_dict:
        Path(awb_file).mkdir(parents=True, exist_ok=True)
        shutil.rmtree(awb_file)
        if(awb_file=="ra"):
            Path(all_banks_config_dict[awb_file]["prefetch_output_mod_folder_name"]).mkdir(parents=True, exist_ok=True)
            shutil.rmtree(all_banks_config_dict[awb_file]["prefetch_output_mod_folder_name"])
        Path(all_banks_config_dict[awb_file]["output_mod_folder_name"]).mkdir(parents=True, exist_ok=True)
        shutil.rmtree(all_banks_config_dict[awb_file]["output_mod_folder_name"])
        Path(awb_file+'.uasset').unlink(missing_ok=True)
        Path(awb_file+'.acb').unlink(missing_ok=True)
        Path(awb_file+'.awb').unlink(missing_ok=True)
        if (all_banks_config_dict[awb_file]["is_iostore"] == True) or (awb_file == "ra"):
            Path('fixed_'+all_banks_config_dict[awb_file]["menv_utoc_manifest_filename"]).unlink(missing_ok=True)

def main():

    # make sure nothing is in the packed directory so that user knows if things fail and doesn't take previously generated mods
    Path('packed').mkdir(parents=True, exist_ok=True)
    shutil.rmtree('packed')

    f_top_level_json = open('.\\' + top_level_json_filename) #TODO:  check for file existence
    # load json file to dict:
    top_level_config_dict = json.load(f_top_level_json)
    f_top_level_json.close()

    all_banks_config_dict, tracks_dict = populate_dictionaries(top_level_config_dict)

    # Extract the audio for each of the banks using Sonic Audio Tools
    if(top_level_config_dict["run_hca_extraction"]==True):  # you can set this to false if you already extracted the original tracks and you don't want to re-run this every time
        extract_audio_tracks(top_level_config_dict, all_banks_config_dict, tracks_dict)

    # Generate new awb files with tracks replaced
    if(top_level_config_dict["run_hca_injection_and_pack"]==True): # you can set this to false if you only want to extract, and want to skip injection and packing
        updated_tracks_dict = batch_replace_tracks_in_awbs(top_level_config_dict, all_banks_config_dict, tracks_dict)  # Replace tracks with modded tracks
        package_mod(top_level_config_dict, all_banks_config_dict)  # package the mod

    if (top_level_config_dict["cleanup_after_running"] == True):
        cleanup(all_banks_config_dict)

    print("If all was successful, your mods should be in the 'packed' directory.  Enjoy!")

out_dict = main()
