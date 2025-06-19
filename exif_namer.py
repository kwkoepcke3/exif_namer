#!/usr/bin/env python
from PIL import Image, ExifTags
import os
import shutil
import argparse

DATE_TIME_TAKEN_K = 36867

# remember to lowercase the extension
VALID_EXTS = [".3gp", ".jpg", ".jpeg", ".png", ".gif"]

def exif_rename(input_file, output_dir=None, test=False):
    img = Image.open(input_file)
    exif_data = img._getexif()
    if DATE_TIME_TAKEN_K not in exif_data:
        print(f"ERROR! {input_file} DOES NOT HAVE EXIF DATA! IGNORING")
        return
    name_raw = exif_data[DATE_TIME_TAKEN_K]

    ext = os.path.splitext(input_file)[1]
    date, time = name_raw.split()
    year, month, day = date.split(":")
    hour, minute, second = time.split(":")

    input_name_ext = os.path.basename(input_file)
    input_name = os.path.splitext(input_name_ext)[0]
    new_name_suffix = f"{year}-{month}-{day}_{hour}-{minute}-{second}{ext}"

    new_name = f"{input_name}_{new_name_suffix}"

    if output_dir:
        if os.path.exists(f"{output_dir}/{new_name}"):
            print(f"ERROR! {output_dir}/{new_name} ALREADY EXISTS! WILL NOT REPLACE!")
            return
        if test:
            print(f"COPY FROM {input_file} TO {output_dir}/{new_name}")
            return

        print(f"{output_dir}/{new_name}")
        shutil.copy2(input_file, f"{output_dir}/{new_name}")
    else:
        if os.path.exists(f"{os.path.dirname(input_file)}/{new_name}"):
            print(f"ERROR! {output_dir}/{new_name} ALREADY EXISTS! WILL NOT REPLACE!")
        if test:
            print(f"COPY FROM {input_file} TO {os.path.dirname(input_file)}/{new_name}")
            return

        print(f"{os.path.dirname(input_file)}/{new_name}")
        shutil.copy2(input_file, f"{os.path.dirname(input_file)}/{new_name}")
    

def main():
    parser = argparse.ArgumentParser(prog="ExifNamer", description="Copies file to destination with date taken as name")
    parser.add_argument("input_file")
    parser.add_argument('-o', "--output-dir", default=None)
    parser.add_argument('--directory', action='store_true')
    parser.add_argument('--test', action='store_true')

    args = parser.parse_args()
    

    if args.directory:
        # args.input_file will be a directory if --directory is specified
        for file in os.listdir(args.input_file):
            ext = os.path.splitext(file)[1].lower()
            if ext not in VALID_EXTS:
                print(f"ERROR! {args.input_file}/{file} DOES NOT HAVE A VALID EXTENSION ({ext})")
                continue
            
            exif_rename(f"{args.input_file}/{file}", args.output_dir, args.test)
    else:
        exif_rename(args.input_file, args.output_dir, args.test)
                
    
if __name__ == "__main__":
    main()

