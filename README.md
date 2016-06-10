# HttpServer
HTTP server that serves static webpages. Meant as a learning exercise.

## Usage
* Clone the repository and `cd` to it
* Run `./server.py` with following optional arguments

| Options          | Details           |
|------------------|:------------------|
| `-p`, `--port`   | Specify the port where server will listen. Default to HTTP port 80.              |
| `-d`, `--dir`    | Directory in which requested resources will be looked for. Defaults to this repo.|
| `-h`, `--help`   | Show help and exit.                                                              |


## Features
* Supports `GET` and `HEAD` requests
