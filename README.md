# FFMPEG Installer

A script to download FFMPEG and install FFMPEG to a Windows machine.
FFMPEG builds are downloaded from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).


## How it works

#### Step 1

Make a folder called "FFMPEG" in the installation directory.
If that folder already exists and contains files then an error will be thrown.

By default the install directory will be in "C:/", which then becomes "C:/FFMPEG".
To change the install directory, pass the `--install directory [YOUR DIRECTORY]` flag
and FFMPEG will be installed to `[YOUR DIRECTORY]/FFMEPG`.

#### Step 2

Download an FFMPEG build to the installation directory and check that the file's hash is correct

#### Step 3

Decompress the downloaded build

#### Step 4

Figure out where in the directory the actual ffmpeg executable is located and move it to the top level of the install directory.
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
[Environment]::SetEnvironmentVariable("Path", "[CURRENT OS PATH];[INSTALL_DIR]", "User")
```
The script will prompt you before running this command