#!/usr/bin/env python
from PIL import Image, ExifTags
import os
import shutil
import argparse

def main():
    parser = argparse.ArgumentParser(
        prog="ExifNamer",
        description="Copies file to destination with date taken as name",
    )
    parser.add_argument("input_file")
    parser.add_argument("-o", "--output-dir", default=None)

    args = parser.parse_args()

    img = Image.open(args.input_file)
    exif_data = img._getexif()

    for key, val in exif_data.items():
        if key in ExifTags.TAGS:
            print("Known Tag")
            print(f"{key}:{ExifTags.TAGS[key]}:{val}")
        else:
            print("Unknown Tag")
            print(f"{key}:{val}")


if __name__ == "__main__":
    main()
