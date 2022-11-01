from typing import List
from setuptools import find_packages,setup
from  typing import List

def get_requirements()->List[str]:
    """
    This function returns a list of requirements
    """
    
    requirement_list:List[str] = []

    """
    Write a code to read requirements.txt file and append each reqirements in requirements_list variable
    """
    return requirement_list

setup(

    name = "sensor",
    version="0.0.1",
    author="yogesh",
    author_email="yogeshkonduru@gmail.com",
    packages = find_packages(),
    install_requires=get_requirements(),
)