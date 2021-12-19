"""Run this script to start-up the project."""


import os
import platform


def install_dependencies(pip):
    """Returns the requirements file name to be installed."""
    neovim = input('Will you use neovim? [y/N]: ').upper()
    if neovim == 'Y':
        file_name = 'neovim.txt'
    else:
        file_name = 'dev.txt'
    os.system(f'{pip} --quiet install -r requirements/{file_name}')


def main():
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
    os.system(f'{python} manage.py runserver 0.0.0.0:8000')


if __name__ == "__main__":
   main()
