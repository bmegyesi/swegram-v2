from re import sub
import subprocess
import os

from invoke import task


@task
def clean_up(_):
    subprocess.run('rm -rf dist build'.split())

@task(pre=[clean_up])
def build_whl(_):
    """
    build a wheel
    precondition: wheel is installed
    """
    try:
        subprocess.run('python3 setup.py bdist_wheel'.split())
    except:
        subprocess.run('python setup.py bdist_wheel'.split())

@task(pre=[build_whl])
def install(_):
    try:
        try:
            subprocess.run('pip uninstall swegram'.split(), input=b'y')
        except:
            ...
        whl = os.path.join(
            os.getcwd(),
            'dist',
            os.listdir(
                os.path.join(os.getcwd(), 'dist')
            )[-1]
        )
        subprocess.run(f'pip install {whl}'.split())
    
    except:
        print('pip install swegram with wheel fails')
        
    
    