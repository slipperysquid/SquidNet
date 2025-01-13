#!/bin/bash

Xvfb :0 -screen 0 1024x768x16 &

function install_buildtools {
    # Nuitka appreciates cl.exe so we could try to make sure MSVC 14.39.33519 or higher is installed.
    # However installing MSVC in wine appears non-trivial, and the mingw64 gcc.exe appears to work.
    # But here's how we would install MSVC if we could:
    #
    # Download it from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    # https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-community?view=vs-2022
    # TIP: The easiest way to find which packages are installed, is to run msvc_14.exe on a windows machine graphically,
    #      and after installing all the build tools, in the installer main menu, press "More" on Build Tools -> "Export configuration"
    #      and from there cherry-pick whatever you wish to install.
    echo -e "\033[0;32mInstalling MSVC 14\033[0m"
    wine cmd /c msvc_14.exe --quiet --add \
        Microsoft.Component.MSBuild \
        Microsoft.VisualStudio.Component.VC.Tools.x86.x64 \
        Microsoft.VisualStudio.Component.VC.Runtimes.x86.x64.Spectre \
        Microsoft.VisualStudio.Component.Windows11SDK.22621 & \
        while kill -0 $! 2> /dev/null; do sleep 1; done;
}

function install_python {
    mkdir -p /python/prefix/drive_c/users/$(whoami)/AppData/Local/Nuitka/Nuitka/Cache/downloads/depends/x86_64
    unzip /builddir/depends22_x86.zip -d /python/prefix/drive_c/users/$(whoami)/AppData/Local/Nuitka/Nuitka/Cache/downloads/depends/x86_64

    mkdir -p /python/prefix/drive_c/users/$(whoami)/AppData/Local/Nuitka/Nuitka/Cache/downloads/gcc/x86_64/13.2.0-16.0.6-11.0.1-msvcrt-r1/
    unzip /builddir/gcc.zip -d /python/prefix/drive_c/users/$(whoami)/AppData/Local/Nuitka/Nuitka/Cache/downloads/gcc/x86_64/13.2.0-16.0.6-11.0.1-msvcrt-r1/

    echo -e "\033[0;32mInstalling Python 3.12\033[0m"
    wine cmd /c python-3.12.exe /quiet InstallAllUsers=1 Include_exe=1 Include_lib=1 Include_pip=1 Include_tools=1 PrependPath=1CompileAll=0 AssociateFiles=0 Include_debug=0 Include_launcher=0 InstallLauncherAllUsers=0 Include_symbols=0 Include_tcltk=0 Include_test=0 & \
        while kill -0 $! 2> /dev/null; do sleep 1; done;
}

echo -e "\033[0;32mRunning wineboot\033[0m"
wineboot --init & while kill -0 $! 2> /dev/null; do sleep 1; done;

echo -e "\033[0;32mRunning winecfg\033[0m"
winecfg /v win11 & while kill -0 $! 2> /dev/null; do sleep 1; done;

echo -e "\033[0;32mRunning winetricks for win11\033[0m"
winetricks -q --force win11 & while kill -0 $! 2> /dev/null; do sleep 1; done;


# install_buildtools
install_python

echo -e "\033[38;5;250mChecking python version:\033[0m"
wine cmd /c python --version

echo -e "\033[38;5;250mChecking python version:\033[0m"
wine cmd /c pip install nuitka==2.4.4 --break-system-packages