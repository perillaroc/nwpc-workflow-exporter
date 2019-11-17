# coding: utf-8
import time
import json
from loguru import logger

import click
import yaml
import redis
from dateutil.parser import parse


@click.command("node-status")
@click.option("--config-file", help="config file path", required=True)
def node_status(config_file):
    with open(config_file) as f:
        config = yaml.safe_load(f)

    redis_config = config["global"]["redis"]

    redis_host = redis_config["host"]
    redis_port = redis_config["port"]
    redis_password = redis_config["password"]
    redis_db = redis_config["db"]
    logger.info(f"connecting to redis...{redis_host}:{redis_port}/{redis_db}")
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        db=redis_db
    )

    owner = config["global"]["owner"]
    repo = config["global"]["repo"]
    redis_channel = f"{owner}/{repo}/status/channel"

    scrape_interval = config["global"]["scrape_interval"]
    interval = parse(scrape_interval)

    nodes_config = config["nodes"]

    p = redis_client.pubsub()
    p.subscribe(redis_channel)

    while True:
        message = p.get_message()
        if message:
            if message["type"] != "message":
                logger.info("type is not message: {message}".format(message=message))
            else:
                data = json.loads(message["data"])
                logger.info(f"new status arrived: {data['collected_time']}")
                status_records: list = data["status_records"]
                for node_config in nodes_config:
                    node_path = node_config["path"]
                    node_record = next(x for x in status_records if x["path"] == node_path)
                    logger.info(f"{node_path}: {node_record['status']}")

        time.sleep(interval.second)
