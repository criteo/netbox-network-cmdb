import codecs
import os.path

from setuptools import find_namespace_packages, setup


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name="netbox-cmdb",
    version=get_version("netbox_cmdb/version.py"),
    description="Netbox CMDB plugin",
    author="Criteo",
    install_requires=[],
    packages=find_namespace_packages(),
    package_data={
        "netbox_cmdb.templates.netbox_cmdb": ["*.html"],
        "netbox_cmdb.templates.netbox_cmdb.decommissioning": ["*.html"],
    },
    zip_safe=False,
)
