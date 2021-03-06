import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import zipfile
try:
    import pyunpack
    import patoolib  # noqa: F401
    AVAILABLE_7Z = True
except (ImportError, ModuleNotFoundError):
    AVAILABLE_7Z = False


def get_ffmpeg_url(build=None, format=None) -> str:
    '''
    Constructs an FFMPEG build download URL

    Args:
        build (str): the type of FFMPEG build you want
        format (str): whether you want a 7z or zip file
    '''
    if format == '7z' and not AVAILABLE_7Z:
        raise ValueError('7z format unavailable as pyunpack and patool are not present')

    for ffbuild in FFMPEG_BUILDS:
        if build is not None and ffbuild.split('.')[0] != build:
            continue

        if format is not None and ffbuild.split('.')[1] != format:
            continue

        return f'https://gyan.dev/ffmpeg/builds/ffmpeg-{ffbuild}'

    raise ValueError(f'{build} as format {format} does not exist')


class InstallDirs():
    '''
    Takes a URL and an installation directory and generates a number
    of suggested file paths.
    '''
    def __init__(self, url, install_dir):
        '''
        Args:
            url (str): the URL to the FFMPEG download
            install_dir (str): the directory to install FFMPEG to

        Instance Variables:
            install_dir (str): stores `install_dir` arg
            install_path (str): the actual path FFMPEG will be installed into
                (simply joins a "FFMPEG/" dir onto the `install_dir`)
            url (str): stores `url` arg
            hash_url (str): the URL of the file's expected sha256 hash
            download_dest (str): the file that the data will be downloaded into
            unzip_dest (str): the path that the downloaded file will be decompressed into
        '''
        self.install_dir = os.path.abspath(install_dir)
        self.install_path = os.path.join(install_dir, 'FFMPEG')
        self.url = url
        self.hash_url = url + '.sha256'
        self.download_dest = os.path.join(self.install_path, os.path.basename(self.url))
        self.unzip_dest = self.download_dest.rstrip(os.path.splitext(self.download_dest)[-1])


def get_sha256(fname) -> str:
    hash_method = hashlib.sha256()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_method.update(chunk)
    return hash_method.hexdigest()


def make_empty_path(path):
    '''
    Creates a filepath and makes sure that it is empty

    Raises:
        FileExistsError: if the filepath exists AND is not empty
    '''
    try:
        os.mkdir(path)
    except FileExistsError as e:
        if os.listdir(path):
            raise FileExistsError('install directory exists and is not empty') from e


class Downloader():
    def __init__(self, url, destination, hash_url=None):
        '''
        Args:
            url (str): the URL of the resource to download
            destination (str): the filepath to save the data to
            hash_url (str): the URL containing the file's expected hash
        '''
        self.url = url
        self.destination = destination
        if hash_url is not None:
            self.hash = urllib.request.urlopen(hash_url).read().decode()
        else:
            self.hash = None
        self.data = urllib.request.urlopen(self.url)
        self.size = self.data.length

    def download(self):
        '''
        Downloads the file

        Raises:
            ValueError: if the expected hash does not match the downloaded file's hash
        '''
        self.failed = False
        try:
            with open(self.destination, 'wb') as f:
                while (chunk := self.data.read(4096)):
                    f.write(chunk)

            if self.hash is None:
                return

            if self.hash != get_sha256(self.destination):
                self.failed = True
                raise ValueError('downloaded file does not match expected hash')
        except Exception:
            self.failed = True
            raise

    def progress(self) -> int:
        '''Returns number of downloaded bytes'''
        return self.size - self.data.length


def decompress(path, destination):
    '''Decompresses `path` into `destination`'''
    if path.endswith('.zip'):
        with zipfile.ZipFile(path) as f:
            f.extractall(destination)
    else:
        os.mkdir(destination)
        pyunpack.Archive(path).extractall(destination)


def move_ffmpeg_exe_to_top_level(top_level):
    '''
    Finds the `bin/ffmpeg.exe` file in a directory tree and moves it to
    the top-level of that tree.
    EG: `C:/FFMPEG/ffmpeg-release-essentials/bin/ffmpeg.exe` -> `C:/FFMPEG/bin/ffmpeg.exe`.

    Args:
        top_level (str): the tree to search
    '''
    for root, _, files in os.walk(top_level):
        for file in files:
            if file == 'ffmpeg.exe':
                base_path = os.path.abspath(os.path.join(root, '..'))
                to_remove = os.listdir(top_level)

                for item in os.listdir(base_path):
                    shutil.move(os.path.join(base_path, item), top_level)

                for item in to_remove:
                    item = os.path.join(top_level, item)
                    if os.path.isdir(item):
                        shutil.rmtree(item)
                    else:
                        os.remove(item)
                break


def add_path_to_environment(path):
    '''Adds a filepath to the users PATH variable after asking the user's consent'''
    os_path = os.environ['path']
    if not os_path.endswith(';'):
        os_path += ';'
    command = f'[Environment]::SetEnvironmentVariable("Path","{os_path}{path}","User")'
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


FFMPEG_BUILDS = [
    'release-full.7z',
    'release-full-shared.7z',
    'release-essentials.zip',
    'release-essentials.7z',
    'git-essentials.7z',
    'git-full.7z'
]

INSTALL_DIR = 'C:\\'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--install-dir', type=str, default=INSTALL_DIR,
        help=f'The path to install FFMPEG to (default is {INSTALL_DIR})'
    )
    parser.add_argument(
        '--build', type=str,
        help='The build of FFMPEG to install'
    )
    parser.add_argument(
        '--format', choices=('7z', 'zip'),
        help='Preferred file format'
    )
    args = parser.parse_args()

    dirs = InstallDirs(get_ffmpeg_url(args.build, args.format), args.install_dir)

    print(f'Making install dir {dirs.install_path!r}')
    make_empty_path(dirs.install_path)

    print(f'Downloading {dirs.url!r} to {dirs.download_dest!r}')
    downloader = Downloader(dirs.url, dirs.download_dest, dirs.hash_url)
    dl_thread = threading.Thread(target=downloader.download, daemon=True)
    dl_thread.start()
    time.sleep(1)
    while dl_thread.is_alive():
        time.sleep(5)
        print(f'Progress: {downloader.progress() / 10 ** 6:.2f}MB / {downloader.size / 10 ** 6:.2f}MB')
    time.sleep(1)
    if downloader.failed:
        sys.exit(1)

    print(f'Unzipping {dirs.download_dest!r} to {dirs.unzip_dest!r}')
    decompress(dirs.download_dest, dirs.unzip_dest)

    print(f'Move bin/ffmpeg.exe to top level of {dirs.install_path!r}')
    move_ffmpeg_exe_to_top_level(dirs.install_path)

    print(f'FFMPEG installed to {dirs.install_path!r}')

    add_path_to_environment(os.path.abspath(os.path.join(dirs.install_path, 'bin')))
