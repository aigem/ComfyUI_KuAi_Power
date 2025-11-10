from setuptools import setup, find_packages

setup(
    name="KuaiPower",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "pillow>=9.0.0",
        "numpy>=1.21.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
    ],
    entry_points={
        "comfyui.plugins": [
            "kuaipower = kuaipower",
        ]
    },
    python_requires=">=3.9",
    description="ComfyUI API Nodes about Kuai.host",
    author="Kuai.host",
)