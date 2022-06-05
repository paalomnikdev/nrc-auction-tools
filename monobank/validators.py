import click

def validate_format(ctx, param, value):
    ALLOWED_FORMATS = ['csv', 'sheet']

    if value not in ALLOWED_FORMATS:
        raise click.BadParameter('{} is not allowed report format'.format(value))

    return value