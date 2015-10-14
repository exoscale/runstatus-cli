from __future__ import unicode_literals

import os

import click


def parse_config(config, ctx):
    config = os.path.expanduser(config)
    if not os.path.exists(config):
        click.secho("No config file found at '", fg='red', nl=False)
        click.secho(config, bold=True, nl=False)
        click.secho("'.", fg='red')
        click.secho("Please create '", nl=False)
        click.secho(config, bold=True, nl=False)
        click.secho("' with the following format:")
        click.secho("""
    page = your-status-page-name
    key = api-key
    secret = secret-key
""", bold=True)
        ctx.abort()
    with open(config, 'r') as f:
        config = f.read()

    parsed = {}
    for line in config.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        parsed[key.strip()] = value.strip()
    missing = {'page', 'key', 'secret'} - set(parsed)
    if missing:
        click.secho("Missing configuration parameters: ", nl=False, fg='red')
        click.secho(", ".join(sorted(missing)), nl=False, bold=True)
        click.secho(".", fg='red')
        ctx.abort()
    return (
        parsed['page'],
        parsed['key'],
        parsed['secret'],
        parsed.get('endpoint', 'https://api.runstatus.com'),
    )
