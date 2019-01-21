from Cython.Build import cythonize
from setuptools import setup
from distutils.extension import Extension


extensions = [
    Extension("replay_parser.body", ["replay_parser/body.py"]),
    Extension("replay_parser.replay", ["replay_parser/replay.py"]),
    Extension("replay_parser.commands", ["replay_parser/commands.py"]),
    Extension("replay_parser.header", ["replay_parser/header.py"]),
    Extension("replay_parser.reader", ["replay_parser/reader.py"]),
    Extension("replay_parser.config", ["replay_parser/config.py"]),
    Extension("replay_parser.constants", ["replay_parser/constants.py"]),
    Extension("replay_parser.replay", ["replay_parser/replay.py"]),
    Extension("replay_parser.units", ["replay_parser/units.py"]),
]

setup(
    name='replay_parser',
    version='1.1',
    description='Supreme Commander Forged alliance replay parser',
    author='Kalinovsky Konstantin',
    author_email='norraxx@gmail.com',
    packages=["replay_parser"],
    ext_modules=cythonize(extensions),
)
