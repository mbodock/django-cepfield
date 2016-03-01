from setuptools import setup, find_packages

__version__ = '0.1.5'
__description__ = 'Django CepField'
__long_description__ = 'Auto fill address using brasizilian CEP number.'

__author__ = 'Marcus Bodock'
__author_email__ = 'mbodock@gmail.com'

requires = [i.strip() for i in open("requirements.txt").readlines()]

testing_extras = [
    'pytest',
    'pytest-cov',
]

setup(
    name='django-cepfield',
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    packages=find_packages(),
    license='MIT',
    description=__description__,
    long_description=__long_description__,
    url='https://github.com/mbodock/django-cepfield/',
    keywords='Django, CEP, Address, Brazil',
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'License :: OSI Approved :: MIT License',
    ],
    tests_require=['pytest'],
    extras_require={
        'testing': testing_extras,
    },
)
