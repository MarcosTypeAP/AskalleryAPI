"""Run this script to start-up the project."""


import os
import platform
import sys


def install_dependencies(pip):
    """Returns the requirements file name to be installed."""
    neovim = input('Will you use neovim? [y/N]: ').upper()
    if neovim == 'Y':
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


def main():
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
