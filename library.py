import json
import os
import subprocess
import urllib

import requests


def get_change_ids(repo_path, since="6.months"):
    """Return array of change-Ids of merged patches.

    returns list starting with most recent change

    repo_path: file path of repo
    since: how far back to look
    """
    change_ids = []
    cwd = os.getcwd()
    os.chdir(repo_path)
    command = ("git log --no-merges --since=%s master" % since)
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


def get_change_details(change_id, repo_name):
    """get gerrit change details for a given change_id."""
    # TODO(jogo) remove hard coded nova
    # ChangeIDs can be used in multiple branches/repos
    patch_id = urllib.quote_plus("%s~master~" % repo_name) + change_id
    query = "https://review.openstack.org/changes/%s/detail" % patch_id
    r = requests.get(query)
    change = json.loads(r.text[4:])
    return change
