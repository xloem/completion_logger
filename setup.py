from setuptools import setup
from setuptools.command.develop import develop as setuptools_develop
from setuptools.command.install import install as setuptools_install
import importlib

wrapped_packages = ['openai']

class cmd_develop(setuptools_develop):
    def run(self):
        super().run()
        wrap_packages()

class cmd_install(setuptools_install):
    def run(self):
        super().run()
        wrap_packages()

def wrap_packages():
    for pkg in wrapped_packages:
        fn = importlib.util.find_spec(pkg).origin
        with open(fn) as fh:
            pkg_text = fh.read()
        addition = f'\ntry:\n\timport completion_logger.wrapper.{pkg}\nexcept ImportError:\n\tpass\n'''
        if not addition in pkg_text:
            with open(fn, 'a') as fh:
                fh.write(addition)

setup(
    name='completion_logger',
    packages=[
        'completion_logger',
    ],
    install_requires=[
        'pyarweave @ git+https://github.com/xloem/pyarweave',
        'python-dateutil',
        'diskcache',
        *wrapped_packages,
    ],
    setup_requires=[
        *wrapped_packages,
    ],
    cmdclass={
        'develop': cmd_develop,
        'install': cmd_install,
    },
)
