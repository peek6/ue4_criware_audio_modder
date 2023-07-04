# _Criware Audio Bank Automated Extracter, Modifier, and Packager for Unreal Engine Game Mods_

#### By _**peek6**_

#### Configurable and extendable python-based tool to automate the process of audio modding in Unreal Engine games with Criware audio banks and a mix of IoStore and legacy packaging.  Sample audio mods and config files for the music and character voice banks in the AEW Fight Forever game are included.  This framework should be extendable to other banks and other games by adding new configuration files in config_files and new uecastoc manifest files in menv_utoc_maifests.

## Credits

 * Assumes Fmodel ( https://github.com/4sval/FModel/ ) was used to extract the uassets, acb, and awb files from the original game's archives
 * https://github.com/blueskythlikesclouds/SonicAudioTools for extracting the original game's audio tracks
 * https://github.com/Thealexbarney/VGAudio for encoding WAV files to HCA
 * https://github.com/peek6/UEcastoc/ (fork of https://github.com/gitmenv/UEcastoc) for packing modded uassets -> UE4 IoStore packages
 * Rewrote https://www.fluffyquack.com/tools/unrealpak.rar in Python to pack modded uassets into non-IoStore (legacy pak) UE4 containers
 * My audio track insertion code in criware_batch_replace_audio_tracks.py is based heavily on https://github.com/TheSoraHD/HCAreplace/, but I added the capability to batch replace the audio tracks

## Description

The script automates:
 - Extracting the audio tracks from the game's audio banks (it assumes you already extracted the banks themselves using Fmodel).
 - Merging different audio mods that all touch the same banks
 - Batch conversion of mod tracks in to HCA and batch insertion of modded tracks into the appropriate banks
 - Batch packaging of modded audio banks for both IoStore and legacy packaging modes. 
 
## Setup/Installation Requirements

All of my own code is written in Python3, which you can grab from  https://www.python.org/downloads/windows/ for Windows.  To run Python from any directory, you need to set your PATH variable properly, as described in https://www.youtube.com/watch?v=4V14G5_CNGg .  To run this tool, open a command prompt in the directory where you extracted the tool (e.g. the directory containing ue4_criware_audio_modder.py), and run:
    <pre>  python ue4_criware_audio_modder.py  </pre>
 
Assuming everything was set up correctly, your packaged mods will be in the "packed" directory, and, assuming they end in _P, you can copy them into your ~mods directory like any other UE4 mod.  

The only pieces that potentially need to be built are the submodules that the tool relies on:
 * https://github.com/blueskythlikesclouds/SonicAudioTools for extracting the original game's audio tracks
 * https://github.com/Thealexbarney/VGAudio for encoding WAV files to HCA
 * https://github.com/peek6/UEcastoc for packing modded uassets -> UE4 IoStore packages

These submodules can either be built following the instructions on their respective pages, or you can just grab my latest release where I have already built all of these tools for you.

Configuration of the tool is via JSON files, as described in the sections below.

 ## Making Your Own Audio Mods 

To make audio mods which can be processed by this tool, create a folder with the audio you want to inject into the game, and create a config.json in the same folder that follows the format of the sample config.json files in the audio_mods folders of this tool, namely:
<pre>
{
  "bank_name_without_any_file_extension": {
    "original_track_1.hca":  "replacement_track_1.wav",
    "orignal_track_2.hca":  "replacement_track_2.wav",
    "original_track_3.hca":  "replacement_track_3.wav"
  }
}
</pre>

You can replace as many or as few tracks as you want.  The names of the original tracks must match the names of the tracks when they are extracted by ACBEditor.exe from Sonic Audio Tools.  To find these names, you can follow the procedure described in the "Using This Tool As An Audio Bank Extraction Tool" section below.  After extraction, there should be a folder with the name of the bank, with that folder containing the original audio tracks with the names you will need to use in the config.json.

For each set of tracks, the replacement track must be small enough that when it is compressed to HCA, it is no larger than the original track it is replacing.   Note that the last set of tracks listed should not end with a comma.

Once you have a folder with the audio you want to inject into the game and the config.json set up as described above, just zip the folder, and your audio mod is done and now compatible with other audio mods (unless they modify the same track of the same bank).

I recommend testing your audio mod by running it through the tool as described in the "Using This Tool To Automatically Inject Audio Mods Into Your Game" section below.

## Using This Tool To Automatically Inject Audio Mods Into Your Game

This tool can inject any combination of audio mods (configured as described in the above section) into the game, by creating Unreal Engine packages compatible with the game.  The procedure is as follows:  
 * Unzip your audio mods into the audio_mods folder.  
 * Open top_config.json and select which of the audio mods in the audio_mods folder you want to package into .pak, .utoc, and .ucas mods that will be compatible with the game and will actually change the audio when you play your game.   Note that the last audio mod listed should not end with a comma.
 * Use Fmodel to extract the audio banks you want to inject audio into.  For AEW FF, select UE 4.27 and set the AES key to 0x766D2004BD1CA41B20A273CBEB8368FF267A819C30324F75B98C3EEAEB62BB1D .
 * Make a note of Fmodel's root Export directory (e.g., for AEWFF, this would be the parent directory of AEWFightForever\Content\GameData\... Assuming your Fmodel is set to default values, the root extraction directory probably looks like <the_output_directory_you_see_in_fmodel_settings>\Exports ).
 * Set the original_game_asset_root in your top_config.json to this Fmodel extraction root directory (e.g., for AEWFF, this would be the parent directory of AEWFightForever\Content\GameData\... ) 
 * Run this tool by opening a command prompt in the directory where you extracted this tool (e.g. the directory containing ue4_criware_audio_modder.py), and typing:
    <pre>  python ue4_criware_audio_modder.py  </pre>
 * Assuming everything was set up correctly, your packaged mods will be in the "packed" directory, and, assuming they end in _P, you can copy them into your ~mods directory like any other UE4 mod.  Enjoy!

## Using This Tool As An Audio Bank Extraction Tool

You can use this tool to extract audio as follows:
 * In top_config.json,  set run_hca_extraction to true, but change run_hca_injection_and_pack to false (to skip audio track injection and UE mod packaging) and change cleanup_after_running to false (so that the extracted banks and audio tracks are not removed).  In other words, your top_config.json should include:
<pre>
  "run_hca_extraction": true,
  "run_hca_injection_and_pack": false,
  "cleanup_after_running": false
</pre>
 * For any audio bank you want to extract, make sure you have at least one audio mods in your audio_mods directory which points to that bank, as the tool will only extract banks for which there is at least one audio mod in your audio_mods directory.  You should be able make a dummy audio mod by just having a subdirectory in your audio_mods directory with a config.json that looks like:
<pre>
{
  "bank_name_without_any_file_extension": {
  }
}
</pre>
* After extraction, you can open any .awb files in foobar (https://www.foobar2000.org/download) with the vgmstream plugin (https://github.com/vgmstream/vgmstream/) to listen to the audio and see which track is which.  If you don't see a .awb file for a bank, you can just open the .acb in foobar instead.
* After extraction, there should be a folder with the name of the bank, with that folder containing the original audio tracks with the original track names you will need to use in your config.json files when making audio mods.  
* Remember to set both run_hca_injection_and_pack and cleanup_after_running back to true to use this tool for modding.

## Using Fmodel To Extract the Audio Banks

This tool automates almost everything involved in audio modding, but it does assume that you have already extracted the original game's audio banks using Fmodel (https://github.com/4sval/FModel).  For example:
 * For AEW FF, Fmodel should be configured to use UE 4.27 and the AES key should be set to 0x766D2004BD1CA41B20A273CBEB8368FF267A819C30324F75B98C3EEAEB62BB1D
 * For the AEW FF music bank there is both an ACB and an AWB, with all the actual music data in the AWB as opposed to the ACB.  Use Fmodel to extract both the raw uasset for GameData/Assets/Audio/Music/music.uasset and the raw "uasset" for GameData/Resources/CriWareData/music.awb
 * For the AEW FF generic_roster bank, use Fmodel to extract GameData/Assets/Audio/Voice/Generic_Roster/generic_roster.uasset 
 * Make a note of Fmodel's root Export directory (e.g., for AEWFF, this would be the parent directory of AEWFightForever\Content\GameData\... Assuming your Fmodel is set to default values, the root extraction directory probably looks like <the_output_directory_you_see_in_fmodel_settings>\Exports ).
 * Set the original_game_asset_root in your top_config.json to this Fmodel extraction root directory (e.g., for AEWFF, this would be the parent directory of AEWFightForever\Content\GameData\... ) 
 

## ADVANCED:  Extending The Tool (not necessary if you want to mod music or character voices in AEWFF):

The tool is designed to be extendible to modding other banks in AEW and and to modding other games which use Criware and Uneal Engine.  To add support for new banks, create new configuration JSON files in the config_files directory which match the structure and naming conventions of generic_roster.json (for IoStore packaged banks where the entire bank is a single uasset containing an ACB file with all the audio tracks) or music.json (for audio banks where there is a separate ACB header and a separate AWB with the actual audio tracks, the ACB is in a uasset, and the AWB is directly packed into a .pak file without IoStore).  The name of the JSON should match the name of the bank (without file extensions).

To extend the tool to new banks packaged using IoStore, you also need to generate a manifest to be used by menv's uecastoc tool.  This can be done, for example, by making a dummy mod with (a placeholder for) the uasset containing that bank, which you would then pass to menv's uecastoc tool to get the manifest.  The procedure is as follows:
* Import any random audio file into the appropriate version of UE (UE4.27 for AEW FF), with the path and name of the audio bank you want to modify.  For example, to generate the manifest for generic_roster.uasset, I imported some random audio into UE as Content/GameData/Assets/Audio/Voice/Generic_Roster/generic_roster.uasset
* Package in UE as an IoStore chunk as if you are making any other normal mod.
* Append _P at the end of each UTOC/UCAS/PAK filename as you would with any other mod.
* Put this dummy mod into the "cpp" directory from https://github.com/peek6/UEcastoc.
* Open a command prompt at that "cpp" directory and run:
<pre>
         .\main.exe unpackAll .\pakchunk110-WindowsNoEditor_P.utoc .\pakchunk110-WindowsNoEditor_P.ucas output/
         .\main.exe manifest .\pakchunk110-WindowsNoEditor_P.utoc .\pakchunk110-WindowsNoEditor_P.ucas test_manifest.json
</pre>
 where instead of pakchunk110 in those two commands, you would use whichever chunk ID you used in UE, and where, instead of test_manifest.json (assuming you want to match my naming convention for generic_roster), you would append _manifest to the name of the the bank (without its various file extensions).  
 * Copy the manifest into the menv_utoc_manifests folder and point to it from the config file you created for your bank in config_files.


## Known Issues

  * No checking whether different audio mods modify the same track of the same bank
  * Need to add more robust error checking and handling to the script
  * Currently, the AEW generic_roster bank (e.g., the in-match character voices) and the AEW music bank are the only banks fully supported, but it should be straightforward to extend support to other banks.  
  * It would be nice if there were an option to also automatically extract the original game's audio banks.  I need to look into whether I can call Fmodel's API from a script.

Copyright (c) July 3, 2023 _peek6_