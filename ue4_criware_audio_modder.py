# Script to automate audio modding for UE4 games which use Criware audio banks and IoStore, such as AEW FF
# Author: peek6


# Usage:
#  - Point to a JSON config file in which you specify which tracks you want to replace in each AWB, and the new audio you want to replace each track with

# Credits:
# - Assumes Fmodel ( https://github.com/4sval/FModel/ ) was used to extract the uassets, acb, and awb files from the original game's archives
# - Uses https://github.com/blueskythlikesclouds/SonicAudioTools to extract the original game's audio tracks
# - Uses https://github.com/Thealexbarney/VGAudio to encode WAV files to HCA
# - Uses https://github.com/gitMenv/UEcastoc/ to pack modded uassets into IoStore UE4 containers
# - Uses https://www.fluffyquack.com/tools/unrealpak.rar to pack modded uassets into non-IoStore (legacy pak) UE4 containers
# - My audio track insertion code here is based heavily on https://github.com/TheSoraHD/HCAreplace/, but I added the capability to insert a batch
#   of audio tracks into an AWB, rather than needing to manually insert one at a time


import json
import os
# import mmap
# import shutil
# from pathlib import Path

#####################################
# EDIT THESE PARAMETERS AS DESIRED #
#####################################

# Set to your JSON directory.  TODO: eventually read in a JSON for each mod and combine them so that I can merge all modded tracks into a single bank.  For this to work, for any given bank, the new_bank_file_location field in the JSON should be set the same in all JSON files.
json_path = r'D:\games\tools\HCAreplace-main\HCAreplace-main\x64\Debug\config_files'

#TODO:  eventually do this for all JSON files in the audio mods folder and merge the dictionaries
json_filename = "sample_config.json"

# all other configuration info should be in the JSON file

#####################################
# END OF USER-DEFINED PARAMETERS #
#####################################


def wav_encoder(local_input, local_output, local_quality): #(const char* input, const char* output, const char* quality) {
    #char temp[512];
    print("Encoding... ")
    my_cmd = "VGAudioCli.exe -i "+local_input+" -o "+local_output+" --hcaquality " + local_quality
    print(my_cmd)
    os.system(my_cmd)
    return

def batch_replace_tracks_in_awbs(): # Replace audio tracks in AWBs with modded audio.  Corresponds to step#4 of my original tutorial
    HCAQuality_string_list = [
        "Highest",
        "High",
        "Middle",
        "Low",
        "Lowest"]

    json_fptr_target = open(json_path + '\\' + json_filename)
    # load json file to dict:
    tracks_dict = json.load(json_fptr_target)


    for awb_file in tracks_dict:
        found_errors = False
        tracks_to_replace = tracks_dict[awb_file]["batch_replace_tracks"]
        original_tracks_path = tracks_dict[awb_file]["original_tracks_path"]
        new_tracks_path = tracks_dict[awb_file]["new_tracks_path"]
        for track in tracks_to_replace:
            original_hca_filename = original_tracks_path + '\\' + track["original_track_name"] #config_dict[awb_file]["batch_replace_tracks"]["original_track_name"]
            modified_hca_filename = new_tracks_path + '\\' + track["new_track_name"] #config_dict[awb_file]["batch_replace_tracks"]["new_track_name"]

            f_original_hca = open(original_hca_filename, 'rb')
            f_modified = open(modified_hca_filename, 'rb')

            # read the HCA files into buffers
            oghca_buffer = f_original_hca.read()
            mod_buffer = f_modified.read()

            f_original_hca.close()
            f_modified.close()


            print("Original track "+track["original_track_name"]+" size:"+str(len(oghca_buffer)))


            header_buffer = mod_buffer[:3]
            hca_header = bytes("HCA", 'UTF-8')

            if header_buffer == hca_header:  # TODO: not tested
                print("New track " + track["new_track_name"] + "is already in HCA format.  Skipping conversion.")
                modhca_buffer = mod_buffer
                print("New track " + track["new_track_name"] + " size:" + str(len(modhca_buffer)))
                if ((len(oghca_buffer) >= len(modhca_buffer)) and (len(modhca_buffer) != 0)):
                    done_converting = True
                    track["is_error"] = False
            else:  # convert wav to HCA
                done_converting = False
                quality = 0
                while (done_converting==False) and (quality < 5):
                    wav_encoder(modified_hca_filename, "output.hca", HCAQuality_string_list[quality])
                    f_modified_hca = open("output.hca", 'rb')
                    modhca_buffer = f_modified_hca.read()
                    f_modified_hca.close()
                    print("Encoded HCA size with quality " + HCAQuality_string_list[quality] + ". Size = " + str(len(modhca_buffer)))
                    if ((len(oghca_buffer) >= len(modhca_buffer)) and (len(modhca_buffer) != 0)):
                        done_converting = True
                        track["is_error"] = False
                    else:
                        quality = quality + 1

                if (done_converting==False):
                    print("Can't compress HCA enough! Use a smaller WAV and try again.")
                    found_errors = True
                    track["is_error"] = True
                    track["modhca_buffer_size"] = len(modhca_buffer)
                    track["oghca_buffer_size"] = len(oghca_buffer)

                # Check new HCA size <= original HCA size .
                print("Modified HCA size: " +str(len(modhca_buffer)))

                if (len(oghca_buffer) < len(modhca_buffer)) or (len(modhca_buffer) == 0):
                    print("Modified HCA file not valid! Must be lower in size than the Original HCA.")
                    found_errors = True
                    track["is_error"] = True
                    track["modhca_buffer_size"] = len(modhca_buffer)
                    track["oghca_buffer_size"] = len(oghca_buffer)

            if (track["is_error"]==False): # confirmed new HCA size less than original, so zero-pad new HCA to make them equal and keep AWB aligned
                extra_bytes = len(oghca_buffer) - len(modhca_buffer)
                assert(extra_bytes >= 0)
                if(extra_bytes!=0):
                    modhca_buffer = modhca_buffer + (b'\0' * extra_bytes)
                    track["modhca_buffer"] = modhca_buffer
                    track["oghca_buffer"] = oghca_buffer
                    track["modhca_buffer_size"] = len(modhca_buffer)
                    track["oghca_buffer_size"] = len(oghca_buffer)

        if(found_errors): # Abort AWB conversion
            print("Errors found converting the following tracks to HCA. "+awb_file +" audio track insertion aborted.  Please fix the following errors and retry:")
            for track in tracks_to_replace:
                if (track["is_error"]):
                    print("ERROR: Original track "+track["original_track_name"]+" only has size "+str(track["oghca_buffer_size"]) +
                        " but new track "+track["new_track_name"]+" has size "+str(track["modhca_buffer_size"]))
        else: # no errors found in this AWB batch replace request, so replace tracks in AWB with new HCAs now guaranteed to be the same length
            print("No errors found converting the tracks to HCA.  Proceeding with "+awb_file +" audio track insertion...")
            original_awb_filename = tracks_dict[awb_file]["original_bank_file_location"] + "\\"+awb_file
            new_awb_filename = tracks_dict[awb_file]["new_bank_file_location"] + "\\" + awb_file


            f_original_awb = open(original_awb_filename, 'rb')
            awb_data = f_original_awb.read()
            original_awb_data_size = len(awb_data)
            f_original_awb.close()

            found_errors_during_insertion = False
            for track in tracks_to_replace:
                modhca_buffer = track["modhca_buffer"]
                oghca_buffer =  track["oghca_buffer"]
                assert(track["modhca_buffer_size"] == track["oghca_buffer_size"])
                found_hca_ptr = awb_data.find(oghca_buffer)
                if(found_hca_ptr==-1): # replace was not successful
                    print("ERROR: Original HCA "+track["original_track_name"]+" not found in AWB file "+awb_file)
                    found_errors_during_insertion = True
                else:
                    print("Found HCA "+track["original_track_name"]+" at address "+hex(found_hca_ptr))
                    awb_data = awb_data[:found_hca_ptr] + modhca_buffer + awb_data[(found_hca_ptr+track["modhca_buffer_size"]):]
                    assert(len(awb_data) == original_awb_data_size)
                    #awb_data[found_hca_ptr:(found_hca_ptr+track["modhca_buffer_size"])] = modhca_buffer

            if found_errors_during_insertion:
                print("Was not able to find all original HCA files. "+awb_file +" audio track insertion aborted.  Please fix the errors and retry.")
            else:
                # TODO:  check that directory for new AWB file exists, and that the new AWB file does not yet exist.
                f_new_awb = open(new_awb_filename, 'wb')
                f_new_awb.write(awb_data)
                f_new_awb.close()
                print("AWB "+new_awb_filename+" has been written with new audio tracks.")
                print("Enjoy your mod!")


def main():
    batch_replace_tracks_in_awbs()


main()
