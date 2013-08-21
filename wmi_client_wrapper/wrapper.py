"""
Houses the wrapper for wmi-client.

There are a handful of injection vulnerabilities in this, so don't expose it
directly to end-users.
"""

import csv
import sh
from StringIO import StringIO

class WmiClientWrapper(object):
    """
    Wrap wmi-client. Creating an instance of the wrapper will make a security
    context through which all future queries will be executed. It's basically
    just a convenient way to remember the username, password and host.

    There are a handful of injection vulnerabilities in this, so don't expose
    it directly to end-users.
    """

    def __init__(self, username="Administrator", password=None, host=None, delimiter="\01"):
        assert username
        assert password
        assert host # assume host is up

        # store the credentials for later
        self.username = username
        self.password = password
        self.host = host

        self.delimiter = delimiter

    def _make_credential_args(self):
        """
        Makes credentials that get passed to wmic. This assembles a list of
        arguments.
        """
        arguments = []

        # the format is user%pass
        # NOTE: this is an injection vulnerability
        userpass = "--user={username}%{password}".format(
            username=self.username,
            password=self.password,
        )

        arguments.append(userpass)

        # the format for ip addresses and host names is //
        hostaddr = "//{host}".format(host=self.host)

        arguments.append(hostaddr)

        return arguments

    def _setup_params(self):
        """
        Makes extra configuration that gets passed to wmic.
        """
        return ["--delimiter={delimiter}".format(delimiter=self.delimiter)]

    def _construct_query(self, klass):
        """
        Makes up a WMI query based on a given class.
        """
        # NOTE: this is an injection vulnerability
        queryx = "SELECT * FROM {klass}".format(klass=klass)
        return queryx

    def query(self, klass):
        """
        Executes a query using the wmi-client command.
        """
        # i don't want to have to repeat the -U stuff
        credentials = self._make_credential_args()

        # Let's make the query construction independent, but also if there's a
        # space then it's probably just a regular query.
        if " " not in klass:
            queryx = self._construct_query(klass)
        else:
            queryx = klass

        # and these are just configuration
        setup = self._setup_params()

        # construct the arguments to wmic
        arguments = setup + credentials + [queryx]

        # execute the command
        output = sh.wmic(*arguments)

        # just to be sure? sh is weird sometimes.
        output = str(output)

        # and now parse the output
        return WmiClientWrapper._parse_wmic_output(output, delimiter=self.delimiter)

    @classmethod
    def _parse_wmic_output(cls, output, delimiter="\01"):
        """
        Parses output from the wmic command and returns json.
        """
        # remove newlines and whitespace from the beginning and end
        output = output.strip()

        # just skip the first line
        output = "\n".join(output.split("\n")[1:])

        # well.. it's not quite a file
        strio = StringIO(output)

        # read the csv data
        items = list(csv.DictReader(strio, delimiter=delimiter))

        # walk the dictionaries!
        return WmiClientWrapper._fix_dictionary_output(items)

    @classmethod
    def _fix_dictionary_output(cls, incoming):
        """
        The dictionary doesn't exactly match the traditional python-wmi output.
        For example, there's "True" instead of True. Integer values are also
        quoted. Values that should be "None" are "(null)".

        This can be fixed by walking the tree.

        The Windows API is able to return the types, but here we're just
        guessing randomly. But guessing should work in most cases. There are
        some instances where a value might happen to be an integer but has
        other situations where it's a string. In general, the rule of thumb
        should be to cast to whatever you actually need, instead of hoping that
        the output will always be an integer or will always be a string..
        """

        if isinstance(incoming, list):
            output = []

            for each in incoming:
                output.append(cls._fix_dictionary_output(each))

        elif isinstance(incoming, dict):
            output = dict()

            for (key, value) in incoming.items():
                if value == "(null)":
                    output[key] = None
                elif value == "True":
                    output[key] = True
                elif value == "False":
                    output[key] = False
                elif isinstance(value, str) and len(value) > 1 and value[0] == "(" and value[-1] == ")":
                    # convert to a list with a single entry
                    output[key] = [value[1:-1]]
                elif isinstance(value, str):
                    output[key] = value
                elif isinstance(value, dict):
                    output[key] = cls._fix_dictionary_output(value)

        return output
