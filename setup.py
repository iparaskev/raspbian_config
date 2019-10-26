import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

DEPENDENCIES = ['PyInquirer']

setuptools.setup(
    name='raspi_config',  
    version='0.1',
    install_requires=DEPENDENCIES,
    scripts=['raspi_config'],

    # Metadata
    author="Iasonas Paraskevopoulos",
    author_email="iaswnparaskev@gmail.com",
    description="CLI tool for configuring a raspberry pi before first boot",
    url="",
)
