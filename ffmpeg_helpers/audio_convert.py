#!/usr/bin/env python3
# convert all files in a directory from .FLAC to .opus via ffmpeg
import multiprocessing
import subprocess
import sys
import os
from functools import partial
from typing import List

def convert_file(filename: str, inopts: List[str], outopts:List[str], force: bool) -> bool:
    """Take sound file in `filename` and convert it to opus if it doesn't
    already exist (or if --force was used)."""
    base, ext = os.path.splitext(filename)
    outfile = base + '.opus'
    if not force and os.path.exists(outfile):
        print(f'Skipping {outfile} since it exists...', file=sys.stderr)
        return True
    try:
        cmd = [ 'ffmpeg', '-v', 'quiet', '-i', filename, *inopts, 
               '-c:a', 'libopus', *outopts, outfile ]
        if force: cmd.insert(-1,'-y')
        print(f'Processing {filename}')
        subprocess.run(cmd, check=True) 
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg on {filename}: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Convert all audio files below the given directory to Ogg Vorbis')
    parser.add_argument('--bitrate', type=int,  help='Target rate (default 192000). (tip: use 0.59*stereo rate for mono)')
    parser.add_argument('--input', default='flac', help='Extension of the files we will convert (default flac)')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    parser.add_argument('--podcast', action='store_true', help='Set options for podcast (mono, 10kbps, voip-application)')
    parser.add_argument('directory', type=str, help='Root directory to search for files.')
    args = parser.parse_args()
    workload = []
    extension = '.' + args.input
    if args.directory:
        for root, dirs, files in os.walk(args.directory):
            workload.extend(os.path.join(root,file) for file in files if file.lower().endswith(extension))
        print(f'Going to process {len(workload)} files ending in {extension} under the directory {args.directory}')
        if args.podcast:
            inopts = ['-ac', '1']
            outopts = ['-application', 'voip', '-b:a', str(args.bitrate or 10000)]
        else:
            inopts = []
            outopts = ['-b:a', str(args.bitrate or 192000)]
        file_converter = partial(convert_file, inopts=inopts, outopts=outopts, force=bool(args.force))
        with multiprocessing.Pool() as pool:
            results = pool.map(file_converter, workload)
            if not all(results):
                print(f"There were {sum(1 for res in results if not res)} errors.", file=sys.stderr)
                sys.exit(1)

