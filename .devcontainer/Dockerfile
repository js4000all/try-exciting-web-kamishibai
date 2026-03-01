FROM node:22-slim

# Install necessary packages
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        python3-full \
        python3-pip \
        ca-certificates \
        git \
        git-completion \
        curl \
        jq \
        zip \
        unzip \
        iputils-ping \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY profile.d /etc/profile.d


USER node
WORKDIR /workspace
