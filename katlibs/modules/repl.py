import cmd
from pprint import pprint


# noinspection PyPep8Naming,PyMethodMayBeStatic,PyUnusedLocal
class Katloop(cmd.Cmd):
    def __init__(self, connection):
        cmd.Cmd.__init__(self)
        self.connection = connection

    def do_list_cviews(self, line):
        pprint(self.connection.content_views)

    def do_list_versions(self, version_name):
        pass

    def do_EOF(self, line):
        return True


def main(**kwargs):
    loop = Katloop(kwargs['connection'])
    loop.cmdloop()
