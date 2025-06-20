#!/usr/bin/env python
from PIL import Image, ExifTags, ImageFile
import os
import shutil
import argparse
from dataclasses import dataclass
import sys

DATE_TIME_TAKEN_K = 36867

# remember to lowercase the extension
VALID_EXTS = [".3gp", ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov", ".avi"]


@dataclass
class ExifDate:
    year: str
    month: str
    day: str


@dataclass
class ExifTime:
    hour: str
    minute: str
    second: str


@dataclass
class ExifData:
    date: ExifDate
    time: ExifTime


@dataclass
class Args:
    input: str
    output_dir: str
    directory: bool
    dry_run: bool
    error_quit: bool


def extract_exif_data(input_file: str, error_quit=False) -> ExifData | None:
    img = Image.open(input_file)
    exif_data = img._getexif()
    if exif_data is None or DATE_TIME_TAKEN_K not in exif_data:
        return None
    name_raw = exif_data[DATE_TIME_TAKEN_K]

    date, time = name_raw.split()
    year, month, day = date.split(":")
    hour, minute, second = time.split(":")

    return ExifData(ExifDate(year, month, day), ExifTime(hour, minute, second))


def exif_rename(input_file, output_dir=None, dry_run=False, error_quit=False):
    ext = os.path.splitext(input_file)[1]
    if ext.lower() not in VALID_EXTS:
        print(f"ERROR! {input_file} DOES NOT HAVE A VALID EXTENSION ({ext})")

        exit_on_error(error_quit)
        return

    input_name_ext = os.path.basename(input_file)
    input_name = os.path.splitext(input_name_ext)[0]
    exif: ExifData = extract_exif_data(input_file, error_quit)
    if exif is None:
        print(f"ERROR! {input_file} DOES NOT HAVE EXIF DATA! IGNORING")
        exit_on_error(error_quit)
        return

    new_name_suffix = f"{exif.date.year}-{exif.date.month}-{exif.date.day}_{exif.time.hour}-{exif.time.minute}-{exif.time.second}{ext}"

    new_name = f"{input_name}_{new_name_suffix}"

    if output_dir:
        copy_from = input_file
        copy_to = f"{output_dir}/{new_name}"
    else:
        copy_from = input_file
        copy_to = f"{os.path.dirname(input_file)}/{new_name}"

    # if our suffix already exists, we may have copied this picture already.
    # We have to check if for <name>_suffix_suffix_..., <name>_suffix exists
    copy_to_dir = os.path.dirname(copy_to)
    # if our suffix is in any file name
    if any([new_name_suffix in fname for fname in os.listdir(copy_to_dir)]):
        # for a_random_name_date_time_date_time.ext, check if a_random_name_date_time.ext exists
        for fname in os.listdir(copy_to_dir):
            split = fname.split("_")

            # get up to the suffix, since the suffix is date_time.ext anything before must be the basename
            reconstructed = "_".join(split[: len(split) - 2])

            full_recon = f"{copy_to_dir}/{reconstructed}_{new_name_suffix}"
            if os.path.exists(full_recon):
                print(f"ERROR! {full_recon} ALREADY EXISTS! WILL NOT REPLACE!")

                exit_on_error(error_quit)
                return

    if os.path.exists(copy_to):
        print(f"ERROR! {copy_to} ALREADY EXISTS! WILL NOT REPLACE!")

        exit_on_error(error_quit)
        return

    print(f"COPY FROM {copy_from} TO {copy_to}")
    if not dry_run:
        shutil.copy2(copy_from, copy_to)


def exit_on_error(error_quit=False):
    if error_quit:
        print("EXIT ON ERROR SET! EXITING...")
        sys.exit(-1)
    else:
        print("SKIPPING!")


def main():
    parser = argparse.ArgumentParser(
        prog="exif_namer",
        description="Copies image file with date taken as name suffix",
        epilog=f"""
Copies image file with date taken as name suffix

Does not copy if image file has unknown extension! ({VALID_EXTS})
Does not copy if image file destination already exists!
Does not copy if image file does not have appropriate exif data!
Does not copy if in dry_run mode!
""",
    )
    parser.add_argument(
        "input", help="The input file or directory to copy image file(s) from"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=None,
        help="If set, output copies to this directory",
    )
    parser.add_argument(
        "-d",
        "--directory",
        action="store_true",
        help="If set, the input is a directory",
    )
    parser.add_argument(
        "-t",
        "--dry-run",
        action="store_true",
        help="If set, do not copy, only show log",
    )
    parser.add_argument(
        "-e",
        "--error-quit",
        action="store_true",
        help="If set, quit on error. By default in directory mode will not quit if encountering an error, and will continue to the next file if possible",
    )

    args: Args = parser.parse_args()

    if args.directory:
        if not os.path.isdir(args.input):
            print(
                f"ERROR! {args.input} IS NOT A VALID DIRECTORY! DO NOT KNOW WHERE TO COPY TO!"
            )
            exit_on_error()
            return

        # args.input will be a directory if --directory is specified
        for file in os.listdir(args.input):
            exif_rename(
                f"{args.input}/{file}", args.output_dir, args.dry_run, args.error_quit
            )
    else:
        if not os.path.isfile(args.input):
            print(f"ERROR! {args.input} IS NOT A VALID FILE! CANNOT COPY!")
            exit_on_error()
            return

        exif_rename(args.input, args.output_dir, args.dry_run, args.error_quit)


if __name__ == "__main__":
    main()
