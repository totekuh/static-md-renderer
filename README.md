# Static Markdown Renderer

This repository contains the setup for `static-md-renderer`, a Dockerized environment for a Jekyll blog. It's designed to facilitate the development of static Markdown-based websites, offering a live-reloading feature for real-time content updates.

## Prerequisites

Before starting, make sure you have the following installed on your system:
- Docker
- Docker Compose

## Setup and Running

**Clone the Repository** (if applicable):
   
```bash
git clone https://github.com/totekuh/static-md-renderer
cd static-md-renderer
```
    
**Environment Configuration**:
    
Modify `docker.env` to suit your environment settings, such as specifying the local folder for pages and the port number.

    
**Building and Running the Container**:
    
Use the provided `run.sh` script to build and start your Jekyll site:

```bash
./run.sh
```
    
This script executes docker-compose with the necessary parameters to set up the environment.

**Accessing the Site**:
    
Once the container is running, access your Jekyll site at `http://localhost:[HOST_PORT]`, where `[HOST_PORT]` is the port number specified in `docker.env`.

## Adding Content:

Place your Markdown files in the specified directory as configured in `docker.env` (the default folder is `./pages/` in the current running directory).
