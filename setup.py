from setuptools import setup

requirements = ['cfn-lint', 'boto3']

setup(
    name='sonde',
    use_scm_version=True,
    author="Karl Gutwin",
    author_email="karl@bioteam.net",
    description="CloudFormation test framework",
    packages=[
        'sonde'
    ],
    entry_points={
        'console_scripts': ['sonde=sonde.cli:main']
    },
    python_requires='>=3.6',
    setup_requires=['setuptools_scm'],
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3'
    ]
)
