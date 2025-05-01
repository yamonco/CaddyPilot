import docker
import subprocess
import os

DEFAULT_DOMAIN = os.getenv("DEFAULT_DOMAIN", "example.com")
DEFAULT_EMAIL = os.getenv("DEFAULT_EMAIL", "admin@example.com")
HTTP_PORT = os.getenv("HTTP_PORT", "80")
HTTPS_PORT = os.getenv("HTTPS_PORT", "443")

from jinja2 import Environment, FileSystemLoader

CADDYFILE_OUT = "Caddyfile.generated"
CADDY_DOCKER_NETWORK = "caddy_net"
CADDY_CONTAINER_NAME = "caddy_proxy"
CADDY_COMPOSE_FILE = "docker-compose.caddy.yml"
DOMAIN_SUFFIX = ".yamon.io"

def get_running_containers():
    client = docker.from_env()
    containers = []
    for container in client.containers.list():
        ports = container.attrs['NetworkSettings']['Ports']
        exposed = [p for p in ports if ports[p] and ports[p][0].get("HostPort")]
        if exposed:
            containers.append({
                "id": container.id,
                "name": container.name,
                "ports": exposed
            })
    return containers

def choose_services(containers):
    print("다음 컨테이너를 선택하여 Caddy에 연결합니다:")
    selected = []
    for idx, c in enumerate(containers, start=1):
        port_info = ", ".join([f"{p}->{c['ports'][p][0]['HostPort']}" for p in c['ports']])
        print(f"[{idx}] {c['name']} ({port_info})")
    choices = input("선택 (쉼표로 구분): ").strip().split(",")
    for i in choices:
        try:
            selected.append(containers[int(i.strip()) - 1])
        except (ValueError, IndexError):
            continue
    return selected

def generate_caddyfile(services):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("caddyfile.j2")
    context = {
        "services": [{
            "container_name": s["name"],
            "port": list(s["ports"].keys())[0].split("/")[0],
            "domain": s["name"] + DOMAIN_SUFFIX
        } for s in services]
    }
    output = template.render(context)
    with open(CADDYFILE_OUT, "w") as f:
        f.write(output)
    print(f"Caddyfile 생성 완료: {CADDYFILE_OUT}")

def ensure_network():
    result = subprocess.run(["docker", "network", "ls", "--filter", f"name={CADDY_DOCKER_NETWORK}", "--format", "{{.Name}}"],
                            capture_output=True, text=True)
    if CADDY_DOCKER_NETWORK not in result.stdout:
        subprocess.run(["docker", "network", "create", CADDY_DOCKER_NETWORK])
        print(f"도커 네트워크 생성: {CADDY_DOCKER_NETWORK}")

def run_caddy():
    print("Caddy 컨테이너 실행 중...")
    subprocess.run(["docker", "compose", "-f", CADDY_COMPOSE_FILE, "up", "-d"])
    print("Caddy 실행 완료.")

def main():
    containers = get_running_containers()
    if not containers:
        print("실행 중인 컨테이너가 없습니다.")
        return
    selected = choose_services(containers)
    if not selected:
        print("선택된 컨테이너가 없습니다.")
        return
    ensure_network()
    for s in selected:
        subprocess.run(["docker", "network", "connect", CADDY_DOCKER_NETWORK, s["name"]])
    generate_caddyfile(selected)
    run_caddy()

if __name__ == "__main__":
    main()
