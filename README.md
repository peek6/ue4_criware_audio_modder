Configurable and extendable python script to automate the process of audio modding in Unreal Engine games with Criware audio banks and a mix of IoStore and legacy packaging.  Sample audio mods and config files for the music and character voice banks in the AEW Fight Forever game are included.  This framework should be extendable to other banks and other games by adding new configuration files in config_files and new uecastoc manifest files in menv_utoc_maifests.     

The script automates:
 - Extracting the audio tracks from the game's audio banks (it assumes you already extracted the banks themselves using Fmodel).
 - Merging different audio mods that all touch the same banks
 - Batch conversion of mod tracks in to HCA and batch insertion of modded tracks into the appropriate banks
 - Batch packaging of modded audio banks for both IoStore and legacy packaging modes. 
 
 TODO:
  - No checking whether different audio mods modify the same track of the same bank
  - Add more robust error checking and handling to the script
  - Currently, the AEW generic_roster bank and music bank are the only banks fully supported, but it should be straightforward to extend support to other banks.  
 
 **************************
 
 To make your own audio mods: 

 - To make audio mods which can be processed by this tool, simply create a folder with the audio you want to inject into the game, and create a config.json in the same folder that follows the format of the sample config.json files in the audio_mods folders of this tool, namely:
 
{
  "bank_name_without_any_file_extension": {
    "original_track_1.hca":  "replacement_track_1.wav",
    "orignal_track_2.hca":  "replacement_track_2.wav",
    "original_track_3.hca":  "replacement_track_3.wav"
  }
}

You can replace as many or as few tracks as you want.  The names of the original tracks must match the names of the tracks when they are extracted by ACBEditor.exe from Sonic Audio Tools.  For each set of tracks, the replacement track must be small enough that when it is compressed to HCA, it is no larger than the original track it is replacing.   Note that the last set of tracks listed should not end with a comma.

Once you have a folder with the audio you want to inject into the game and the config.json set up as described above, just zip the folder, and your audio mod is done and now compatible with other audio mods (unless they modify the same track of the same bank).

I recommend testing your audio mod by running it through the tool as described in the "Using the tool" section below and verifying that the packaged UE4 mod works as expected in game.

****************************
 
Using the tool to automatically inject any combination of audio mods into your game:

 - Unzip your audio mods into the audio_mods folder.  
 
 - Open top_config.json and select which of the audio mods in the audio_mods folder you want to package into .pak, .utoc, and .ucas mods that will actually change the audio when you play your game.   Note that the last audio mod listed should not end with a comma.
 
 - Use Fmodel to extract the audio banks you want to inject audio into.  For AEW FF, select UE4.27 and set the AES key to 0x766D2004BD1CA41B20A273CBEB8368FF267A819C30324F75B98C3EEAEB62BB1D .  Extract the audio banks you want to mod and make a note of the root directory (e.g., for AEWFF, this would be the parent directory of AEWFightForever\Content\GameData\... Assuming your Fmodel is set to default values, the root extraction directory probably looks like <some_path>\Exports ).  Set the original_game_asset_root in your top_config.json to this root directory. 
 
 - Run this tool by opening a command prompt in the directory where you extracted this tool, and typing:
      python ue4_criware_audio_modder.py

 - Assuming everything was set up correctly, your packaged mods will be in the "packed" directory, and, assuming they end in _P, you can copy them into your ~mods directory like any other UE4 mod.  


Enjoy!

************************


ADVANCED:  Extending the tool (not necessary if you want to mod music or character voices in AEWFF):

The tool is designed to be extendible to modding other banks in AEW and other games entirely.  To add support for new banks, create new configuration JSON files in the config_files directory which match the structure and naming conventions of generic_roster.json (for IoStore packaged banks where the entire bank is a single uasset containing an ACB file with all the audio tracks) or music.json (for audio banks where there is a separate ACB header and a separate AWB with the actual audio tracks, the ACB is in a uasset, and the AWB is directly packed into a .pak file without IoStore).  The name of the JSON should match the name of the bank (without its various file extensions).

To extend the tool to new banks packaged using IoStore, you also need to generate a manifest to be used by menv's uecastoc tool.  This can be done for example, by making a dummy mod with (a placeholder for) the uasset containing that bank, which we will pass to menv's uecastoc tool to get the manifest.  So just import any random audio file into the appropriate version of UE (UE4.27 for AEW FF), with the path and name of the audio bank you want to modify.  For example, for generic_roster.uasset, I imported some random audio into UE as Content/GameData/Assets/Audio/Voice/Generic_Roster/generic_roster.uasset . Now package it as an IoStore chunk as if you are making any other normal mod.  Don't forget to put the _P at the end of each UTOC/UCAS/PAK filename as you would with any other mod.  Then put the dummy mod from step (5) into the "cpp" directory from step (6).  Open a command prompt at that cpp directory and run:
         .\main.exe unpackAll .\pakchunk110-WindowsNoEditor_P.utoc .\pakchunk110-WindowsNoEditor_P.ucas output/
         .\main.exe manifest .\pakchunk110-WindowsNoEditor_P.utoc .\pakchunk110-WindowsNoEditor_P.ucas test_manifest.json
where instead of pakchunk110 in those two commands, you would use whichever chunk ID you used in UE, and where, instead of test_manifest.json (assuming you want to match my naming convention for generic_roster) , you would append _manifest to the name of the the bank (without its various file extensions).  Then stick the manifest in the menv_utoc_manifests folder and point to it from the config file you created for your bank in config_files.


***********************

For completeness, I have included my previous manual AEW FF audio modding guide below.  Note that aside from step (1), the ue4_criware_audio_modder.py script in this repository automates all of the remaining steps for you, so there is no need for you to do them.  Step (3) may be useful for people who want to make their own audio mods, so that you can see the names of the original HCA tracks you want to replace, which you need to use when setting up your config.json for your audio mod.


Manual Character Voice Modding Tutorial (or, in general, IoStore audio modding tutorial).  NOTE:  IF YOU ARE USING MY ue4_criware_audio_modder.py SCRIPT FROM THIS REPO, YOU ONLY NEED TO DO STEP 1.  THE SCRIPT AUTOMATES EVERYTHING ELSE.

Part I:  Extraction

  1) Extract the raw uasset for the audio bank you want to hack using Fmodel ( https://github.com/4sval/FModel ).   For AEW FF, select UE4.27 and set the AES key to 0x766D2004BD1CA41B20A273CBEB8368FF267A819C30324F75B98C3EEAEB62BB1D .  Extract the audio banks you want to mod and make a note of the root directory (e.g., for AEWFF, this would be the parent directory of AEWFightForever\Content\GameData\... ).  Set the original_game_asset_root in your top_config.json to this root directory.
 
  2) Extract the ACB file from the uasset by opening the uasset in a hex editor, looking for the FIRST instance of the string @UTF and copying from @UTF (including @UTF) to the end of the file.  Paste it into a new hex file, and save the new hex file with a .acb extension (e.g., as generic_roster.acb in my example).  To test that you did this properly, you can try opening the acb file in foobar ( https://www.foobar2000.org/download ) with vgmstream plugin (https://github.com/vgmstream/vgmstream/releases/tag/r1843) installed. If it plays, you should be good to go to the next step.  
 
  3) Now we will extract the individual HCA files from the ACB.  Grab sonicaudiotools from https://github.com/blueskythlikesclouds/SonicAudioTools and then in windows explorer, just drag-and-drop your ACB from step (2) onto the ACBEditor.exe .  Alternatively, open a command prompt where you extracted your acb and run (with your ACB file instead of generic_roster.acb):   
     path_to_ACBEditor/ACBEditor.exe generic_roster.acb
  If this works, you should see a folder (in my example, it will be called generic_roster) with all the HCA files.  You can open any of the HCA files in foobar if you want.

Part 2:  Injection into uasset
 
  4) Grab https://github.com/TheSoraHD/HCAreplace and move:
      (a)  the folder with the extracted HCA files from step (3)
      (b)  the VGAudioCli.exe from https://github.com/Thealexbarney/VGAudio/releases/tag/v2.2.1
      (c)  the uasset from step (1) (for example, generic_roster.uasset)
    into the same folder as your HCAReplace.exe executable from https://github.com/TheSoraHD/HCAreplace .  Now open a command prompt in this folder and run something like:
      .\HCAreplace.exe generic_roster.uasset generic_roster\00099.hca modded_voice_file.wav  
    where generic_roster.uasset should be replaced with the uasset you want to hack, the generic_roster\00099.hca should be replaced with the HCA file from the original uasset that you want to replace, and modded_voice_file.wav is your modded audio file.  This will replace audio tracks one at a time, but it is command line, so you can script it with a batch script or a Python script.  This will edit your uasset "in-place" so generic_roster.uasset will now have your new audio tracks.
    
Part 3: Packaging the uasset into an IoStore mod    
    
    5) If you are modding the same audio bank as in my example (e.g., generic_roster.uasset ), then you can skip this step and just use the UTOC/UCAS/PAK from my sample_voice_mod.zip in step (7).  Othewrise, we need to make a dummy mod with (a placeholder for) that uasset, which we will pass to menv's uecastoc tool to get the manifest.  So just import any random audio file into my UE template ( https://www.nexusmods.com/aewfightforever/mods/4 ), with the path and name of the audio bank you want to modify.  In my example with generic_roster.uasset, you would import some random audio into UE as Content/GameData/Assets/Audio/Voice/Generic_Roster/generic_roster.uasset . Now package it as an IoStore chunk as if you are making any other normal mod.  Don't forget to put the _P at the end of each UTOC/UCAS/PAK filename as you would with any other mod.
 
    6) Grab uecastoc from https://github.com/gitMenv/UEcastoc and build it or grab a release (if you build from source, you will need both a Go compiler as well as a C++ compiler).  The important thing is to have a "cpp" sub-directory which contains at least the following three things:
      a)  castoc_x64.dll  
      b)  main.exe
      c)  fix_manifest_and_pack.py      
      
    7) Put the dummy mod from step (5) into the "cpp" directory from step (6).  Open a command prompt at that cpp directory and run:
         .\main.exe unpackAll .\pakchunk110-WindowsNoEditor_P.utoc .\pakchunk110-WindowsNoEditor_P.ucas output/
         .\main.exe manifest .\pakchunk110-WindowsNoEditor_P.utoc .\pakchunk110-WindowsNoEditor_P.ucas test_manifest.json
       where instead of pakchunk110 in those two commands, you would use whichever chunk ID you used in step (5).   
       
    8) You should now see an output directory with your unpacked dummy uasset in the correct path.  Rename that output directory with your modname (e.g., rename it pakchunk110-WindowsNoEditor_P in my example if using chunk ID 110), and replace the dummy uasset from your unpacked dummy mod with the real modded uasset you created in step (4).  You should now move the dummy UTOC/UCAS/PAK out of this directory or delete it, since in the next step we will make the real one.
    
    
    9) Open my Python script fix_manifest_and_pack.py, which should be in the "cpp" directory from when you installed uecastoc in step (6).  Make sure the manifest_file points to your manifest (e.g., to test_manifest.json in this example), and make sure directory_to_pak points to the directory you created in step (8) (  pakchunk110-WindowsNoEditor_P in my example ).  Run the Python script, which should generate the IoStore formatted UTOC/UCAS/PAK containing your modded uasset.  They should be in the "packed" subdirectory under the "cpp" directory.  You can stick this in  AEWFightForever/Content/Paks/~mods and you need the usual other steps to enable mods for AEW in general (e.g., patching the exe, etc.)  
    
    
    
Music Modding Tutorial (or, in general, non-IoStore audio modding tutorial).   NOTE:  IF YOU ARE USING MY ue4_criware_audio_modder.py SCRIPT FROM THIS REPO, YOU ONLY NEED TO DO STEP 1.  THE SCRIPT AUTOMATES EVERYTHING ELSE.

The procedure here is similar to the one above, but with a few key differences.

Part I:  Extraction
 
 1) There is now both an ACB and an AWB, with all the actual music data in the AWB as opposed to the ACB.  We will be only editing the AWB, but we need to extract both to see what each track is.  For music, extracting the ACB follows a similar procedure  to that described for voice above:  Use Fmodel to extract the raw uasset for GameData/Assets/Audio/Music/music.uasset as well as the corresponding music.awb from GameData/Resources/CriWareData/music.awb . For AEW FF, select UE4.27 and set the AES key to 0x766D2004BD1CA41B20A273CBEB8368FF267A819C30324F75B98C3EEAEB62BB1D . Make a note of the root directory (e.g., for AEWFF, this would be the parent directory of AEWFightForever\Content\GameData\... ).  Set the original_game_asset_root in your top_config.json to this root directory.

 2) As described for voice above, extract the ACB file from the uasset by opening the uasset in a hex editor, looking for the FIRST instance of the string @UTF and copying from @UTF (including @UTF) to the end of the file.  Paste it into a new hex file, and save the new hex file with a .acb extension (e.g., as generic_roster.acb in my example).  Unlike for voice, you will not be able to play this ACB in foobar since it has no audio data in it.  If you copy the acb and the awb from step (1) into the same directory, you should be able to open the awb in foobar, and you should see the track names in foobar, which it automatically grabbed from the acb.
 
 3) This step is exactly as described for voice above, except that now you need to move BOTH the acb AND the awb from steps (1) and (2) into the directory with your ACBEditor.exe from https://github.com/blueskythlikesclouds/SonicAudioTools .  Just like you did for voice modding above, drag the ACB file (only) over to the ACBEditor.exe to extract all the HCA tracks.

 
Part 2:  Injection into the AWB
 
  4) Grab https://github.com/TheSoraHD/HCAreplace and move:
      (a)  the folder with the extracted HCA files from step (3)
      (b)  the VGAudioCli.exe from https://github.com/Thealexbarney/VGAudio/releases/tag/v2.2.1
      (c)  the AWB from step (2) (e.g., music.awb)
    into the same folder as your HCAReplace.exe executable from https://github.com/TheSoraHD/HCAreplace .  Now open a command prompt in this folder and run something like:
      .\HCAreplace.exe music.awb music\00154_streaming.hca modded_music.wav
    where music\00154_streaming.hca should be replaced with the HCA file from the original uasset that you want to replace, and modded_music.wav is your modded music file (which should probably be 16-bit signed PCM, 48000 kHz,  stereo).  This will replace audio tracks one at a time, but it is command line, so you can script it with a batch script or a Python script.  This will edit your AWB "in-place" so music.awb will now have your new audio tracks.  This will probably take a long time for each track, since this file is over 1 GB (it has all music for the entire game).
    
    
Part 3: Packaging the uasset into a non-IoStore mod    

Unlike voice, music (as well as announcers) were packaged directly into a pak instead of into a UTOC/UCAS/PAK IoStore package, so the packing procedure here is different than for voice, and is the same as for non-IoStore UE games (like SC6, FF7R, etc.):

    5) Create a directory z_your_mod_name_P (where your_mod_name should be replaced with the name of your mod).  Within that directory, you should make the folder structure:
         z_your_mod_name_P/AEWFightForever/Content/GameData/Resources/CriWareData
      so that you can stick your modded AWB from step (4) into:
           z_your_mod_name_P/AEWFightForever/Content/GameData/Resources/CriWareData/music.awb

    6)  Download unrealpak.rar from https://www.fluffyquack.com/tools/fluffyquack's  and extract it into the directory with your top-level z_your_mod_name_P folder.  Now just drag the z_your_mod_name_P folder onto the UnrealPak-With-Compression.bat batch script you just extracted, and this should (slowly, because the bank is over 1 GB) create a pak file z_your_mod_name_P.pak. You can stick this in  AEWFightForever/Content/Paks/~mods and you need the usual other steps to enable mods for AEW in general (e.g., patching the exe, etc.)  
    
 
Happy audio modding!
 