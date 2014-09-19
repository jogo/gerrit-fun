import logging

import matplotlib.pyplot as plt

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


def plot_revisions(revisions):
    y = sorted(revisions)
    x = range(len(revisions))

    plt.plot(x, y)
    plt.title("Q: How many revisions  does it take to "
              "merge a patch in nova?")
    plt.ylabel("number of revisions")
    plt.show()


def main():
    change_ids = library.get_change_ids("/home/jogo/Develop/openstack/nova")
    revisions = get_revisions(change_ids[:800], "openstack/nova")
    library.stats(revisions)
    plot_revisions(revisions)

if __name__ == '__main__':
    main()
