import os

dirname = os.path.dirname(__file__)
resourse_directory = os.path.join(dirname, 'resource')


def getResourcePath(resource_name: str) -> str:
    return os.path.join(resourse_directory, resource_name)
