import os
from functools import update_wrapper

import click

from .conf import parse_config
from .page import Page


default_config_path = os.path.join('~', '.runstatus')
default_verbosity = 0


class State(click.Context):
    def __init__(self, config=default_config_path, verbose=default_verbosity):
        self.config = config
        self.verbose = verbose

    def __repr__(self):
        return "<State config={} verbose={}>".format(self.config, self.verbose)


pass_state = click.make_pass_decorator(State, ensure=True)


def config_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        if value:
            state.config = value
    return click.option('-c', '--config',
                        expose_value=False,
                        envvar='RUNSTATUS_CONFIG',
                        help='Path to the configuration file.',
                        callback=callback)(f)


def verbose_option(f):
    def callback(ctx, param, value):
        state = ctx.ensure_object(State)
        if value:
            state.verbose = value
    return click.option('-v', '--verbose',
                        expose_value=False,
                        count=True,
                        help='Increase output verbosity.',
                        callback=callback)(f)


def setup_state(state):
    page, key, secret, endpoint = parse_config(state.config, click)
    state.page = Page(page=page, api_key=key, secret_key=secret,
                      endpoint=endpoint, ctx=state)


def common_options(f):
    f = config_option(f)
    f = verbose_option(f)

    if f.__name__ == 'main':
        return f

    @pass_state
    def inner(_state, *args, **kwargs):
        setup_state(_state)
        return f(_state, *args, **kwargs)
    return update_wrapper(inner, f)


@click.group()
@common_options
def main():
    pass


@main.command()
@common_options
def info(state):
    """
    Display the status information.
    """
    state.page.print_summary()


@main.command()
@click.argument('action', type=click.Choice(['add', 'remove']))
@click.argument('name')
@common_options
def services(state, action, name):
    """
    Manage services listed on the status page.
    """
    act = getattr(state.page, '{0}_service'.format(action))
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
@common_options
def update(_state, incident, status, state, text):
    """
    Update an open incident.
    """
    _state.page.add_event(incident, status, state, text)


@main.command()
@click.argument('incident', type=click.INT)
@click.option('--text', prompt='Text', type=click.STRING)
@common_options
def resolve(state, incident, text):
    """
    Resolve an open incident.
    """
    state.page.add_event(incident, 'resolved', 'operational', text)


@main.command()
@click.option('--title', prompt='Title', type=click.STRING)
@click.option('--services', prompt='Services (comma-separated list)',
              type=click.STRING, required=False)
@click.option('--status', prompt=status_prompt, default='investigating',
              type=click.Choice(status_choices))
@click.option('--state', prompt=state_prompt, type=click.Choice(state_choices))
@click.option('--text', prompt='Text', type=click.STRING)
@common_options
def create(_state, title, services, text, status, state):
    """
    Open a new incident.
    """
    _state.page.add_incident(title, services, text, status, state)
