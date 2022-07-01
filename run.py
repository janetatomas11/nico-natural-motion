
import json
import docker
from docker.errors import NotFound, ContextAlreadyExists
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--config", "-c", default="configs/docker.json", help="Config file")
args = parser.parse_args()

docker_client = docker.from_env()


def main():
    with open(args.config) as config_file:
        config = json.load(config_file)

    image_config = config.get("image")
    dockerfile = image_config.get("dockerfile")
    image_tag = image_config.get("tags")

    container_config = config.get("container")
    detach = container_config.get("detach")
    command = container_config.get("command")
    container_name = container_config.get("name")

    volume_config = container_config.get("volume")
    volume_name = volume_config.get("name")
    volume_path = volume_config.get("path")

    train_config = container_config.get("train")
    train_method = train_config.get("method")
    train_args = train_config.get("args")
    train_kwargs = train_config.get("kwargs")

    process_config = container_config.get("process")
    process_method = process_config.get("method")
    process_args = process_config.get("args")
    process_kwargs = process_config.get("kwargs")

    try:
        docker_client.containers.get(container_name)
        raise ContextAlreadyExists(f"{container_name} (container)")
    except NotFound:
        pass

    print(f"Building image with tag: {image_tag}")
    docker_client.images.build(path=dockerfile, tag=image_tag)

    try:
        docker_client.volumes.get(volume_name)
    except NotFound:
        print(f"Creating volume: {volume_name}")
        docker_client.volumes.create(volume_name)

    environment = {
        "TRAIN_METHOD": train_method,
        "TRAIN_ARGS": train_args,
        "TRAIN_KWARGS": train_kwargs,
        "PROCESS_METHOD": process_method,
        "PROCESS_ARGS": process_args,
        "PROCESS_KWARGS": process_kwargs
    }

    print(f"Creating container: {container_name}")
    docker_client.containers.run(
        image=image_tag,
        detach=detach,
        command=command,
        volumes={
            volume_name: {"path": volume_path, "mode": "rw"}
        },
        environment=environment,
        name=container_name,
    )


if __name__ == "__main__":
    main()
