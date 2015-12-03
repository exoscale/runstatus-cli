import os

import click

from .conf import parse_config
from .page import Page


@click.group()
@click.option('-c', '--config', envvar='RUNSTATUS_CONFIG',
              default=os.path.join('~', '.runstatus'),
              help='Path to the configuration file.')
@click.option('-v', '--verbose', count=True, help='Increase output verbosity.')
@click.pass_context
def main(ctx, config, verbose):
    page, key, secret, endpoint = parse_config(config, ctx)

    ctx.obj = Page(page=page, api_key=key, secret_key=secret,
                   endpoint=endpoint, ctx=ctx)


@main.command()
@click.pass_obj
def info(page):
    """
    Display the status information.
    """
    page.print_summary()


@main.command()
@click.argument('action', type=click.Choice(['add', 'remove']))
@click.argument('name')
@click.pass_obj
def services(page, action, name):
    """
    Manage services listed on the status page.
    """
    act = getattr(page, '{0}_service'.format(action))
    act(name)


status_choices = ['investigating', 'identified', 'monitoring', 'resolved']
status_prompt = 'Status [{0}]'.format('|'.join(status_choices))
state_choices = ['operational', 'degraded_performance',
                 'partial_outage', 'major_outage']
state_prompt = 'State [{0}]'.format('|'.join(state_choices))


@main.command()
@click.argument('incident', type=click.INT)
@click.option('--status', prompt=status_prompt,
              type=click.Choice(status_choices))
@click.option('--state', prompt=state_prompt, type=click.Choice(state_choices))
@click.option('--text', prompt='Text', type=click.STRING)
@click.pass_obj
def update(page, incident, status, state, text):
    """
    Update an open incident.
    """
    page.add_event(incident, status, state, text)


@main.command()
@click.argument('incident', type=click.INT)
@click.option('--text', prompt='Text', type=click.STRING)
@click.pass_obj
def resolve(page, incident, text):
    """
    Resolve an open incident.
    """
    page.add_event(incident, 'resolved', 'operational', text)


@main.command()
@click.option('--title', prompt='Title', type=click.STRING)
@click.option('--services', prompt='Services (comma-separated list)',
              type=click.STRING, required=False)
@click.option('--status', prompt=status_prompt, default='investigating',
              type=click.Choice(status_choices))
@click.option('--state', prompt=state_prompt, type=click.Choice(state_choices))
@click.option('--text', prompt='Text', type=click.STRING)
@click.pass_obj
def create(page, title, services, text, status, state):
    """
    Open a new incident.
    """
    page.add_incident(title, services, text, status, state)
