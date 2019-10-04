"""Setup."""

from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

inst_reqs = [
    # "git+https://github.com/developmentseed/cogeo-mosaic",
    "rio-cogeo>=1.1.5",
    "rasterio[s3]>=1.0.28",
    "watchbot_progress",
    "wget"
]
extra_reqs = {"test": ["pytest", "pytest-cov"]}

setup(
    name="app",
    version="0.0.1",
    description=u"Lambda Watchbot",
    python_requires=">=3",
    keywords="AWS-Lambda Python",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)
