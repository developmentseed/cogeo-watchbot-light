"""translator."""

from typing import Dict, Any, Union

from io import BytesIO
from urllib.parse import urlparse

import requests

from boto3.session import Session as boto3_session

import rasterio
from rasterio.io import MemoryFile
from rio_cogeo.cogeo import cog_translate, cog_validate
from rio_cogeo.profiles import cog_profiles

session = boto3_session()
client = session.client("s3")


def _download_obj(bucket: str, key: str) -> BytesIO:
    buff = BytesIO()
    client.download_fileobj(bucket, key, buff)
    buff.seek(0)
    return buff


def _upload_obj(obj: BytesIO, bucket: str, key: str) -> bool:
    client.upload_fileobj(obj, bucket, key)
    return True


def _get(url: str) -> BytesIO:
    url_info = urlparse(url.strip())
    if url_info.scheme.startswith("http"):
        body = BytesIO(requests.get(url).content)
    elif url_info.scheme == "s3":
        in_bucket = url_info.netloc
        in_key = url_info.path.strip("/")
        body = _download_obj(in_bucket, in_key)    
    return body


def process(
    url: str,
    out_bucket: str,
    out_key: str,
    profile: str = "webp",
    profile_options: Dict = {},
    allow_remote_read: bool = False,
    copy_valid_cog: bool = False,
    config: Dict[str, Any] = {},
    **options: Any,
) -> bool:
    """Download, convert and upload."""
    url_info = urlparse(url.strip())
    if url_info.scheme not in ["http", "https", "s3"]:
        raise Exception(f"Unsuported scheme {url_info.scheme}")

    if copy_valid_cog and cog_validate(url):
        _upload_obj(_get(url), out_bucket, out_key)
        return True

    src_path: Union[str, BytesIO] = url if allow_remote_read else _get(url)

    config.update(
        {
            "GDAL_NUM_THREADS": "ALL_CPUS",
            "GDAL_TIFF_INTERNAL_MASK": "TRUE",
            "GDAL_TIFF_OVR_BLOCKSIZE": "128",
        }
    )

    output_profile = cog_profiles.get(profile)
    output_profile.update(dict(BIGTIFF="IF_SAFER"))
    output_profile.update(profile_options)

    with rasterio.open(src_path) as src:
        with MemoryFile() as mem_dst:
            cog_translate(
                src,
                mem_dst.name,
                output_profile,
                config=config,
                in_memory=True,
                quiet=True,
                allow_intermediate_compression=True,  # Limit Disk usage
                **options,
            )
            _upload_obj(mem_dst, out_bucket, out_key)

    del mem_dst, src_path, src

    return True
