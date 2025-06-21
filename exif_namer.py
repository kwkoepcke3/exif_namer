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
class LogEntry:
    success: bool
    copy_from: str
    copy_to: str
    exif_data: str

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
    verbose: bool
    report: bool

def verbose_print(to_print: str, verbose=False):
    if verbose:
        print(to_print)

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


def exif_rename(input_file, output_dir=None, dry_run=False, error_quit=False, verbose=False, log=[]):
    ext = os.path.splitext(input_file)[1]
    if ext.lower() not in VALID_EXTS:
        verbose_print(f"ERROR! {input_file} DOES NOT HAVE A VALID EXTENSION ({ext})", verbose)
        log.append(LogEntry(False, input_file, None, None))

        exit_on_error(error_quit, verbose)
        return

    input_name_ext = os.path.basename(input_file)
    input_name = os.path.splitext(input_name_ext)[0]
    exif: ExifData = extract_exif_data(input_file, error_quit)
    if exif is None:
        verbose_print(f"ERROR! {input_file} DOES NOT HAVE EXIF DATA!", verbose)
        log.append(LogEntry(False, input_file, None, None))

        exit_on_error(error_quit, verbose)
        return
    exif_str = f"{exif.date.year}-{exif.date.month}-{exif.date.day} {exif.time.hour}:{exif.time.minute}:{exif.time.second}"


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
            reconstructed_w_suffix = f"{reconstructed}_{new_name_suffix}"
            full_recon = f"{copy_to_dir}/{reconstructed_w_suffix}"
            if os.path.exists(full_recon) and reconstructed_w_suffix == new_name:
                verbose_print(f"ERROR! {full_recon} ALREADY EXISTS! WILL NOT REPLACE!", verbose)
                log.append(LogEntry(False, input_file, copy_to, exif_str))

                exit_on_error(error_quit, verbose)
                return

    if os.path.exists(copy_to):
        verbose_print(f"ERROR! {copy_to} ALREADY EXISTS! WILL NOT REPLACE!", verbose)
        log.append(LogEntry(False, input_file, copy_to, exif_str))

        exit_on_error(error_quit, verbose)
        return

    verbose_print(f"COPY FROM {copy_from} TO {copy_to}", verbose)
    log.append(LogEntry(True, input_file, copy_to, exif_str))
    if not dry_run:
        shutil.copy2(copy_from, copy_to)


def exit_on_error(error_quit=False, verbose=False):
    if error_quit:
        verbose_print("EXIT ON ERROR SET! EXITING...", verbose)
        sys.exit(-1)
    else:
        verbose_print("SKIPPING!", verbose)


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
        help="If set, do not copy, only show log. Automatically sets verbose flag",
    )
    parser.add_argument(
        "-e",
        "--error-quit",
        action="store_true",
        help="If set, quit on error. By default in directory mode will not quit if encountering an error, and will continue to the next file if possible",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="If set, print out verbose logs during program execution"
    )
    parser.add_argument(
        "-r",
        "--report",
        action="store_true",
        help="If set, print out report at end of program"
    )

    args: Args = parser.parse_args()
    if args.dry_run:
        args.verbose = True
    log = []

    if args.directory:
        if not os.path.isdir(args.input):
            verbose_print(
                f"ERROR! {args.input} IS NOT A VALID DIRECTORY! DO NOT KNOW WHERE TO COPY TO!",
                args.verbose
            )
            exit_on_error(args.error_quit, args.verbose)
            return

        # args.input will be a directory if --directory is specified
        for file in os.listdir(args.input):
            if not os.path.isfile(f"{args.input}/{file}"):
                # ignore all dirs
                continue

            exif_rename(
                f"{args.input}/{file}", args.output_dir, args.dry_run, args.error_quit, args.verbose, log
            )
    else:
        if not os.path.isfile(args.input):
            print(f"ERROR! {args.input} IS NOT A VALID FILE! CANNOT COPY!")
            exit_on_error(args.error_quit, args.verbose)
            return

        exif_rename(args.input, args.output_dir, args.dry_run, args.error_quit, args.verbose, log)

    n_total = len(log)
    n_moved = sum(map(lambda entry: 1 if entry.success else 0, log))

    print(f"copied {n_moved}/{n_total}")

    if args.report:
        print("======= REPORT =======")
        print(f"{'Success,':10s}{'Copy From,':50s}\t{'Copy To,':60s}\t{'Exif Data':30s}")
        for item in log:
            print(f"{str(item.success)+',':10s}{item.copy_from+',':50s}\t{str(item.copy_to)+',':60s}\t{str(item.exif_data):30s}")


if __name__ == "__main__":
    main()
