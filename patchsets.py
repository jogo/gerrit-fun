import logging
import matplotlib.pyplot as plt

import yaml

import library


"""Q: How many patchsets to merge?

Plot over time.
Factor in LOC?
"""

logging.basicConfig()
logger = logging.getLogger("patchsets")
logger.setLevel(logging.DEBUG)


def get_revisions(change_ids, repo):
    revisions = []
    for details in library.get_latest_revision(change_ids, repo):
        current_revision = details['current_revision']
        revision_number = details['revisions'][current_revision]['_number']
        revisions.append(revision_number)
    return revisions


def plot_revisions(revisions, repo):
    y = sorted(revisions)
    x = range(len(revisions))

    plt.plot(x, y)
    plt.title("Q: How many revisions  does it take to "
              "merge a patch in %s?" % repo)
    plt.ylabel("number of revisions")
    plt.show()


def main():
    config = yaml.load(open('config.yaml', 'r'))
    repo = config['repo']
    path = config['path'] + repo

    change_ids = library.get_change_ids(path)
    change_ids = change_ids[:config['limit']]
    revisions = get_revisions(change_ids, repo)
    library.stats(revisions)
    plot_revisions(revisions, repo)

if __name__ == '__main__':
    main()
