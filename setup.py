from setuptools import setup

with open('README.md', 'r') as fin:
    long_description = fin.read()

setup(
     name='icepap-ipassign',
     version='2.3.0',
     author='Cyril Danilevski',
     author_email='cyril.danilevski@esrf.fr',
     description='A tool to configure IcePAP network settings',
     long_description=long_description,
     long_description_content_type="text/markdown",
     url='https://github.com/cydanil/icepap-ipassign',
     packages=['ipassign', 'ipa_gui', 'ipa_utils'],
     install_requires=['PyQt5>=5.12.0', 'netifaces>=0.10.9'],
     tests_require=['pytest'],
     python_requires='>=3.7',
     entry_points={
          "console_scripts": [
              'ipassign = ipa_gui.main:main',
              'ipassign-listener = ipa_utils.listener:main',
          ],
     },
     classifiers=[
         'Development Status :: 6 - Mature',
         'Environment :: X11 Applications :: Qt',
         'Intended Audience :: Developers',
         'Intended Audience :: Science/Research',
         'License :: OSI Approved :: BSD License',
         'Operating System :: POSIX :: Linux',
         'Operating System :: Microsoft :: Windows',
         'Topic :: Scientific/Engineering',
        ],
)
