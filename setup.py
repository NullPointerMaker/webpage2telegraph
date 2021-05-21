import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webpage2telegraph",
    version="0.0.5",
    author="NullPointerMaker",
    description="Transfer webpage to Telegraph archive.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NullPointerMaker/webpage2telegraph",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'html_telegraph_poster',
        'bs4',
        'readability-lxml',
        'telegram_util',
        'readee',
        'opencc-python-reimplemented',
        'cached_url',
        'weibo_2_album',
        'gphoto_2_album',
        'hanzidentifier',
        'pillow',
    ],
    python_requires='>=3.0',
)
