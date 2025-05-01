# caddy-helper

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

CLI tool to detect running Docker containers and automatically configure Caddy reverse proxy.

## Features

- Automatic container detection
- Interactive service selection
- Generates Caddyfile from template
- Connects containers to Caddy network
- Launches Caddy via Docker Compose

## Installation

```bash
git clone https://github.com/yourusername/caddy-helper.git
cd caddy-helper
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Configure your environment in `.env.example`, then:

```bash
cp .env.example .env
# update .env
python helper.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Docker Usage

You can also run the helper tool and Caddy together using Docker Compose:

```bash
# Build and start services
docker-compose -f docker-compose.helper.yml up --build -d

# Attach to helper CLI
docker attach caddy_helper
```

This mounts the Docker socket for container detection and uses the example environment file.  
