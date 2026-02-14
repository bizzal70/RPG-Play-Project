from setuptools import setup, find_packages

setup(
    name="rpg-play-project",
    version="0.1.0",
    description="Fully automated RPG campaign test system",
    author="RPG Play Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ],
)
