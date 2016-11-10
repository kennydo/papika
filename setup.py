from setuptools import (
    find_packages,
    setup,
)


setup(
    name='papika',
    version='0.0.2',
    description="Emit and receive Slack messages over Kafka",
    url='https://github.com/kennydo/papika',
    author='Kenny Do',
    author_email='chinesedewey@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
    ],
    packages=find_packages(exclude=['tests']),
    package_data={
    },
    include_package_Data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'papika-to-slack = papika.cli:to_slack',
            'papika-from-slack = papika.cli:from_slack',
        ],
    },
)
