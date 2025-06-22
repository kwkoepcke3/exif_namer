#!/usr/bin/env python
import argparse
import os
from PIL import Image, ExifTags

DATE_TIME_TAKEN_K = 36867

def main():
    parser = argparse.ArgumentParser(prog="exif_fixer")
    parser.add_argument("directory", help="The directory of files to look through for fixing exif date taken data")
    parser.add_argument("-v", "--verbose", action="store_true")

    args = parser.parse_args()

    handle_fix(args.directory, args.verbose)

def replace_exif(replace_from: Image, replace_to: Image, replace_to_path):
    exif_from = replace_from._getexif()
    exif_to = replace_to._getexif()
    
    if exif_to is None:
        exif_to = exif_from
        exif_to_actual = replace_from.getexif()
    else:
        exif_to_actual = replace_to.getexif()

    exif_to_actual[DATE_TIME_TAKEN_K] = exif_from[DATE_TIME_TAKEN_K]
    replace_to.save(replace_to_path, exif=exif_to_actual)

def handle_fix(directory, verbose=False):
    to_fix = []
    prev = None
    # for file in directory
    #   if exif doesnt exist and there is no prev, add to queue. Continue
    #   if exif doesnt exist and there is some prev, replace exif with prev
    #   if exif does exist at this point, and there are values in the queue, replace all queue values with exif
    dir = os.listdir(directory)
    dir.sort()
    for file in dir:
        path = os.path.join(directory, file)
        if not os.path.isfile(path):
            continue
        
        # try:
        image = Image.open(path)
        exif = image._getexif()
        if (exif is None or DATE_TIME_TAKEN_K not in exif) and prev is None:
            if verbose:
                print(f"ADDING {path} TO QUEUE")
            to_fix.append(path)
            continue
        elif exif is None or DATE_TIME_TAKEN_K not in exif:
            if verbose:
                print(f"REPLACING EXIF AT {path}")
            replace_exif(prev, image, path)
        
        if len(to_fix) > 0 and prev is None:
            for path_to_fix in to_fix:
                print(f"QUEUE REPLACING EXIF AT {path_to_fix}")
                replace = Image.open(path_to_fix)
                replace_exif(image, replace, path_to_fix)
        
        if exif is not None:
            prev = image

        


            

    


if __name__ == "__main__":
    main()