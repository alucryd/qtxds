from setuptools import setup

requirements = [
    'humanize',
    'PyQt5',
    'Quamash',
]

test_requirements = [
    'pytest',
    'pytest-cov',
    'pytest-faulthandler',
    'pytest-mock',
    'pytest-qt',
    'pytest-xvfb',
]

setup(
    name='qtxds',
    version='0.0.1',
    description="A PyQt5 GUI for ndstool and 3dstool",
    author="Maxime Gauduin",
    author_email='alucryd@gmail.com',
    url='https://github.com/alucryd/qtxds',
    packages=['qtxds', 'qtxds.images',
              'qtxds.tests'],
    package_data={'qtxds.images': ['*.png']},
    entry_points={
        'console_scripts': [
            'qtxds=qtxds.qtxds:main'
        ]
    },
    install_requires=requirements,
    zip_safe=False,
    keywords='qtxds',
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
