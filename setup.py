from distutils.core import setup

setup(
     name='icepap-ipassign',
     version='0.0.0',
     author='Cyril Danilevski',
     author_email='cyril.danilevski@esrf.fr',
     description='',
     url='https://github.com/cydanil/icepap-ipassign',
     packages=['ipassign'],
     tests_require=['pytest'],
     python_requires='>=3.6',
     entry_points={
          "console_scripts": [
              'ipassign-listener = utils.listener:main',
              'ipassign = gui.launcher:ipassign',
          ],
     },
)
