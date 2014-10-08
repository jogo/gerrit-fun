import collections

import prettytable
import yaml

import library

"""Generate governance repo voting record."""


def print_voting_record(change_ids, repo):
    headers = ["Subject", "Link"]
    names = collections.defaultdict(dict)  # {name: {number:vote, },}
    total_votes = collections.defaultdict(int)  # {name: count}
    changes = dict()  # {number: subject, }

    for details in library.get_change_details(change_ids, repo):
        number = details['_number']
        changes[number] = details['subject']
        for user in details['labels']['Code-Review']['all']:
            if user['value'] in (1, -1) and user['name'] != "Jenkins":
                names[user['name']][number] = user['value']
                total_votes[user['name']] += 1

    # build table
    x = prettytable.PrettyTable(headers + sorted(names),
                                hrules=prettytable.ALL)
    # total votes
    row = ["total votes", "N/A"]
    for name in sorted(total_votes):
        row.append(total_votes[name])
    x.add_row(row)
    for number in changes:
        row = [changes[number],
               "https://review.openstack.org/#/c/%s/" % number]
        for name in sorted(names):
            if names[name].get(number) is not None:
                row.append(names[name][number])
            else:
                row.append(" ")
        x.add_row(row)

    print x.get_html_string(format=True)


def main():
    config = yaml.load(open('config.yaml', 'r'))
    repo = "openstack/governance"
    path = config['path'] + repo

    change_ids = library.get_change_ids(path, since="5.months")
    change_ids = change_ids[:config['limit']]
    print_voting_record(change_ids, repo)


if __name__ == '__main__':
    main()
