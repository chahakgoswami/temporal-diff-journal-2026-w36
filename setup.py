from setuptools import setup, find_packages

setup(
    name="tdj",
    version="0.1.0",
    description="Temporal Diff Journal – CLI journal with smart diffs.",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "tdj=tdj.cli:main",
        ],
    },
)
