from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in personal_blaster/__init__.py
from personal_blaster import __version__ as version

setup(
	name="personal_blaster",
	version=version,
	description="Campaigning app for Whatsapp, Email and SMS",
	author="Novacept",
	author_email="info@novacept.io",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
