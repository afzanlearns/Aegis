from setuptools import setup, find_packages

setup(
    name="aegis-secrets",
    version="1.0.0",
    description="Aegis - Encrypted Secrets Manager",
    long_description="Military-grade encrypted secrets manager for developers. AES-256-GCM, Argon2, zero cloud.",
    author="Aegis Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "cryptography>=41.0.0",
        "pyperclip>=1.8.2",
    ],
    entry_points={
        "console_scripts": [
            "aegis=cli.main:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security :: Cryptography",
        "Topic :: Utilities",
    ],
)
