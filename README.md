[![Build Status](https://travis-ci.org/instituteofdesign/django-lms.png)](https://travis-ci.org/instituteofdesign/django-lms)

Django-lms
=================================

After ten years of use, we are looking to replace our old intranet here at ID (www.id.iit.edu). There are many options out there, but almost all of them are too heavy weight for us. Being a Django shop, we looked for a Django course management / intranet system. Couldn't find one. That is where this project was born.

It aims to be a simple system. Starting with a springboard interface that is easily customizable from Django's admin. It will include a few modules by default: classes, people, news & alerts, admin, help, and knowledge base.

If you're interested in helping, please drop me a line at cezar@id.iit.edu

Requirements
------------

Requires Python 2.7

Rest of the requirements should be installable with pip.

Uses Postgres by default. As of now there isn't anything Postgres specific in the codebase so it should be portable to Mysql just by flipping the database engine.


Installation
------------

- Create a project directory

 `mkdir django-lms`
 
 `cd django-lms`

- Create a virtual environment.

 `virtualenv venv`

- Activate the environment

 `source venv/bin/activate`

- Clone the repo

 `git clone --recursive git@github.com:instituteofdesign/django-lms.git`

- Use the requirements file in the repo

 `pip install -r django-lms/requirements.txt`

Configuration
-------------

- Django-lms is setup for using 12factor type configuration. This means that all localized settings come from the environment. I recommend using [Autoenv](https://github.com/kennethreitz/autoenv) for local development. Else, [Honcho](https://github.com/nickstenning/honcho) or [foreman](http://ddollar.github.com/foreman/) in production. I have placed an example.env file here to show you the settings. Note: I don't think you need the export for honcho/forman

- The db defaults to a local postgres install. For development, I strongly recommend the [postgres.app](postgresapp.com) project.

- Sync the database

 `python manage.py syncdb`

- Run the dev server

 `python manage.py runserver`

The application is now installed. You'll notice that the springboard show no Icons. Since these are customizable, you'll need to set them yourself. I hope to change this soon, to set some defaults. This can be done from the admin.

Logo
----
Django-lms comes with a basic logo. It's in images unders static-files. I recommend using your own logo in deployment.
