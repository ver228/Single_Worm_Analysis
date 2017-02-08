fname = '/Volumes/behavgenom_archive$/single_worm/MaskedVideos/Laura-phase1/phase 1 pc207-12/Laura/01-10-10/mec-12 (e1605) on food L_2010_10_01__12_25_25___6___3_subsample.mp4'
base_name = 'mec-12 (e1605) on food L_2010_10_01__12_25_25___6___3_subsample.mp4'
description="First upload test" 

cmd = '''python3 upload_video.py --file="{}" --title="{}" --description="{}" --keywords="{}" --category="{}" --privacyStatus="{}"'''

print(cmd.format(fname, base_name, description, "", "", "private"))