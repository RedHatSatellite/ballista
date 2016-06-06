import cmd
from katlibs.main.katello_helpers import get_components
from pprint import pprint


def add_to_subparsers(subparsers):
    parser_cleanout_view = subparsers.add_parser('repl', help='Start repl-shell')
    parser_cleanout_view.set_defaults(funcname='repl')


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class Katloop(cmd.Cmd):
    def __init__(self, connection):
        cmd.Cmd.__init__(self)
        self.connection = connection

    def emptyline(self):
        return

    def do_list_cviews_json(self, line):
        pprint(self.connection.content_views)

    def help_list_cviews_json(self):
        print "Print complete content views in json format"

    def do_list_cviews(self, line):
        print '\n'.join([c['name'] for c in self.connection.content_views])

    def help_list_cviews(self):
        print "Print content views"

    def do_list_versions(self, cview_name):
        for version in get_components(self.connection.content_views, ('name', cview_name))['versions']:
            print "Version_id:{:>25}".format(version['version'])
            print "Date published:{:>25}".format(version['published'])
            print "-" * 40

    def help_list_versions(self):
        print "List versions of specified view"

    def postloop(self):
        print

    def do_EOF(self, line):
        return False


def main(**kwargs):
    loop = Katloop(kwargs['connection'])
    loop.cmdloop()
