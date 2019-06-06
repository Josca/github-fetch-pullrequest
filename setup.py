from setuptools import setup, find_packages

setup(
    name='github-fetch-pullrequest',
    version='0.0.1',
    author='Josef Hák',
    author_email='jhak@redhat.com',
    description='Script to pull request from GitHub.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/Josca/github-fetch-pullrequest',
    license='GPLv2',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'simplejson==3.16.0',
        'gitpython==2.1.11'
    ],
    entry_points='''
        [console_scripts]
        github-fetch-pullrequest=github_fetch_pullrequest.cmd:cmd
    ''',
)
