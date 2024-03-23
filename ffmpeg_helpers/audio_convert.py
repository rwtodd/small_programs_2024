#!/usr/bin/env python3
# convert all files in a directory from .FLAC to .OGG via ffmpeg
import multiprocessing
import subprocess
import sys
import os
from functools import partial

def libvorbis_quality(level: float) -> float:
    """Determine the target bitrate for a given libvorbis -q:a level in ffmpeg.
    The formula was given here: https://trac.ffmpeg.org/wiki/TheoraVorbisEncodingGuide"""
    # The formula 16×(q+4) is used below 4, 32×q is used below 8, and 64×(q-4) otherwise
    match level:
        case q if q < 4: return 16*(q+4)
        case q if q < 8: return 32*q
        case q: return 64*(q-4)

def convert_file(filename: str, quality: int, force: bool) -> bool:
    """Take sound file in `filename` and convert it to ogg vorbis if it doesn't
    already exist (or if --force was used)."""
    base, ext = os.path.splitext(filename)
    outfile = base + '.ogg'
    if not force and os.path.exists(outfile):
        print(f'Skipping {outfile} since it exists...', file=sys.stderr)
        return True
    try:
        cmd = [ 'ffmpeg', '-v', 'quiet', '-i', filename,
                '-c:a', 'libvorbis', '-q:a', str(quality), outfile ]
        if force: cmd.insert(-1,'-y')
        print(f'Processing f{filename}')
        subprocess.run(cmd, check=True) 
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg on {filename}: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Convert all audio files below the given directory to Ogg Vorbis')
    parser.add_argument('-q', '--quality', type=float, default=6.0,  help='Vorbis Q-level (default 6.0).')
    parser.add_argument('-i', '--input', default='flac', help='Extension of the files we will convert (default flac)')
    parser.add_argument('--levels', action='store_true', help='Display a table of Q-Levels and their target bit-rates')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    parser.add_argument('directory', nargs='?', help='Root directory to search for files.')
    args = parser.parse_args()
    if args.levels:
        print(f'~~ Vorbis Quality Levels ~~')
        for l in range(-1,11):
            print(f'{float(l): 5.1f} = {int(libvorbis_quality(l)):3d}kbps')
    workload = []
    extension = '.' + args.input
    if args.directory:
        for root, dirs, files in os.walk(args.directory):
            for file in files:
                if file.lower().endswith(extension):
                    workload.append(os.path.join(root,file))
        print(f'Going to process {len(workload)} files ending in {extension} under the directory {args.directory}')
        file_converter = partial(convert_file, quality=args.quality, force=args.force)
        with multiprocessing.Pool() as pool:
            results = pool.map(file_converter, workload)
            if not all(results):
                print(f"There were {sum(1 for res in results if not res)} errors.", file=sys.stderr)
                os.exit(1)
