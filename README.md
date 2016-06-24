# HttpServer
HTTP server that serves static webpages. Meant as a learning exercise.

## Usage
* Clone this repository and `cd` to it
* Run `./server.py` with the following optional arguments:

| Options          | Description                                                                      |
|------------------|:---------------------------------------------------------------------------------|
| `-p`, `--port`   | Specify the port where the server will listen. Defaults to HTTP port 80.         |
| `-d`, `--dir`    | Directory in which requested resources will be looked for. Defaults to this repo.|
| `-h`, `--help`   | Show help and exit.                                                              |

* Test it using any web browser - `http://127.0.0.1:[PORT]`
* Care should be taken if no port is specified. It is possible some other service might be using HTTP port 80 (eg. Apache)
* The server will correctly only on UNIX based operating systems.

## Features
* Supports `GET` and `HEAD` requests
* Implements look up for `index.html` / `index.htm` in a directory

