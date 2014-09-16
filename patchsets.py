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

def count_rechecks(change_details):
    """Count number of recheck comments in a change."""
    count = 0
    number_of_revisions = 0
    for message in change_details['messages']:
        number_of_revisions = max(number_of_revisions,
                                  message['_revision_number'])
        if ("\nrecheck" in message['message'] or
                "\nreverify" in message['message']):
            count += 1
    print json.dumps(change_details, sort_keys=True, indent=2)
    return (float(count) / number_of_revisions)


def get_rechecks(change_ids, repo):
    rechecks = []
    mod = len(change_ids)/10
    for i, change_id in enumerate(change_ids):
        rechecks.append(count_rechecks(library.get_change_details(
            change_id, repo)))
        if i % mod == 0:
            logger.debug(i)
    return rechecks


def plot_rechecks(normalized_rechecks):
    y = normalized_rechecks
    x = range(len(normalized_rechecks))

    plt.plot(x, y)
    plt.title("Q: How many rechecks/reverifies does it take to "
              "merge a patch in nova?")
    plt.xlabel("X[0]=HEAD, X[1]=HEAD^")
    plt.ylabel("(# of rechecks and reverifies)/(# of patch revisions)")
    plt.show()


def main():
    change_ids = library.get_change_ids("/home/jogo/Develop/openstack/nova")
    rechecks = get_rechecks(change_ids[:400], "openstack/nova")
    print "Average: %s" % float(sum(rechecks)/len(rechecks))
    plot_rechecks(rechecks)

if __name__ == '__main__':
    main()
