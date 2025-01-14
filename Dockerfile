FROM archlinux/archlinux:latest


# Install required packages
RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm \
    git curl base-devel openssl zlib xz tk sqlite bzip2 libffi && \
    pacman -Scc --noconfirm

# Enable multilib repository
RUN echo -e "\n[multilib]\nInclude = /etc/pacman.d/mirrorlist" >> /etc/pacman.conf

# Update package databases and upgrade the system
RUN pacman -Syu --noconfirm

RUN pacman --quiet -S --noconfirm python wine winetricks wine-mono wine-gecko wget \
    xorg-server-xvfb coreutils which lib32-gnutls libwbclient samba

RUN useradd -m -G wheel -s /bin/bash builderbob &&\
    echo '%wheel ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/wheel

# Set up directories and permissions
RUN mkdir -p /builddir /python /app/payload /app/output && \
    chown -R builderbob:builderbob /builddir /python /app

USER builderbob

WORKDIR /builddir

ENV DISPLAY=:0.0
ENV WINEPATH=/python
ENV WINEARCH=win64
ENV WINEPREFIX=/python/prefix
ENV WINEDEBUG=trace-all,warn-all,err+all,fixme-all

# Setup wine environment
RUN wget --quiet -O /builddir/python-3.12.exe https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
RUN wget -O /builddir/depends22_x86.zip https://www.dependencywalker.com/depends22_x86.zip
RUN wget -O /builddir/gcc.zip https://github.com/brechtsanders/winlibs_mingw/releases/download/13.2.0-16.0.6-11.0.1-msvcrt-r1/winlibs-x86_64-posix-seh-gcc-13.2.0-llvm-16.0.6-mingw-w64msvcrt-11.0.1-r1.zip

RUN --mount=type=bind,source=./install_python.sh,target=/builddir/install_python.sh \
    ./install_python.sh

WORKDIR /app

COPY . /app

USER root

RUN chown -R builderbob:builderbob /app /app/payload /app/output

USER builderbob

RUN pip install -r requirements.txt

EXPOSE 5000-5004

#CMD ["/bin/bash"] i am tehsing this stuff

CMD ["python3", "server.py"]