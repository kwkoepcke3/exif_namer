# ExifRenamer

## Install
install requirements.txt

## Usage
exif_namer.py file_with_exif.ext \[--output-dir output_dir\]

copies file_with_exif.ext to the same directory as the input (unless --output-dir is specified)
with a new name, the new name being suffixed with the exif date taken data

if the --output-dir is specified, copy to that directory

suffix: {year}-{month}-{day}_{hour}-{minute}-{second}{ext}

```sh
usage: exif_namer [-h] [-o OUTPUT_DIR] [-d] [-t] [-e] [-v] [-r] input

Copies image file with date taken as name suffix

positional arguments:
  input                 The input file or directory to copy image file(s) from

options:
  -h, --help            show this help message and exit
  -o, --output-dir OUTPUT_DIR
                        If set, output copies to this directory
  -d, --directory       If set, the input is a directory
  -t, --dry-run         If set, do not copy, only show log. Automatically sets verbose flag
  -e, --error-quit      If set, quit on error. By default in directory mode will not quit if encountering an error, and will continue to
                        the next file if possible
  -v, --verbose         If set, print out verbose logs during program execution
  -r, --report          If set, print out report at end of program

Copies image file with date taken as name suffix Does not copy if image file has unknown extension! (['.3gp', '.jpg', '.jpeg', '.png',
'.gif', '.mp4', '.mov', '.avi']) Does not copy if image file destination already exists! Does not copy if image file does not have
appropriate exif data! Does not copy if in dry_run mode!
```

example: 
```sh
 ./exif_namer test_input --directory --dry-run --report                                          05:50:20
ERROR! test_input/unnamed_5.random.extension DOES NOT HAVE A VALID EXTENSION (.extension)
SKIPPING!
COPY FROM test_input/unnamed_4.jpg TO test_input/2010112418_unnamed_4.jpg
COPY FROM test_input/unnamed.jpg TO test_input/2010112418_unnamed.jpg
COPY FROM test_input/unnamed_3.jpg TO test_input/2010112418_unnamed_3.jpg
COPY FROM test_input/unnamed_2.jpg TO test_input/2010112418_unnamed_2.jpg
copied 4/5
======= REPORT =======
Success,  Copy From,                                            Copy To,                                                        Exif Data                     
False,    test_input/unnamed_5.random.extension,                None,                                                           None                          
True,     test_input/unnamed_4.jpg,                             test_input/2010112418_unnamed_4.jpg,                            2010-11-24 18:28:47           
True,     test_input/unnamed.jpg,                               test_input/2010112418_unnamed.jpg,                              2010-11-24 18:28:47           
True,     test_input/unnamed_3.jpg,                             test_input/2010112418_unnamed_3.jpg,                            2010-11-24 18:28:47           
True,     test_input/unnamed_2.jpg,                             test_input/2010112418_unnamed_2.jpg,                            2010-11-24 18:28:47      
```