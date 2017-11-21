# LSPE/Strip Test Database

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repository contains a Django project that runs a site to access a database
of polarimetric unit tests for the [LSPE](http://planck.roma1.infn.it/lspe/index.html)/[Strip](http://planck.roma1.infn.it/lspe/strip.html) instrument.

So far, the project is able to handle the test files acquired during the unit
tests done in the cryogenic laboratory of the University of Milano Bicocca.

## Installation

The program is written using Python3 and Django. The list of packages needed for
the installation is listed in the file
[requirements.txt](https://github.com/lspestrip/stdb2/blob/master/requirements.txt).

If you are using [Anaconda Python](https://www.anaconda.com/) (as you should),
you can install most of the packages above using `conda` from the command line
(e.g., `conda install PACKAGE1 PACKAGE2...`). A few of them are not available
with `conda`: in this case use `pip install`.

Once you have a fully working Python environment, clone this repository:

    git clone https://github.com/lspestrip/stdb2 && cd stdb2

Before running the application, you have to configure it. Copy the file
`example.env` into a file named `.env`, and modify its settings according to
your desire. In particular, you have to select a database backend in
`DATABASE_ENGINE`. Possible alternatives are:

- `django.db.backends.sqlite3`: [SQLite3](https://sqlite.org/) (no configuration needed, thus very useful for debugging)
- `django.db.backends.postgresql`: [PostgreSQL](https://www.postgresql.org/) (my personal top choice)
- `django.db.backends.mysql`: [MySQL](https://dev.mysql.com/)
- `django.db.backends.oracle`: [Oracle Database](https://www.oracle.com/it/database/index.html)

Another important option is `MEDIA_ROOT`, which points to the directory where
uploaded tests will be saved. Be sure to pick a directory outside the Git
repository of the code, otherwise you might inadvertently fill your repository
with lots of data!

Once you have your fully tailored `.env` file, it's time to create the database.
From the `stdb2` directory run the following commands:

    python manage.py makemigrations && python manage.py migrate

Now you must create an administrator account: this will be used to populate a
few tables of the database which cannot be modified by normal users of the site:

    python manage.py createsuperuser

You can now launch the site with the following command:

    python manage.py runserver

It's time to fill a few database tables. Connect to http://127.0.0.1:8000/admin
and log in using your administrator credentials. You must now enter some values
in the tables `Operators` (list of the persons which have conducted the tests)
and `TestTye` (types of tests for which data have been acquired).

Now it's time to run the site: disconnect from the `admin` page and go to
http://127.0.0.1:8000/unittests. You can now start enjoying the site!


## Running stdb2 with nginx and uWSGI

A good tutorial to show how to run Django-based applications (like stdb2) is
available in the [uWSGI
documentation](http://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html).


## Logging

By default, `stdb2` will write log messages into `stdb2.log`, within the base
directory of the source code. You can customize the location of this file
by setting the variable `LOG_FILE_PATH` in the configuration file `.env`.


## Utilities

The base directory contains a standalone program, `convert_to_hdf5.py`, which
can be used to convert data files into HDF5 files from the command line. Run

    convert_to_hdf5.py -h

to get the full help.