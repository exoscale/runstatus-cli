from setuptools import find_packages, setup

with open('requirements.txt') as reqs:
    install_requires = [line for line in reqs.read().split('\n') if (
        line and not line.startswith('--'))
    ]


setup(
    name='runstatus-cli',
    version='0.3',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={'console_scripts': ['runstatus=rscli:main']},
)
