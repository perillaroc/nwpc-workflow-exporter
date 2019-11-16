# coding: utf-8
import time
import json
import logging

import click
import yaml
import redis
from dateutil.parser import parse

logging.basicConfig(level=logging.DEBUG)


@click.command("node-status")
@click.option("--config-file", help="config file path", required=True)
def node_status(config_file):
    logger = logging.getLogger("node-status")
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

    scrape_interval = config["global"]["scrape_interval"]
    interval = parse(scrape_interval)

    redis_channel = f"{owner}/{repo}/status/channel"
    p = redis_client.pubsub()
    p.subscribe(redis_channel)

    while True:
        message = p.get_message()
        if message:
            if message["type"] == "message":
                data = json.loads(message["data"])
                logger.info(data["collected_time"])
            else:
                logger.info("type is not message: {message}".format(message=message))
        time.sleep(interval.second)
