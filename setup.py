import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ast_scope",  # Replace with your own username
    version="0.5.0",
    author="Kavi Gupta",
    author_email="ast_scope@kavigupta.org",
    description="Annotates a Python AST with the scope of symbols.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kavigupta/ast_scope",
    packages=setuptools.find_packages("ast_scope"),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=["attrs>=19.3.0", "typing-extensions>=4.13.2"],
)
