#!/usr/bin/env python
import argparse
import os
from PIL import Image, ExifTags
from pathlib import Path

DATE_TIME_TAKEN_K = 36867

def main():
    parser = argparse.ArgumentParser(prog="exif_fixer")
    parser.add_argument("directory", help="The directory of files to look through for fixing exif date taken data")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-t", "--dry-run", action="store_true", help="Do not make changes to the filesystem, only print logs")

    args = parser.parse_args()

    if args.dry_run:
        args.verbose = True

    handle_fix(args.directory, args.verbose, args.dry_run)

def replace_exif(replace_from: Path, replace_to: Path):
    image_from = Image.open(replace_from)
    image_to = Image.open(replace_to)

    exif_from = image_from._getexif()
    exif_to = image_to._getexif()
    
    if exif_to is None:
        exif_to = exif_from
        exif_to_actual = image_from.getexif()
    else:
        exif_to_actual = image_to.getexif()

    exif_to_actual[DATE_TIME_TAKEN_K] = exif_from[DATE_TIME_TAKEN_K]
    image_to.save(replace_to, exif=exif_to_actual)

def handle_fix(directory, verbose=False, dry_run=False):
    to_fix = []
    prev = None
    # for file in directory
    #   if exif doesnt exist and there is no prev, add to queue. Continue
    #   if exif doesnt exist and there is some prev, replace exif with prev
    #   if exif does exist at this point, and there are values in the queue, replace all queue values with exif
    dir = os.listdir(directory)
    dir.sort()

    first_valid_exif_path = None
    for file in dir:
        path = os.path.join(directory, file)
        if not os.path.isfile(path):
            continue
        try:   
            image = Image.open(path)
        except Exception:
            continue

        exif = image._getexif()
        image.close()

        if exif is None or DATE_TIME_TAKEN_K not in exif:
            continue
        
        first_valid_exif_path = path
    
    if first_valid_exif_path is None:
        print("ERROR! THERE ARE NO FILES WITH EXIF DATA IN THIS DIRECTORY!")
    
    prev = first_valid_exif_path
    for file in dir:
        path = os.path.join(directory, file)
        if not os.path.isfile(path):
            continue
        
        try:
            image = Image.open(path)
        except Exception:
            continue
        
        exif = image._getexif()
        image.close()

        if exif is None or DATE_TIME_TAKEN_K not in exif:
            if verbose:
                print(f"REPLACING EXIF FOR {path} WITH {prev}'s")
            if not dry_run:
                replace_exif(prev, path)
        
        prev = path



        


            

    


if __name__ == "__main__":
    main()