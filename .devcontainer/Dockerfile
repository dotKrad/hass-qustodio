FROM python:3.9

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade colorlog black pylint
RUN python -m pip install --upgrade git+https://github.com/home-assistant/home-assistant@dev
RUN cd && mkdir -p /config/custom_components


WORKDIR /workspace

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash