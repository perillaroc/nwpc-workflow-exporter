# coding: utf-8
import click
import yaml
import redis
import time
import json


@click.command("node-status")
@click.option("--config-file", help="config file path", required=True)
def node_status(config_file):
    with open(config_file) as f:
        config = yaml.safe_load(f)

    redis_config = config["global"]["redis"]

    redis_client = redis.Redis(
        host=redis_config["host"],
        port=redis_config["port"],
        password=redis_config["password"],
        db=redis_config["db"]
    )

    owner = config["global"]["owner"]
    repo = config["global"]["repo"]

    redis_channel = f"{owner}/{repo}/status/channel"
    p = redis_client.pubsub()
    p.subscribe(redis_channel)

    while True:
        message = p.get_message()
        if message and message["type"] == "message":
            data = json.loads(message["data"])
            print(data["collected_time"])
        time.sleep(1)
