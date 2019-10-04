"""translator."""

import os
import uuid
from urllib.parse import urlparse

import wget

from boto3.session import Session as boto3_session

from rio_cogeo.cogeo import cog_translate, cog_validate
from rio_cogeo.profiles import cog_profiles

REGION_NAME = os.environ.get("AWS_REGION", "us-east-1")


def _s3_download(path, key):
    session = boto3_session(region_name=REGION_NAME)
    s3 = session.client("s3")
    url_info = urlparse(path.strip())
    s3_bucket = url_info.netloc
    s3_key = url_info.path.strip("/")
    s3.download_file(s3_bucket, s3_key, key)
    return True


def _upload(path, bucket, key):
    session = boto3_session(region_name=REGION_NAME)
    s3 = session.client("s3")
    with open(path, "rb") as data:
        s3.upload_fileobj(data, bucket, key)
    return True


def _translate(src_path, dst_path, profile="webp", profile_options={}, **options):
    """Convert image to COG."""
    output_profile = cog_profiles.get(profile)
    output_profile.update(dict(BIGTIFF="IF_SAFER"))
    output_profile.update(profile_options)

    config = dict(
        GDAL_NUM_THREADS="ALL_CPUS",
        GDAL_TIFF_INTERNAL_MASK=True,
        GDAL_TIFF_OVR_BLOCKSIZE="128",
    )

    cog_translate(
        src_path,
        dst_path,
        output_profile,
        config=config,
        in_memory=False,
        quiet=True,
        allow_intermediate_compression=True,
        **options,
    )
    return True


def process(
    url,
    out_bucket,
    out_key,
    profile="webp",
    profile_options={},
    copy_valid_cog=False,
    **options,
):
    """Download, convert and upload."""
    url_info = urlparse(url.strip())
    src_path = "/tmp/" + os.path.basename(url_info.path)

    if url_info.scheme not in ["http", "https", "s3"]:
        raise Exception(f"Unsuported scheme {url_info.scheme}")

    if url_info.scheme.startswith("http"):
        wget.download(url, src_path)
    elif url_info.scheme == "s3":
        _s3_download(url, src_path)

    uid = str(uuid.uuid4())
    dst_path = f"/tmp/{uid}.tif"

    if copy_valid_cog and cog_validate(src_path):
        dst_path = src_path
    else:
        _translate(
            src_path,
            dst_path,
            profile=profile,
            profile_options=profile_options,
            **options,
        )

    _upload(dst_path, out_bucket, out_key)

    return True
