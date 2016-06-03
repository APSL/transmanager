import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

install_requires = [
    'django',
    'django-filter',
    'django-hvad',
    'django-rq',
    'xlsxwriter',
    'xlrd',
    'djangorestframework',
    'django-yubin'
]


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='transmanager',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='A simple Django app to deal with the model content translation tasks',
    long_description=README,
    url='https://github.com/APSL/transmanager',
    author='Andreu Vallbona',
    author_email='avallbona@gmail.com',
    install_requires=install_requires,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
    ],
)