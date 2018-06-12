========
tempting
========


.. image:: https://img.shields.io/pypi/v/tempting.svg
        :target: https://pypi.python.org/pypi/tempting

.. image:: https://img.shields.io/travis/ilovetux/tempting.svg
        :target: https://travis-ci.org/ilovetux/tempting

.. image:: https://readthedocs.org/projects/tempting/badge/?version=latest
        :target: https://tempting.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Template all the things.


* Free software: GNU General Public License v3
* Documentation: https://tempting.readthedocs.io.


Features
--------

* Near-Real time rendering of templates
* Template file and directory names
* Jinja2 template engine
* Easy to use
* Plain JSON namespacing
* Only re-renders when templates change

* TODO: Stream data trough templates into output files (like logs)
* TODO: Robust error handling

Rationalle
----------

I love ansible, but sometimes it is too heavy-handed and it can be a lot to
setup anything non-trivial. I also like cookiecutter, but it is made to do
something else (quicky start a new project) and as such has some opinions
which didn't fall in line with what I needed (although I did get it to work).

My requirements were as follows:

I had two use-cases off-the-bat:

  1. Continuously render templated HTML files on the backend to serve a (semi)static web site
  2. Render configuration for a number of servers with configuration in the 10s
     of thousands of lines. (We got this down to a 50 line template rendering to
     72,678 line configuration)

So what I needed was the following features:

  * Continuously run in the background or run on-demand
  * Simple namespace declaration and referencing
  * Recursive, but not by default
  * Template file and directory names
  * No machinery or distributed anything to setup before use
  * No configuration necessary
  * Rich templating language with logic built in

I couldn't find what I needed, so I made this project. I wanted to share it
so it is GPLed, enjoy.

Installation
------------

For most use cases it would be best to install the latest stable version
which can be done with the following command::

  $ pip install tempting

For the latest development version, you can install directly from the
master branch with the following commands::

  $ git clone https://github.com/ilovetux/tempting
  $ cd tempting
  $ pip install -e .

Usage
-----

First, you will want to create a namespace file which is simply a json
file which is read at startup and used to render the templates. For our
example consider the following file which will be saved as `./namespace.json`::

  {
    "foo": "bar",
    "bar": 1,
    "baz": ["this is a list", "second item"],
    "foobar": {
      "this": "that",
      "the other": 2
    }
  }

Now we just need some templates to render. For this we will create a directory
called `./in` and we will create a directory called `./out` to hold the rendered
templates::

  $ mkdir in
  $ mkdir out

Next we will start creating some templates. Consider the following file saved
as `./in/first.txt` (this is Jinja2 syntax, RTFM for Jinja2_)::

  Hello {{ foo }}:

  This is a letter to demonstrate the use of tempting the Python templating tool.

  Please consider the following:

  {% for key, value in foobar.items() -%}
  {{ key }}: {{ value }}
  {% endfor -%}

  {{ ",".join(baz) }}

  Thank You.

Now we can run the following command to template this file::

  $ tempting ./in ./out --namespace ./namespace.json

And we should see the following results in `./out/first.txt`::

  Hello bar:

  This is a letter to demonstrate the use of tempting the Python templating tool.

  Please consider the following:

  this: that
  the other: 2
  this is a list,second item

  Thank You.

Advanced Usage
--------------

We can template directory and file names as well, let's create a directory which
will be named after the value of `bar` (NOTE: You may need to escape some
characters in the following command)::

  $ mkdir ./in/{{foo}}

Next let's create a file named after the value of `bar` and render some HTML.
Consider the following file saved as `./in/{{foo}}/{{bar}}.html`::

  <!DOCTYPE html>
  <html>
    <body>
      <p>
        This file is rendered by tempting.
      </p>
      <table>
        <tr>
          {% for key, value in foobar.items() -%}
            <td>{{ key }}</td><td>{{ value }}</td>
          {% endfor -%}
        </tr>
      </table
    </body>
  </html>

Finally, we just need to render these templates. This time we need to specify
`--recursive` so tempting will render the sibdirectories::

  $ tempting ./in ./out --namespace ./namespace.json

Now our directory structure under `./out` will look like so::

  ./out
  │   first.txt
  │
  └───bar
        1.html

And in ./out/bar/1.html, we should have the following content::

  <!DOCTYPE html>
  <html>
  <body>
    <p>
      This file is rendered by tempting.
    </p>
    <table>
      <tr>
        <td>this</td><td>that</td>
        <td>the other</td><td>2</td>
        </tr>
    </table
  </body>
  </html>

Running Continuously
====================

If you specify `--interval f` where f is a floating-point number, then after
rendering the first time, tempting will sleep for the specified interval. When
tempting wakes up it will look at the modified time of all the templates and
if something was changed or added, those files and/or directories will be
re-rendered.

NOTE: Tempting will not remove files or directories from the `dst` directory.

Credits
-------

Original Author and maintainer: ilovetux_

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _Jinja2: http://http://jinja.pocoo.org/
.. _ilovetux: https://github.com/ilovetux
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
