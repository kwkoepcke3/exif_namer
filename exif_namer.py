#!/usr/bin/env python
from PIL import Image, ExifTags
import os
import shutil
import argparse

DATE_TIME_TAKEN_K = 36867

def main():
    parser = argparse.ArgumentParser(prog="ExifNamer", description="Copies file to destination with date taken as name")
    parser.add_argument("input_file")
    parser.add_argument('-o', "--output-dir", default=None)

    args = parser.parse_args()
    
    img = Image.open(args.input_file)
    exif_data = img._getexif()
    name_raw = exif_data[DATE_TIME_TAKEN_K]

    ext = os.path.splitext(args.input_file)[1]
    date, time = name_raw.split()
    year, month, day = date.split(":")
    hour, minute, second = time.split(":")

    input_name_ext = os.path.basename(args.input_file)
    input_name = os.path.splitext(input_name_ext)[0]
    new_name_suffix = f"{year}-{month}-{day}_{hour}-{minute}-{second}{ext}"

    new_name = f"{input_name}_{new_name_suffix}"
    if args.output_dir:
        print(f"{args.output_dir}/{new_name}")
        shutil.copy2(args.input_file, f"{args.output_dir}/{new_name}")
    else:
        print(f"{os.path.dirname(args.input_file)}/{new_name}")
        shutil.copy2(args.input_file, f"{os.path.dirname(args.input_file)}/{new_name}")
    
    
if __name__ == "__main__":
    main()

