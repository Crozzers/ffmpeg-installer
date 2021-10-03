# FFMPEG Installer

A script to download and install FFMPEG to a Windows machine.
FFMPEG builds are downloaded from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).


## Usage

```
usage: install_ffmpeg.py [-h] [--install-dir INSTALL_DIR]

optional arguments:
  -h, --help            show this help message and exit
  --install-dir INSTALL_DIR
                        The path to install FFMPEG to (default is C:\)
```

## How it works

#### Step 1

A folder called "FFMPEG" is created in the installation directory.
If that folder already exists and contains files then an error will be thrown.

By default the install directory will be in "C:/", which then becomes "C:/FFMPEG".
To change the install directory, pass the `--install directory [YOUR DIRECTORY]` flag
and FFMPEG will be installed to `[YOUR DIRECTORY]/FFMEPG`.

#### Step 2

An FFMPEG build is downloaded to the installation directory and the file's sha256 hash is checked
against what it is supposed to be.
The downloaded build is then decompressed

#### Step 3

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

#### Step 4

Add FFMPEG to the PATH. This is done with the following command in powershell:
```
[Environment]::SetEnvironmentVariable("Path", "[CURRENT OS PATH];[INSTALL_DIR]", "User")
```
The script will prompt you before running this command.

If you do not want to run the command then you can add FFMPEG to your PATH another way.

1. Search for "environment variables" in the start menu and click "Edit environment variables for your account"
2. Scroll and find the "Path" variable in the "User variables" section and double click it
3. Click "Browse" and navigate to the install directory. Select it and click "Ok"
4. Click "Ok" and "Ok" again to exit