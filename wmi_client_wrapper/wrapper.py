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

    def __init__(self, username="Administrator", password=None, host=None, delimiter="|"):
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

        # let's make the query construction independent
        queryx = self._construct_query(klass)

        # and these are just configuration
        setup = self._setup_params()

        # construct the arguments to wmic
        arguments = setup + credentials + [queryx]

        # execute the command
        output = sh.wmic(*arguments)

        # just to be sure? sh is weird sometimes.
        output = str(output)

        # and now parse the output
        return WmiClientWrapper._parse_wmic_output(output, delimiter=delimiter)

    @classmethod
    def _parse_wmic_output(output, delimiter="|"):
        """
        Parses output from the wmic command and returns json.
        """
        # remove newlines and whitespace from the beginning and end
        output = output.strip()

        # just skip the first line
        output = "\n".join(output.split("\n")[1:])

        # well.. it's not quite a file
        strio = StringIO(output)

        # TODO: don't hardcode "|"
        return list(csv.DictReader(strio, delimiter=delimiter))
