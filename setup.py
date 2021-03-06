import setuptools

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="experimenttools",
    version="0.0.1",
    author="Ruben Purdy",
    author_email="rpurdy@andrew.cmu.edu",
    description="Tracking, plotting, and saving metrics for experiments.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=["Programming Language :: Python :: 3"],
    python_requires=">=3.7",
    install_requires=["holoviews[recommended]"],
)
