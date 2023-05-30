try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='completion_logger',
    packages=[
        'completion_logger',
    ],
)
