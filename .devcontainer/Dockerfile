ARG VARIANT "3.11-bookworm"

FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

ARG PANDOC_VERSION "3.1.8"
ARG PANDOC_RELEASE "-1"
ARG DRAWIO_VERSION "22.0.1"
ARG WITH_TEXLIVE "true"
ARG TARGETARCH

RUN apt-get update && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y install --no-install-recommends \
    libasound2 \
    libgbm1 \
    wget \
    xvfb

RUN if [ "$WITH_TEXLIVE" = "true" ]; then \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y install --no-install-recommends \
    fonts-font-awesome \
    latexmk \
    lmodern \
    texlive \
    texlive-fonts-extra \
    texlive-lang-french \
    texlive-lang-german \
    texlive-latex-extra \
    texlive-xetex \
    ; fi

# install pandoc
RUN cd /tmp && wget https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}${PANDOC_RELEASE}-${TARGETARCH}.deb
RUN apt install -y /tmp/pandoc-${PANDOC_VERSION}${PANDOC_RELEASE}-${TARGETARCH}.deb
RUN pip install pandoc-latex-environment

# install draw.io
RUN cd /tmp && wget https://github.com/jgraph/drawio-desktop/releases/download/v${DRAWIO_VERSION}/drawio-${TARGETARCH}-${DRAWIO_VERSION}.deb
RUN apt install -y /tmp/drawio-${TARGETARCH}-${DRAWIO_VERSION}.deb

RUN curl -sSL https://install.python-poetry.org | python3 -

# Install fonts
COPY fonts/* /usr/local/share/fonts/
RUN fc-cache -f -v

# Clean up
RUN rm -Rf /tmp/drawio*
RUN rm -Rf /tmp/pandoc*
RUN rm -rf /var/lib/apt/lists