from setuptools import setup, find_packages

setup(
    name="hermes-translate",
    version="0.01",
    description="全屏划词即时翻译工具 — DeepL 驱动",
    author="Hermes Agent",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pynput>=1.7",
        "pyperclip>=1.8",
        "rumps>=0.4",
        "pyobjc-core>=11.0",
        "pyobjc-framework-Cocoa>=11.0",
        "pyobjc-framework-Quartz>=11.0",
        "requests>=2.28",
    ],
    entry_points={
        "console_scripts": [
            "hermes-translate=hermes_translate.app:main",
        ],
    },
    classifiers=[
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)
