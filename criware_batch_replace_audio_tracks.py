# Function to batch-insert audio tracks into Criware AWB files.
# Author: peek6

# Usage:
# Takes a dictionary keyed by AWB name containing, for each AWB, the paths to the ACB/AWB and a list of pairs of original and replacement tracks

# Credits:
# Based heavily on https://github.com/TheSoraHD/HCAreplace/, but I added the capability to insert a batch
#   of audio tracks into an AWB, rather than needing to manually insert one at a time


import json
import os
# import mmap
# import shutil
from pathlib import Path



# Uses VGAudioCli from https://github.com/Thealexbarney/VGAudio to encode WAV files to HCA at specified quality
def wav_encoder(local_input, local_output, local_quality): #(const char* input, const char* output, const char* quality) {
    #char temp[512];
    print("Encoding... ")
    my_cmd = ".\\VGAudio\\bin\\Release\\cli\\net451\\VGAudioCli.exe -i "+local_input+" -o "+local_output+" --hcaquality " + local_quality
    print(my_cmd)
    os.system(my_cmd)
    return

# Replaces audio tracks in AWBs with modded audio.
# Corresponds to step#4 of my original tutorial
# Based on https://github.com/TheSoraHD/HCAreplace/, but I added the capability to insert a batch
# of audio tracks into an AWB, rather than needing to manually insert one at a time
def batch_replace_tracks_in_awbs(top_level_config_dict, all_banks_config_dict, tracks_dict_arg):
    HCAQuality_string_list = [
        "Highest",
        "High",
        "Middle",
        "Low",
        "Lowest"]

    #found_errors_during_extraction = {}
    #found_errors_during_insertion = {}


    # convert the tracks_dict dictionary to have a list with a dictionary for each track to replace
    tracks_dict = {}
    for awb_file in tracks_dict_arg:
        tracks_to_replace = tracks_dict_arg[awb_file]
        #new_track = {}
        tracks_dict[awb_file] = []
        for old_track, new_track_full_path in tracks_to_replace.items():
            tracks_dict[awb_file].append({})

            tracks_dict[awb_file][-1]["original_track_path"] = '.\\'+awb_file
            tracks_dict[awb_file][-1]["original_track_name"] = old_track
            tracks_dict[awb_file][-1]["new_track_path"] = ('\\').join(new_track_full_path.split('\\')[:-1])
            tracks_dict[awb_file][-1]["new_track_name"] = new_track_full_path.split('\\')[-1]





    for awb_file in tracks_dict:
        found_errors_during_extraction = False
        tracks_to_replace = tracks_dict[awb_file] #["batch_replace_tracks"]

        for track in tracks_to_replace:
            original_track_path = track["original_track_path"]
            new_track_path = track["new_track_path"]
            original_hca_filename = original_track_path + '\\' + track["original_track_name"] #config_dict[awb_file]["batch_replace_tracks"]["original_track_name"]
            modified_hca_filename = new_track_path + '\\' + track["new_track_name"] #config_dict[awb_file]["batch_replace_tracks"]["new_track_name"]

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
                    found_errors_during_extraction = True
                    track["is_error"] = True
                    track["modhca_buffer_size"] = len(modhca_buffer)
                    track["oghca_buffer_size"] = len(oghca_buffer)

                # Check new HCA size <= original HCA size .
                print("Modified HCA size: " +str(len(modhca_buffer)))

                if (len(oghca_buffer) < len(modhca_buffer)) or (len(modhca_buffer) == 0):
                    print("Modified HCA file not valid! Must be lower in size than the Original HCA.")
                    found_errors_during_extraction = True
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

        if(found_errors_during_extraction): # Abort AWB conversion
            print("Errors found converting the following tracks to HCA. "+awb_file +" audio track insertion aborted.  Please fix the following errors and retry:")
            for track in tracks_to_replace:
                if (track["is_error"]):
                    print("ERROR: Original track "+track["original_track_name"]+" only has size "+str(track["oghca_buffer_size"]) +
                        " but new track "+track["new_track_name"]+" has size "+str(track["modhca_buffer_size"]))
        else: # no errors found in this AWB batch replace request, so replace tracks in AWB with new HCAs now guaranteed to be the same length
            print("No errors found converting the tracks to HCA.  Proceeding with "+awb_file +" audio track insertion...")


            if(all_banks_config_dict[awb_file]["directly_package_awb"]==True): # insert tracks into AWB
                original_awb_filename = '.\\' + all_banks_config_dict[awb_file]["awb_filename"] # ' tracks_dict[awb_file]["original_bank_file_location"] + "\\"+awb_file
                mod_folder_name = ".\\"+all_banks_config_dict[awb_file]["output_mod_folder_name"] + "\\" + top_level_config_dict["game_name"] + "\\" + all_banks_config_dict[awb_file]["relative_path_to_awb"]
                new_awb_filename = mod_folder_name + "\\" + all_banks_config_dict[awb_file]["awb_filename"]
            else:  # insert tracks into uasset which contains awb
                original_awb_filename = '.\\' + all_banks_config_dict[awb_file]["uasset_with_acb_filename"]
                mod_folder_name = ".\\"+all_banks_config_dict[awb_file]["output_mod_folder_name"] + "\\" + top_level_config_dict["game_name"] + "\\" + all_banks_config_dict[awb_file]["relative_path_to_uasset_with_acb"]
                new_awb_filename = mod_folder_name + "\\" + all_banks_config_dict[awb_file]["uasset_with_acb_filename"]

            Path(mod_folder_name).mkdir(parents=True, exist_ok=True)

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

        all_banks_config_dict[awb_file]["found_errors_during_extraction"] = found_errors_during_extraction
        all_banks_config_dict[awb_file]["found_errors_during_insertion"] = found_errors_during_insertion

    return all_banks_config_dict, tracks_dict

