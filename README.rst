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

Configuration
-------------

The runstatus command line client requires a configuration file

Default configuration file: runstatus will look for a configuration
file in ~/.runstatus

It is also possible to pass a specific configuration file with the
-c option: runstatus -c <configuration>.conf COMMAND

Parameters

::

        page = your-page-name
        key = api-key
        secret = secret-key

