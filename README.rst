Runstatus-cli
=============

Runstatus command-line client.

Installation
------------

::

    pip install runstatus-cli

Usage
-----

::

	Usage: runstatus [OPTIONS] COMMAND [ARGS]...

	Options:
	  -c, --config TEXT  Path to the configuration file.
	  -v, --verbose      Increase output verbosity.
	  --help             Show this message and exit.

	Commands:
	  create    Open a new incident.
	  info      Display the status information.
	  resolve   Resolve an open incident.
	  services  Manage services listed on the status page.
	  update    Update an open incident.
