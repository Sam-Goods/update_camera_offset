import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="update_camera_offset-SamGoodwin", # Replace with your own username
    version="0.0.1",
    author="Sam Goodwin + Bob Dimmock",
    author_email="support@vicon.com",
    description="Snap alignment of prop object attached to a calibrated SDI camera in Shogun Live 1.6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sam-Goods/update_camera_offset.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9.1',
)