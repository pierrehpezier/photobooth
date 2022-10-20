from setuptools import setup

setup(
   name='photobooth',
   version='0.1',
   description='raspberry pi photobooth',
   author='Pierre-Henri Pezier',
   packages=['photobooth'],
   install_requires=['flask', 'pygame', 'gettext'],
   scripts=[
            'scripts/cool',
            'scripts/skype',
           ]
)