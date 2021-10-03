import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile


def get_sha256(fname):
    hash_method = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_method.update(chunk)
    return hash_method.hexdigest()


FFMPEG_URL = {
    'zip': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
    'hash': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip.sha256'
}


INSTALL_DIR = 'C:\\'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--install-dir', help=f'The path to install FFMPEG to (default is {INSTALL_DIR})', type=str)
    args = parser.parse_args()

    if args.install_dir:
        INSTALL_DIR = args.install_dir

    INSTALL_DIR = os.path.join(INSTALL_DIR, 'FFMPEG')

    print(f'Making install dir {INSTALL_DIR!r}')

    try:
        os.mkdir(INSTALL_DIR)
    except FileExistsError as e:
        if os.listdir(INSTALL_DIR):
            raise FileExistsError('install directory exists and is not empty') from e

    download_dest = os.path.join(INSTALL_DIR, os.path.basename(FFMPEG_URL['zip']))
    expected_hash = urllib.request.urlopen(FFMPEG_URL['hash']).read().decode()

    print(f'Downloading {FFMPEG_URL["zip"]!r} to {download_dest!r}')
    data = urllib.request.urlopen(FFMPEG_URL['zip'])
    total_size = data.length
    total_size_mb = f'{total_size / 10 ** 6:.2f}'
    last_print = time.time()
    try:
        with open(download_dest, 'wb') as f:
            while (chunk := data.read(4096)):
                f.write(chunk)
                if time.time() - last_print >= 5:
                    last_print = time.time()
                    print(f'{(total_size - data.length) / 10 ** 6:.2f}MB / {total_size_mb}MB')
    except KeyboardInterrupt:
        print(f'KeyboardInterrupt - Removing {download_dest}')
        os.remove(download_dest)
        sys.exit(1)

    if expected_hash != get_sha256(download_dest):
        print('File downloaded but hashes do not match')
        sys.exit(1)
    print('File downloaded and hashes match')

    unzip_dest = download_dest.rstrip('.zip')
    print(f'Unzipping {download_dest!r} to {unzip_dest!r}')
    with zipfile.ZipFile(download_dest) as f:
        f.extractall(unzip_dest)

    for root, _, files in os.walk(unzip_dest):
        for file in files:
            if file == 'ffmpeg.exe':
                base_path = os.path.abspath(os.path.join(root, '..'))
                print(f'Move {base_path!r} to {INSTALL_DIR!r}')

                to_remove = os.listdir(INSTALL_DIR)
                for item in os.listdir(base_path):
                    shutil.move(os.path.join(base_path, item), INSTALL_DIR)

                for item in to_remove:
                    item = os.path.join(INSTALL_DIR, item)
                    if os.path.isdir(item):
                        shutil.rmtree(item)
                    else:
                        os.remove(item)
                break

    print(f'FFMPEG installed to {INSTALL_DIR!r}')

    path_dir = os.path.abspath(os.path.join(INSTALL_DIR, 'bin'))
    os_path = os.environ['path']
    if not os_path.endswith(';'):
        os_path += ';'
    command = f'[Environment]::SetEnvironmentVariable("Path","{os_path}{path_dir}","User")'
    print('\n\n')
    print(command)
    print()
    if input('Would you like to run the above command in PowerShell to add FFMPEG to your PATH? (Y/n) ') == 'Y':
        try:
            subprocess.check_output(['powershell', command])
        except subprocess.CalledProcessError as e:
            print(e.stdout.decode())
    else:
        print('User input was not "Y". Command not run')
