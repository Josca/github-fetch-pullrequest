# github-fetch-pullrequest
Script to pull request from GitHub and prepare them for rebase process.

## Install
~~~bash
pip install github-fetch-pullrequest # from PyPI
pip install .                        # from sources
~~~

## Usage
~~~bash
github-fetch-pullrequest --help # show help
github-fetch-pullrequest        # available pull requests
github-fetch-pullrequest -n 42  # fetch pull request number 42
~~~

## Oauth
To use oauth create secret file `~/.github-fetch-pullrequest-token` including your
github access token. You can create and copy GitHub access token using your
GitHub web interface.
