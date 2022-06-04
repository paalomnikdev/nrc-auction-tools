# from dateutil import parser
from datetime import datetime, timedelta
import requests
import click
from pprint import pp

ENDPOINT = 'https://api.monobank.ua'


@click.group()
def cli():
    pass

@cli.command()
@click.argument('mono_token')
@click.option('--ticket-price', default=100)
def extract_jar_transactions(mono_token, ticket_price):
    r = requests.get(
        '{}/personal/client-info'.format(ENDPOINT),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'X-Token': mono_token
        }
    )

    if r.status_code != 200:
        print(r.json())
        quit()

    client_data = r.json()
    jars = client_data.get('jars')

    if not jars:
        print('[❗] No jars. Exiting.')

    message = "Found next jars: \n"

    valid_jar_numbers = []

    for i,jar in enumerate(jars):
        valid_jar_numbers.append(i)
        message += "[{}] {} ({} UAH) \n".format(str(i), jar.get('title', 'no title'), str(jar.get('balance', 0)/100))

    print(message)

    jar_number = click.prompt('[🙋] Please enter your choice', type=int)
    
    if jar_number not in valid_jar_numbers:
        click.echo('[❗] Invalid jar number. Exiting.')
        quit()

    selected_jar = jars[jar_number]
    click.echo('[✅] {} selected'.format(selected_jar.get('title')))
    
    now = datetime.now().replace(microsecond=0)

    r = requests.get(
        '{url}/personal/statement/{account}/{from_timestamp}/{to_timestamp}'.format(
            url=ENDPOINT,
            account=selected_jar.get('id'),
            from_timestamp=str(int((now - timedelta(days=7)).timestamp())),
            to_timestamp=str(int(now.timestamp()))
        ),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'X-Token': mono_token
        }
    )

    statement = r.json()

    for operation in statement:
        if operation.get('amount') < 0 or not operation.get('description'):
            continue
        print(
            '[💸] {} {} tickets ({} UAH)'.format(
                operation.get('description'),
                int(round((operation.get('amount')/100)/100, 0)),
                operation.get('amount')/100
            )
        )


if __name__ == '__main__':
    cli()
