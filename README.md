# FFMPEG Installer

A script to download and install FFMPEG to a Windows machine.
FFMPEG builds are either downloaded from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) or [GyanD/codexffmpeg](https://github.com/GyanD/codexffmpeg).

## Setup
```
pip install -r requirements.txt
```

## Usage

```
usage: install_ffmpeg.py [-h] [--install-dir INSTALL_DIR] [--build BUILD] [--format {7z,zip}] [--overwrite] [--downloader {default,windows,wget,curl}]

options:
  -h, --help            show this help message and exit
  --install-dir INSTALL_DIR
                        The path to install FFMPEG to (default is C:\)
  --build {release-full,release-full-shared,release-essentials,git-essentials,git-full}
                        The build of FFMPEG to install
  --format {7z,zip}     Preferred file format
  --overwrite           Overwrite existing install
  --downloader {default,windows,wget,curl}
                        Control how files are downloaded. "default" will use python libraries to download, "windows" will use Invoke-WebRequest, "wget" and "curl" will attempt to use their respective CLI utilities
```

## How it works

#### Step 1

An appropriate FFMPEG build is found. By default this will be the `release-full` build
in `7z` format but this can be changed using the `--build` and `--format` flags.

Available builds:
* release-full (7z and zip)
* release-full-shared (7z and zip)
* release-essentials (7z and zip)
* git-essentials (7z)
* git-full (7z)

To unpack `7z` archives you will need to install `patool`. You can do this with `pip install -r requirements.txt`

#### Step 2

A folder called "FFMPEG" is created in the installation directory.
If that folder already exists and contains files then an error will be thrown.

By default the install directory will be in "C:/", which then becomes "C:/FFMPEG".
To change the install directory, pass the `--install-dir [YOUR DIRECTORY]` flag
and FFMPEG will be installed to `[YOUR DIRECTORY]/FFMEPG`.

#### Step 3

An FFMPEG build is downloaded to the installation directory and the file's sha256 hash is checked
against what it is supposed to be.
The downloaded build is then decompressed

#### Step 4

The script then tries to figure out where in the directory the actual
FFMPEG executable is located and move it to the top level of the install directory.
```
Before:                                 | After:
                                        |
+ {INSTALL DIRECTORY}/                  | + {INSTALL DIRECTORY}/
|____ ffmpeg-release-essentials.zip     | |___+ bin/
|___+ ffmpeg-release-essentials/        | |   |____ ffmpeg.exe
    |___+ ffmpeg-4.4-essentials_build/  | |   |____ ffplay.exe
        |___+ bin/                      | |   |____ ffprobe.exe
        |   |____ ffmpeg.exe            | |___+ doc/
        |   |____ ffplay.exe            | |___+ presets/
        |   |____ ffprobe.exe           | |____ LICENSE
        |___+ doc/                      | |____ README.txt
        |___+ presets/                  |
        |____ LICENSE                   |
        |____ README.txt                |
```

#### Step 5

Add FFMPEG to the PATH. This is done with the following command in powershell:
```
[Environment]::SetEnvironmentVariable("Path", "<CURRENT OS PATH>;<INSTALL_DIR>", "User")
```
The script will prompt you before running this command.

If you do not want to run the command then you can add FFMPEG to your PATH another way.

1. Search for "environment variables" in the start menu and click "Edit environment variables for your account"
2. Scroll and find the "Path" variable in the "User variables" section and double click it
3. Click "Browse" and navigate to the install directory. Select it and click "Ok"
4. Click "Ok" and "Ok" again to exit
