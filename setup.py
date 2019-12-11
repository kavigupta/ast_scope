import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ast_scope", # Replace with your own username
    version="0.1.0",
    author="Kavi Gupta",
    description="Annotates a Python AST with the scope of symbols.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kavigupta/ast_scope",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=[
        'attrs==19.3.0'
    ]
)
