"""Watchbot-light Worker."""

import os
import json

from . import translator


def process(message):
    """Map Step: Create COGs."""
    if isinstance(message, str):
        message = json.loads(message)

    print(message)

    src_path = message["src_path"]
    dst_prefix = message["dst_prefix"]

    bname = os.path.splitext(os.path.basename(src_path))[0]
    out_key = os.path.join(dst_prefix, f"{bname}_cog.tif")
    translator.process(
        src_path,
        os.environ["COG_BUCKET"],
        out_key,
        message["profile_name"],
        message["profile_options"],
        allow_remote_read=message.get("allow_remote_read", False),
        copy_valid_cog=message.get("copy_valid_cog", False),
        **message["options"],
    )

    return True


def _parse_message(message):
    if not message.get("Records"):
        return message
    record = message["Records"][0]
    body = json.loads(record["body"])
    return body["Message"]


def main(event, context):
    """
    Handle events.

    Events:
        - SQS queue (MAP)

    """
    message = _parse_message(event)
    return process(message)
