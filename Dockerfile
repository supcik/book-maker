FROM python:3.11-bookworm

ARG book_maker_version=0.1.0
ARG pandoc_version=3.1.8
ARG pandoc_release=${pandoc_version}-1
ARG drawio_version=21.8.2
ARG with_texlive
ARG TARGETARCH

RUN apt-get update && apt-get install -y \
    libasound2 \
    wget \
    xvfb

RUN if [[ "${with_texlive}" == "true" ]]; then \
    apt-get install -y \
    texlive \
    texlive-lang-french \
    texlive-lang-german \
    texlive-latex-extra \
    texlive-xetex \
    ; fi

# Install book_maker
COPY dist/book_maker-${book_maker_version}.tar.gz /tmp/
RUN pip install /tmp/book_maker-${book_maker_version}.tar.gz

# install pandoc
RUN cd /tmp && wget https://github.com/jgm/pandoc/releases/download/${pandoc_version}/pandoc-${pandoc_release}-${TARGETARCH}.deb
RUN apt install -y /tmp/pandoc-${pandoc_release}-${TARGETARCH}.deb

# install draw.io
RUN cd /tmp && wget https://github.com/jgraph/drawio-desktop/releases/download/v${drawio_version}/drawio-${TARGETARCH}-${drawio_version}.deb
RUN apt install -y /tmp/drawio-${TARGETARCH}-${drawio_version}.deb

# Install fonts

# Clean up
RUN rm -Rf /tmp/drawio*
RUN rm -Rf /tmp/pandoc*
RUN rm -rf /var/lib/apt/lists
