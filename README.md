# ExifRenamer

## Install
install requirements.txt

## Usage
exif_renamer.py file_with_exif.ext \[--output-dir output_dir\]

copies file_with_exif.ext to the same directory as the input (unless --output-dir is specified)
with a new name, the new name being suffixed with the exif date taken data

if the --output-dir is specified, copy to that directory

suffix: {year}-{month}-{day}_{hour}-{minute}-{second}{ext}

```sh
usage: ExifNamer [-h] [-o OUTPUT_DIR] [--directory] [--test] input_file
```

example: 
```sh
./exif_renamer.py $HOME/unnamed.jpg
/home/mayo/unnamed_2010-11-24_18-28-47.jpg
```
if --directory is given then the input is a directory, and all files in the directory/* will be copied

+ No copy will be made if the extension is not a known image extension
+ No copy will be made if the output file already exists
+ No copy will be made if no exif data is found
