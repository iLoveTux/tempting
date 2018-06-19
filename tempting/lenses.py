"""a simple, streaming, templating engine designed to
help produce usable information.

our utility, lenses, lets you write Python code in a
declarative manner with eval based superpowers.

a lense is a python dict which :

  * name: a unique name
  * tests:
  * templates: a template
  3. a test

lenses are useful for creating useful information
out of raw data streams. They are evaluated and
rendered withhin the context of a line-delimeted
data stream. The most basic of which is the noble
text file. To this end, there is a command line
program which takes a configuration of lenses and
any number of input files (URLs are supported as
well).

a unique name is required which creates a namespace.
this namespace allows the storage of state. this
namespace is used as the execution environment of
both the template and the test. it also persists and
can be queried by other templates based on permissions
given to the templates

The template consists of a multi-line string which
will be rendered with any instance of
{{$PYTHON_STATEMENT}} replaced with the value
to which $PYTHON_STATEMENT evaluates.

the test is also required, this is a Python
statement which acts as  a test and should
evaluate to a truthy value if the template
should be rendered.

A set of lenses are defined in a file named with
the `.lns` extension and are in the following
format:

<$NAME />:<$TEST />
    <Multi-LINE
     template />

to be explicit, the multi-line template is
placed within a hanging indent under the name
and test which are on their own line seperated
by a colon.
"""
from threading import Lock
from glob import glob
import logging.config
import configparser
import fileinput
import logging
import yaml
import atexit
import click
import sys
import os
import re

config_parser = configparser.ConfigParser()

statement = re.compile(r"(\{\{(.*?)\}\})")
class Template(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.tests = kwargs.get("tests")
        self.templates = kwargs.get("templates")
        self.namespace = kwargs.get("namespace", {})
        self.begin = kwargs.get("begin", list())
        self.begin_line = kwargs.get("begin_line", list())
        self.end = kwargs.get("end", list())
        self.end_line = kwargs.get("end_line", list())
        for item in self.begin:
            exec(item, self.namespace)
        for item in self.end:
            if item is not None:
                atexit.register(exec, item, self.namespace)

    def should_render(self, line):
        self.namespace.update({"line": line})
        return all(eval(test, self.namespace) for test in self.tests)

    def render(self, line):
        log = logging.getLogger(self.name)
        for item in self.begin_line:
            exec(item, self.namespace)
        for name, template in self.templates.items():
            _log = logging.getLogger("{}.{}".format(self.name, name))
            message = template
            for match in statement.findall(message):
                message = message.replace(match[0], eval(match[1], self.namespace))
            _log.info(message)
        for item in self.end_line:
            if item is not None:
                exec(item, self.namespace)


@click.command()
@click.argument("config")
@click.argument("files", nargs=-1)
@click.option("--logging-config", "-L")
@click.option("--logging-format", default="%(message)s")
def main(config, files, logging_config, logging_format):
    log = logging.getLogger(__name__)
    if logging_config:
        with open(logging_config, "r") as fp:
            logging.config.dictConfig(eval(fp.read()))
    else:
        logging.basicConfig(
            stream=sys.stdout,
            level=10,
            format=logging_format,
        )
    if not files:
        files = ["-"]
    filenames = []
    for filename in files:
        if filename == "-":
            filenames.append("-")
        else:
            filenames.extend(glob(filename))
    with open(config, "r") as fp:
        template_config = eval(fp.read())
    print(template_config)
    templates = {name: Template(name=name, **kwargs) for name, kwargs in template_config.items()}

    last_filename = None
    nr = 0
    for line in fileinput.input(filenames):
        if fileinput.filename() != last_filename:
            fnr = 0
        fnr, nr = fnr + 1, nr + 1
        for name, template in templates.items():
            template.namespace.update({
                "line": line,
                "nr": nr,
                "fnr": fnr,
            })
            if template.should_render(line):
                template.render(line)

if __name__ == "__main__":
    main()
