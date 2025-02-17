# archive-downloader
This tool is handy for downloading mp4 or other media from an archive site.

## Usage
$ git clone repo
$ cd archive-downloader

## Make a Virtual environment
$ python3 -m venv env
$ source env/bin/activate

## Install the dependancies
$ pip install -r requirements.txt

## Options
python adl.py
usage: adl.py [-h] -u URL -f FOLDER [-t THREADS]
adl.py: error: the following arguments are required: -u/--url, -f/--folder

## Example
$ python adl.py -u https://someurl.com/path/to/files -f localfolder_save_location -t 4
