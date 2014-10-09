import datetime
import matplotlib.pyplot as plt

import yaml

import library


"""Q: How long to get a patch approved?

* Support checking subtrees, compare nova/virt vs rest
* Normalize for LOC?
* Measure from first patch until approved, not until merged
* Factor in what percent of the time we are waiting on author vs reviewer
"""

FORMAT = '%Y-%m-%d %H:%M:%S.%f000'


def get_duration(change_ids, repo):
    durations = []
    for details in library.get_latest_revision(change_ids, repo):
        created = datetime.datetime.strptime(details['created'], FORMAT)
        for workflow in details['labels']['Workflow']['all']:
            if workflow['value'] is 1:
                approved = datetime.datetime.strptime(workflow['date'], FORMAT)
        # rounds down to nearest day
        durations.append((approved - created).days)
    return durations


def plot_durations(revisions):
    y = sorted(revisions)
    x = range(len(revisions))

    plt.plot(x, y)
    plt.title("Q: Duration between first patch and approval")
    plt.ylabel("duration in days")
    plt.show()


def process_change_ids(change_ids, repo):
    duration = get_duration(change_ids, repo)
    # duration should be in days
    library.stats(duration)
    # plot_durations(duration)


def main():
    def process_subtree(subtree):
        change_ids = library.get_change_ids(path, subtree=subtree)
        change_ids = change_ids[:config['limit']]
        print "subtree: %s (%s patches):" % (subtree, len(change_ids))
        process_change_ids(change_ids, repo)

    config = yaml.load(open('config.yaml', 'r'))
    repo = config['repo']
    path = config['path'] + repo
    print "repo: %s" % repo

    process_subtree(None)
    process_subtree('nova/virt/')
    process_subtree('nova/virt/hyperv/')
    process_subtree('nova/virt/libvirt/')
    process_subtree('nova/virt/xenapi/')
    process_subtree('nova/virt/vmwareapi/')

if __name__ == '__main__':
    main()
