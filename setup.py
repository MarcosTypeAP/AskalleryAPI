"""Run this script to start-up the project."""


import os
import platform
import sys


def get_choice(message, yes_default, extra_info=None):
    """Prints a message and get the user input.
    Returns whether the users input was Yes or No.
    """
    if extra_info:
        print(extra_info)
    user_input = input(message).upper()
    if user_input == 'Y' or (not user_input and yes_default):
        return True
    elif user_input == 'N' or (not user_input and not yes_default):
        return False
    elif yes_default:
        return True
    else:
        return False


def install_dependencies(pip):
    """Returns the requirements file name to be installed."""
    neovim = get_choice('Will you use neovim? [y/N]: ', yes_default=False)
    if neovim:
        file_name = 'neovim.txt'
    else:
        file_name = 'dev.txt'
    os.system(f'{pip} --quiet install -r requirements/{file_name}')


def print_help():
    """Prints the docs for this script."""
    print(
        """
        Quick setup and start-up script for the project.

        -l, --listen    Specify the port and address on which the server will listen.
                        Eg: 0.0.0.0:8000 or localhost:8080

        -h, --help      Prints this text.
        """
    )


def validate_env_file():
    """Validates that 'SECRET_KEY' and 'LOCAL_DEV' are set."""
    with open('.env', 'r') as f:
        SECRET_KEY = False
        LOCAL_DEV = False
        for line in f.readlines():
            if 'SECRET_KEY=' in line and len(line) > 11:
                SECRET_KEY = True
            if 'LOCAL_DEV=' in line and len(line) > 10:
                LOCAL_DEV = True

        if not LOCAL_DEV:
            print(
                '\tThe "LOCAL_DEV" is missing in the .env file or is set to False.\n\tSet it and try again.'
            )
            return False
        if not SECRET_KEY:
            print(
                '\tThe "SECRET_KEY" is missing in the .env file.\n\tSet it and try again.'
            )
            return False
    return True


def create_env_file():
    """Creates a .env file with the essential variables."""
    with open('.env', 'w') as f:
        new_lines = [
            'SECRET_KEY=eMeVgUdFOZy2/kBZpfmMH4OSdU4TZHuwtYWKQ2jWBk9HR65goLGprg3eHWv3o/Ti40PbRswFdYuKn2Yy0mPfEw==\n',
            'LOCAL_DEV=1\n',
            'APP_URL=localhost\n',
            'DEBUG=1\n',
            'HTTP_PROTOCOL=http\n'
        ]
        f.writelines(new_lines)


def set_vars_tutorial():
    """Prints how to set DJANGO_READ_DOT_ENV_FILE based on OS."""
    if platform.system() == 'Windows':
        print('To set "DJANGO_READ_DOT_ENV_FILE" to 1, run:')
        print("\t[System.Environment]::SetEnvironmentVariable('DJANGO_READ_DOT_ENV_FILE','1'")
        print('And run setup.py again.')
    else:
        print('To set "DJANGO_READ_DOT_ENV_FILE" to 1, run:')
        print('\texport DJANGO_READ_DOT_ENV_FILE=1')
        print('And run setup.py again.')


def environment_variables_exist():
    """Verifies that the environment variables exist
    or creates a .env file with the essential variables.
    """
    if os.environ.get('DJANGO_READ_DOT_ENV_FILE') != '1':
        create_env = get_choice(
            extra_info='The "DJANGO_READ_DOT_ENV_FILE" variable is not set.',
            message='Do you want to set it? [Y/n]: ',
            yes_default=True
        )
        if create_env:
            set_vars_tutorial()
            return False
        else:
            if not os.environ.get('SECRET_KEY'):
                print('\tThe "SECRET_KEY" is not set.')
                print('\tSet it and try again.')
                return False
            if os.environ.get('LOCAL_DEV') != '1':
                print('\tThe "LOCAL_DEV" is not set.')
                print('\tSet it and try again.')
                return False
            return True
    else:
        if os.path.exists('.env'):
            overwrite = get_choice(
                'A .env file already exists. Overwrite it? [N/y]: ',
                yes_default=False
            )
            if overwrite:
                create_env_file()
                return True
            return validate_env_file()
        else:
            create_env_file()
            return True


def main():
    if not environment_variables_exist():
        return 0

    if len(sys.argv) == 1:
        address = '0.0.0.0:8000'
    elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print_help()
        return 0
    elif sys.argv[1] == '-l' or sys.argv[1] == '--listen':
        try:
            address = sys.argv[2]
        except IndexError:
            print('You must specify an address.')
            return 0
    else:
        print('Arguments not recognized')
        return 0

    if not os.path.exists('static'):
        os.mkdir('static')

    if platform.system() == 'Windows':
        python = 'python'
        pip = 'pip'
    else:
        python = 'python3'
        pip = 'pip3'

    install_dependencies(pip)
    os.system(f'{python} manage.py collectstatic --no-input')
    os.system(f'{python} manage.py makemigrations')
    os.system(f'{python} manage.py migrate')
    os.system(f'{python} manage.py runserver {address}')


if __name__ == "__main__":
    main()
