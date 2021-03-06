import logging
import matplotlib.pyplot as plt

import yaml

import library


"""Q: How many rechecks does it take to merge a patch?

Plot over time.
Normalize for number of revisions

To distinguish between user error and valid rechecks, ignore rechecks where
there is at least one job failure in common on both sides of the recheck.
"""

logging.basicConfig()
logger = logging.getLogger("recheck")
logger.setLevel(logging.DEBUG)


def count_rechecks(change_details):
    """Count number of recheck comments in a change."""
    count = 0
    number_of_revisions = 0
    for i, message in enumerate(change_details['messages']):
        number_of_revisions = max(number_of_revisions,
                                  message['_revision_number'])
        if ("\nrecheck" in message['message'] or
                "\nreverify" in message['message']):
            if valid_recheck(change_details, i):
                count += 1
    return (float(count) / number_of_revisions)


def valid_recheck(change_details, recheck_position):
    """Return True if the failure before isn't seen after the recheck."""
    failure_list = []
    for i, message in enumerate(change_details['messages']):
        if ('author' in message and
                message['author'].get('username') == 'jenkins'):
            if i < recheck_position:
                # before the comment
                failure_list = get_failed_jobs(message['message'])
            else:
                new_list = get_failed_jobs(message['message'])
                failures = []
                for failure in failure_list:
                    if failure in new_list:
                        failures.append(failure)
                        # logger.debug(message['message'].split('\n')[4])
                        # Found failure after the recheck
                if len(failures) is not 0:
                    logger.debug("recheck didn't work, found %s before "
                                 "and after" % failures)
                    return False
                # Stop after first jenkins comment after recheck
                return True


def get_failed_jobs(message):
    """Return list of failed jenkins jobs."""
    failure_list = []
    for line in message.split("\n"):
        # Look for voting failures
        if "FAILURE" in line and "(non-voting)" not in line:
            failure_list.append(line.split(' ')[1])
    return failure_list


def get_rechecks(change_ids, repo):
    """Go through a list of Change-Ids and count the rechecks."""
    rechecks = []
    for i, details in enumerate(library.get_change_details(change_ids, repo)):
        rechecks.append(count_rechecks(details))
    return rechecks


def plot_rechecks(normalized_rechecks, repo):
    y = sorted(normalized_rechecks)
    x = range(len(normalized_rechecks))

    plt.plot(x, y)
    plt.title("Q: How many rechecks/reverifies does it take to "
              "merge a patch in %s?" % repo)
    plt.ylabel("(# of rechecks and reverifies)/(# of patch revisions)")
    plt.show()


def main():
    config = yaml.load(open('config.yaml', 'r'))
    repo = config['repo']
    path = config['path'] + repo

    change_ids = library.get_change_ids(path)
    rechecks = get_rechecks(change_ids[:config['limit']], repo)
    library.stats(rechecks)
    plot_rechecks(rechecks, repo)

if __name__ == '__main__':
    main()
