from setuptools import setup, find_packages

setup(
    name="rpg-play-automation",
    version="0.1.0",
    description="Automated RPG campaign playthrough system",
    author="RPG Play Project",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "numpy>=1.24.0",
    ],
    python_requires=">=3.8",
)
