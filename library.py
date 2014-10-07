import json
import logging
import os
import subprocess
import urllib

import grequests
import numpy

logging.basicConfig()
logger = logging.getLogger("recheck")
logger.setLevel(logging.DEBUG)


def get_change_ids(repo_path, subtree=None, since="6.months"):
    """Return array of change-Ids of merged patches.

    returns list starting with most recent change

    repo_path: file path of repo
    since: how far back to look
    """
    change_ids = []
    cwd = os.getcwd()
    os.chdir(repo_path)
    command = "git log --no-merges --since=%s master" % since
    if subtree:
        command = command + " " + subtree
    log = subprocess.check_output(command.split(' '))
    os.chdir(cwd)
    lines = log.splitlines()
    for line in lines:
        if line.startswith("    Change-Id: "):
            change_id = line.split()[1]
            if len(change_id) != 41 or change_id[0] != "I":
                raise Exception("Invalid Change-Id: %s" % change_id)
            change_ids.append(change_id)
    return change_ids


def query_gerrit(template, change_ids, repo_name):
    """query gerrit."""
    queries = []
    template = "https://review.openstack.org" + template
    for change_id in change_ids:
        # ChangeIDs can be used in multiple branches/repos
        patch_id = urllib.quote_plus("%s~master~" % repo_name) + change_id
        queries.append(template % patch_id)
    unsent = (grequests.get(query) for query in queries)
    for r in grequests.map(unsent, size=10):
        try:
            yield json.loads(r.text[4:])
        except AttributeError:
            # request must have failed, ignore it and move on
            logger.debug("failed to parse gerrit response")
            pass


def get_change_details(change_ids, repo_name):
    """get gerrit change details for a list of change_id.

    Returns a generator
    """
    return query_gerrit("/changes/%s/detail", change_ids, repo_name)


def get_latest_revision(change_ids, repo_name):
    """get latest revisions for a list of change_ids.

    Returns a generator
    """
    return query_gerrit("/changes/%s/revisions/current/review",
                        change_ids, repo_name)


def stats(values):
    print "Average: %s" % numpy.mean(values)
    print "median: %s" % numpy.median(values)
    print "variance: %s" % numpy.var(values)
