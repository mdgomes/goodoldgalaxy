from setuptools import setup, find_packages
from glob import glob
import subprocess
from goodoldgalaxy.version import VERSION

# Generate the translations
subprocess.run(['bash', 'scripts/compile-translations.sh'])

setup(
    name="goodoldgalaxy",
    version=VERSION,
    packages=find_packages(exclude=['tests']),
    scripts=['bin/goodoldgalaxy'],

    data_files=[
        ('share/applications', ['data/io.github.mdgomes.goodoldgalaxy.desktop']),
        ('share/icons/hicolor/128x128/apps', ['data/icons/128x128/io.github.mdgomes.goodoldgalaxy.png']),
        ('share/icons/hicolor/192x192/apps', ['data/icons/192x192/io.github.mdgomes.goodoldgalaxy.png']),
        ('share/goodoldgalaxy/ui', glob('data/ui/*.ui')),
        ('share/goodoldgalaxy/images', glob('data/images/*')),
        ('share/metainfo', ['data/io.github.mdgomes.goodoldgalaxy.metainfo.xml']),

        # Add translations
        ('share/goodoldgalaxy/translations/de/LC_MESSAGES/', ['data/mo/de/LC_MESSAGES/goodoldgalaxy.mo']),
        ('share/goodoldgalaxy/translations/es/LC_MESSAGES/', ['data/mo/es/LC_MESSAGES/goodoldgalaxy.mo']),
        ('share/goodoldgalaxy/translations/fr/LC_MESSAGES/', ['data/mo/fr/LC_MESSAGES/goodoldgalaxy.mo']),
        ('share/goodoldgalaxy/translations/nb_NO/LC_MESSAGES/', ['data/mo/nb_NO/LC_MESSAGES/goodoldgalaxy.mo']),
        ('share/goodoldgalaxy/translations/nl/LC_MESSAGES/', ['data/mo/nl/LC_MESSAGES/goodoldgalaxy.mo']),
        ('share/goodoldgalaxy/translations/nn_NO/LC_MESSAGES/', ['data/mo/nn_NO/LC_MESSAGES/goodoldgalaxy.mo']),
        ('share/goodoldgalaxy/translations/pl/LC_MESSAGES/', ['data/mo/pl/LC_MESSAGES/goodoldgalaxy.mo']),
        ('share/goodoldgalaxy/translations/pt_BR/LC_MESSAGES/', ['data/mo/pt_BR/LC_MESSAGES/goodoldgalaxy.mo']),
        ('share/goodoldgalaxy/translations/ru_RU/LC_MESSAGES/', ['data/mo/ru_RU/LC_MESSAGES/goodoldgalaxy.mo']),
        ('share/goodoldgalaxy/translations/tr/LC_MESSAGES/', ['data/mo/tr/LC_MESSAGES/goodoldgalaxy.mo']),
        ('share/goodoldgalaxy/translations/zh_CN/LC_MESSAGES/', ['data/mo/zh_CN/LC_MESSAGES/goodoldgalaxy.mo']),
        ('share/goodoldgalaxy/translations/zh_TW/LC_MESSAGES/', ['data/mo/zh_TW/LC_MESSAGES/goodoldgalaxy.mo']),
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
        'PyGObject>=3.30',
        'requests',
    ],

    # metadata to display on PyPI
    author="Miguel Gomes",
    author_email="alka.setzer@gmail.com",
    description="A simple GOG Linux client",
    keywords="GOG gog client gaming gtk Gtk",
    url="https://github.com/mdgomes/goodoldgalaxy",  # project home page, if any
    project_urls={
        "Bug Tracker": "https://github.com/mdgomes/goodoldgalaxy/issues",
        "Documentation": "https://github.com/mdgomes/goodoldgalaxy/blob/master/README.md",
        "Source Code": "https://github.com/mdgomes/goodoldgalaxy",
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ]
)
