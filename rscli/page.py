from __future__ import unicode_literals

import calendar
import sys
from datetime import datetime, timedelta

import click
import requests
from exoscale_auth import ExoscaleAuth

if sys.version_info >= (3, 3):
    dot = " ● "
else:
    dot = ' o '


def color(st):
    return {
        'operational': 'green',
        'degraded_performance': 'yellow',
        'partial_outage': 'yellow',
        'major_outage': 'red',
    }[st]


TIMESINCE_CHUNKS = (
    (60 * 60 * 24 * 365, '%d years'),
    (60 * 60 * 24 * 30, '%d months'),
    (60 * 60 * 24 * 7, '%d weeks'),
    (60 * 60 * 24, '%d days'),
    (60 * 60, '%d hours'),
    (60, '%d minutes'),
)


def time_ago(d, now=None):
    if not now:
        now = datetime.utcnow()
    try:
        d = datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        d = datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ")
    delta = now - d
    delta -= timedelta(calendar.leapdays(d.year, now.year))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        return '0 minutes'
    for i, (seconds, name) in enumerate(TIMESINCE_CHUNKS):  # noqa
        count = since // seconds
        if count != 0:
            break
    result = name % count
    if i + 1 < len(TIMESINCE_CHUNKS):
        seconds2, name2 = TIMESINCE_CHUNKS[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            result += ", " + name2 % count2
    return result


class Page:
    def __init__(self, page, api_key, secret_key, ctx,
                 endpoint='https://api.runstatus.com'):
        self.page = page
        self.base_endpoint = '{0}/pages/{1}'.format(endpoint, page)
        self.session = requests.Session()
        self.session.auth = ExoscaleAuth(api_key, secret_key)
        self.ctx = ctx

    def get(self):
        response = self.session.get(self.base_endpoint)
        if not response.status_code == 200:
            click.secho("Status page '", fg='red', nl=False)
            click.secho(self.page, bold=True, nl=False)
            click.secho("' not found, status code was {0}.".format(
                response.status_code), fg='red')
            self.ctx.abort()
        return response.json()

    def print_summary(self):
        data = self.get()
        click.secho(dot, nl=False, fg=color(data['state']), bold=True)
        domain = "https://{subdomain}.runstat.us"
        if data['domain']:
            domain = 'https://{domain}'
        click.secho(domain.format(**data), underline=True, nl=False)
        click.secho("\t", nl=False)
        click.secho("[{state}]".format(**data),
                    fg=color(data['state']), bold=True)
        if data['services']:
            click.echo()
            click.secho("Services:", bold=True)
            for service in sorted(data['services'], key=lambda s: s['name']):
                fg = color(service['state'])
                click.secho(dot, nl=False, fg=fg, bold=True)
                click.secho(service['name'], nl=False)
                click.secho("\t", nl=False)
                click.secho("[{state}]".format(**service), bold=True, fg=fg)

        open_incidents = [i for i in data['incidents']
                          if i['end_date'] is None]
        if open_incidents:
            click.echo()
            click.secho("Open incidents:", bold=True)
        for incident in open_incidents:
            incident['id'] = incident['url'].rsplit('/', 1)[-1]
            fg = color(incident['state'])
            click.secho(dot, nl=False, fg=fg, bold=True)
            click.secho("#{id} - {title}".format(**incident), nl=False)
            click.secho("\t[{state}]\t[{status}]".format(**incident),
                        fg=fg)
            event = incident['events'][0]
            click.secho("   {text}".format(**event))
            click.secho("   Created: {0} ago. Updated: {1} ago.".format(
                time_ago(incident['start_date']),
                time_ago(event['created']),
            ), fg='yellow')
            click.secho("   To update this incident: ", fg='cyan', nl=False)
            click.secho("runstatus update {id}".format(**incident))
            click.secho("   To resolve: ", fg='cyan', nl=False)
            click.secho("runstatus resolve {id}".format(**incident))

    def add_service(self, name):
        url = self.base_endpoint + '/services'
        response = self.session.post(url, json={'name': name})
        if response.status_code != 201:
            click.secho("Error adding service '", fg='red', nl=False)
            click.secho(name, nl=False, bold=True)
            click.secho("', API returned HTTP {r.status_code}: "
                        "{r.content}".format(r=response), fg='red')
            self.ctx.abort()
        click.secho("Added service '", nl=False)
        click.secho(name, nl=False, bold=True)
        click.secho("'.")

    def remove_service(self, name):
        try:
            [service] = [s for s in self.get()['services']
                         if s['name'] == name]
        except ValueError:
            click.secho("Unknown service: '", fg='red', nl=False)
            click.secho(name, bold=True, nl=False)
            click.secho("'.", fg='red')
            self.ctx.abort()
        url = service['url']
        response = self.session.delete(url)
        if response.status_code != 204:
            click.secho("Error removing service '", fg='red', nl=False)
            click.secho(name, nl=False, bold=True)
            click.secho("'. API returned HTTP {r.status_code}: "
                        "{r.content}.".format(r=response), fg='red')
            self.ctx.abort()
        click.secho("Removed service '", nl=False)
        click.secho(name, nl=False, bold=True)
        click.secho("'.")

    def add_event(self, incident, status, state, text):
        url = '{0}/incidents/{1}/events'.format(self.base_endpoint, incident)
        response = self.session.post(url, json={'status': status,
                                                'state': state,
                                                'text': text})
        if response.status_code != 201:
            click.secho("Error updating incident #{id}. API returned HTTP "
                        "{r.status_code}: {r.content}.".format(id=incident,
                                                               r=response),
                        fg='red')
            self.ctx.abort()
        click.secho("Incident updated.")

    def add_incident(self, title, services, text, status, state):
        url = self.base_endpoint + '/incidents'
        services = [s.strip() for s in services.split(',') if s.strip()]
        response = self.session.post(url, json={
            'services': services,
            'title': title,
            'status_text': text,
            'status': status,
            'state': state,
        })
        if response.status_code != 201:
            click.secho("Error creating incident. API returned HTTP "
                        "{r.status_code}: {r.content}.".format(r=response),
                        fg='red', nl=False)
            self.ctx.abort()
        click.secho("Incident #{0} created".format(response.json()['id']))
