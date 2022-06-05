from datetime import datetime, timedelta, date
import math
import csv
import requests
import click
import validators

from pprint import pp

ENDPOINT = 'https://api.monobank.ua'


@click.group()
def cli():
    pass

@cli.command()
@click.argument('mono_token')
@click.option('--from-date', type=click.DateTime(formats=['%d.%m.%Y']), default=date.today().strftime('%d.%m.%Y'))
@click.option('--ticket-price', default=100)
@click.option('--format', default='csv', callback=validators.validate_format)
def extract_jar_transactions(from_date, mono_token, ticket_price, format):
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
    
    from_date = from_date.replace(microsecond=0)

    r = requests.get(
        '{url}/personal/statement/{account}/{from_timestamp}'.format(
            url=ENDPOINT,
            account=selected_jar.get('id'),
            from_timestamp=str(int(from_date.timestamp()))
        ),
        headers={
            'Content-Type': 'application/json; charset=utf-8',
            'X-Token': mono_token
        }
    )

    statement = r.json()
    total = 0
    report_data = [
        ['ID', 'Name', 'Amount']
    ]

    i = 1
    for operation in statement:
        if operation.get('amount') < 0 or not operation.get('description') or not operation.get('description').startswith('Від:'):
            continue

        amount = operation.get('amount')/100
        total += amount
        donater = operation.get('description').replace('Від: ', '')
        tickets = math.trunc(amount/ticket_price)

        
        if tickets > 1:
            for _ in range(tickets):
                report_data.append([
                    i, donater, amount
                ])
                i += 1
        else:
            report_data.append([
                i, donater, amount
            ])
            i += 1
        # print(
        #     '[💸] {} {} tickets ({} UAH)'.format(
        #         donater,
        #         tickets,
        #         amount
        #     )
        # )

    print('Amount for period: {}'.format(total))

    if format == 'csv':
        with open('report.csv', 'w+') as f:
            writer = csv.writer(f)
            for row in report_data:
                writer.writerow(row)

if __name__ == '__main__':
    cli()
