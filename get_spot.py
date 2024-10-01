"""Download and install spot. (Code adapted from tulip-control/dd/download.py)"""
import tarfile
import urllib.error
import urllib.request
import subprocess
import os
import typing as _ty
import textwrap as _tw
import sys

SPOT_VERSION: _ty.Final = '2.12'
SPOT_TARBALL: _ty.Final = f'spot-{SPOT_VERSION}.tar.gz'
SPOT_URL: _ty.Final = ('http://www.lrde.epita.fr/dload/spot/'
                    f'spot-{SPOT_VERSION}.tar.gz')
FILE_PATH = os.path.dirname(os.path.realpath(__file__))
SPOT_PATH = os.path.join(FILE_PATH,f'spot-{SPOT_VERSION}')
ENV_PATH = sys.prefix

def fetch_spot():
    filename = SPOT_TARBALL
    fetch(SPOT_URL, filename)
    untar(filename)
    make_spot()

def fetch(url,filename):
    if os.path.isfile(filename):
        print(
            f'File `{filename}` already present.')
        return
    print(f'Attempting to download file from URL:  {url}')
    try:
        response = urllib.request.urlopen(url)
        if response is None:
            raise urllib.error.URLError(
                '`urllib.request.urlopen` returned `None` '
                'when attempting to open the URL:  '
                f'{url}')
    except urllib.error.URLError as url_error:
        raise RuntimeError(_tw.dedent(f'An exception was raised when attempting to open the URL: {url}'))
    with response, open(filename, 'wb') as f:
        f.write(response.read())
    print(
        'Completed downloading from URL '
        '(may have resulted from redirection):  '
        f'{response.url}\n'
        'Wrote the downloaded data to file:  '
        f'`{filename}`\n')

def untar(filename):
    print(f'++ unpack: {filename}')
    with tarfile.open(filename) as tar:
        tar.extractall()
    print('-- done unpacking.')

def make_spot():
    """Compile spot."""
    path = SPOT_PATH
    cmd = ["./configure --prefix "+ ENV_PATH]
    print('running: '+str(cmd)+' in '+path)
    # subprocess.call(cmd, cwd=path)
    subprocess.check_call('./configure --prefix /flowsynth/.venv', shell=True, cwd=path)
    subprocess.check_call(['make'], cwd=path)
    subprocess.check_call(['make','install'], cwd=path)

if __name__ == '__main__':
    fetch_spot()
