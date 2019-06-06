#!/usr/bin/env python3
"""Script to pull request from GitHub and prepare them for rebase process."""

import os
import re
import sys
import argparse
from urllib.request import urlopen

import simplejson
import git


class Progress(git.RemoteProgress):
    """Shows state on command line"""
    def __init__(self, desc):
        super(Progress, self).__init__()
        self.desc = desc

    def update(self, _, cur_count, max_count=None, message=''):
        print("\r{}: {}/{} {}".format(self.desc, cur_count, max_count, message), end="", flush=True)


def setup_token(oauth_file):
    """Load oauth token from oauth_file"""
    oauth = ""
    try:
        oauth = open(oauth_file).readline().strip()
    except Exception:
        pass
    return oauth


def list_requests(user, repo, oauth):
    """Prints open pull requests with some additional info"""
    url = "https://api.github.com/repos/%s/%s/pulls" % (user, repo)
    if oauth:
        url += "?access_token=%s" % oauth
    pull_requests = simplejson.load(urlopen(url))
    for request in pull_requests:
        print ('{0:4} ({1:>12}) {2}'.format(request.get('number'), request.get('assignee').get('login') if request.get('assignee') else '', request.get('title')))


def get_pull_request(req_num, user, repo, oauth):
    """Get data about one request"""
    url = "https://api.github.com/repos/%s/%s/pulls/%d" % (user, repo, req_num)
    if oauth:
        url += "?access_token=%s" % oauth
    result = simplejson.load(urlopen(url))
    return result


def guess_USER_REPO(repo_obj):
    """Uses convention that upstream remote is named either
    'upstream' or 'origin'"""
    a = dict((r.name, re.match(r'.*[:/](.*)/(.*)\.git', r.url).groups())
             for r in repo_obj.remotes)
    return a.get('upstream') or a.get('origin')


def prepare_repo(user, repo, repo_obj, req_num, master, ignore_dirty, oauth):
    """Main functionality"""
    if not ignore_dirty:
        if repo_obj.is_dirty() or repo_obj.untracked_files:
            print("Repo is dirty (uncommited changes/untracked files).")
            sys.exit(1)

    pull_request = get_pull_request(req_num, user, repo, oauth)

    message = pull_request.get("message")
    if message:
        print(message)
        sys.exit(2)

    remote_url = pull_request.get("head").get("repo").get("clone_url")
    from_who = pull_request.get("user").get("login")
    remote_branch = pull_request.get("head").get("ref")
    local_branch = pull_request.get("base").get("ref")

    print("{} {}".format(remote_url, remote_branch))

    remote_name = "pull-request-%s-%s" % (from_who, remote_branch)

    remote = repo_obj.create_remote(remote_name, remote_url)
    try:
        remote.fetch(progress=Progress("fetch"))
    except AssertionError:  # :-(  Some git assertion fails here
        pass
    repo_obj.git.checkout('%s/%s' % (remote_name, remote_branch), b=remote_name)
    repo_obj.delete_remote(remote)
    try:
        repo_obj.git.rebase(local_branch)
    except git.exc.GitCommandError:
        print("Rebase failed. You can either resolve it and run "
              "`git rebase --continue` or ask author to do the rebase.")

    if master:
        repo_obj.git.checkout("master")
        repo_obj.git.merge(remote_name, "--ff-only")
        repo_obj.git.branch("-d", remote_name)

    print("\nIn branch '{}'.".format("master" if master else remote_name))


def cmd():
    parser = argparse.ArgumentParser(("Fetch pull requests from GitHub and prepare them for rebase process.\n"
                                      "With no arguments it just lists actual pull requests."),
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--pr-number", "-n", help=("Pull request number. Fetches the pull request #n, creates separate "
                                                   "branch for it, rebases it on top of requested branch (usually "
                                                   "master) and deletes remote."), type=int)
    parser.add_argument("--master", "-m", help="Merge to master.", action='store_true')
    parser.add_argument("--ignore-dirty", "-i", help="Fetch PR without checking local repository.", action='store_true')
    args = parser.parse_args()

    repo_obj = git.Repo(search_parent_directories=True)
    user, repo = guess_USER_REPO(repo_obj)

    oauth_file = os.environ['HOME'] + "/.github-fetch-pullrequest-token" #os.path.join(os.environ['HOME'], ".github-fetch-pullrequest-token")
    oauth = setup_token(oauth_file)

    if not args.pr_number:
        list_requests(user, repo, oauth)
    else:
        prepare_repo(user, repo, repo_obj, args.pr_number, args.master, args.ignore_dirty, oauth)


if __name__ == "__main__":
    cmd()
