import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chatroom-name-history-weixin",
    version="1.0.0",
    author="JiangGua",
    author_email="pypi@mg.jonbgua.com",
    description="Log the Wechat chatroom name history",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JiangGua/chatroom-name-history-weixin",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)