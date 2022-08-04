from distutils.core import setup

setup(
    name='pyp4qt',
    version='1.0.0',
    packages=['pyp4qt', 'pyp4qt.qt', 'pyp4qt.apps', 'pyp4qt.apps.maya',
              'pyp4qt.apps.nuke', 'pyp4qt.apps.standalone', 'pyp4qt.apps.katana',
              'pyp4qt.apps.houdini', 'pyp4qt.perforce_utils', 'test_perforce', 'test_perforce.qt'],
    package_dir={'': 'src'},
    url='https://github.com/KidKaboom/pyp4qt',
    license='MIT',
    author='Justin Tirado',
    author_email='',
    description='A Perforce Toolset for QT Applications with Python'
)
