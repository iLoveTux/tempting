# -*- coding: utf-8 -*-

"""Console script for tempting."""
import os
import sys
import json
import glob
import click
import requests
from lxml import etree
from time import sleep
from pathlib import Path
import jinja2
from jinja2 import Environment, FunctionLoader

def load_filename(name):
    with Path(name).open("rb") as fin:
        ret = fin.read()
    return ret.decode()

def render_directory(src, dst, recursive, namespace):
    global env
    for item in src.iterdir():
        item = item.resolve()
        if item.is_dir():
            if recursive:
                new_dir = dst / item.name
                # print(new_dir)
                template = env.from_string(str(new_dir), globals=namespace)
                try:
                    os.makedirs(template.render())
                except FileExistsError:
                    pass
                render_directory(item, new_dir, recursive, namespace)
        elif item.is_file():
            render_file(item, dst / item.name, namespace)

templates = {}
def render_file(src, dst, namespace):
    global env
    global templates
    mtime = src.stat().st_mtime
    if src.as_posix() in templates:
        if mtime != templates[src.as_posix()]:
            print("{}: {}: cached version is stale".format(src.as_posix(), mtime))
            templates[src.as_posix()] = mtime
            dst = Path(env.from_string(str(dst), globals=namespace).render())
            template = env.get_template(str(src), globals=namespace)
            try:
                dst.write_text(template.render())
            except ValueError:
                print("Error rendering template")
        else:
            pass
            # print("{}: {}: found cached".format(src.as_posix(), mtime))
    else:
        print("Found {}".format(src.as_posix()))
        templates[src.as_posix()] = mtime
        dst = Path(env.from_string(str(dst), globals=namespace).render())
        template = env.get_template(str(src), globals=namespace).render()
        dst.write_text(template)


default_namespace = {
    "environ": os.environ,
    "requests": requests,
    "json": json,
    "etree": etree,
    "open": open,
    "sys": sys,
    "os": os,
}
@click.command()
@click.argument("src")
@click.argument("dst")
@click.option("--interval", "-i", default=0, type=int)
@click.option("--recursive", "-R", is_flag=True, default=False)
@click.option("--namespace", "-N", default="os.environ", type=str)
def main(src, dst, interval, recursive, namespace):
    """Console script."""
    global env
    env = Environment(
        loader=FunctionLoader(load_filename),
        cache_size=0,
    )
    src, dst = map(Path, (src, dst))
    src, dst = src.resolve(), dst.resolve()
    old_namespace = None
    while True:
        if isinstance(namespace, (str, Path)):
            namespace_file = namespace
            with open(namespace, "r") as fin:
                namespace = default_namespace
                namespace.update(
                    {
                        "args": {
                            "src": src,
                            "dst": dst,
                            "interval": interval,
                            "recursive": recursive,
                            "namespace": namespace_file
                        }
                    }
                )
                namespace.update(json.load(fin))
        data_changed = old_namespace != namespace
        if data_changed:
            if src.is_dir():
                if not dst.is_dir():
                    raise ValueError("If src is a directory, dst must also be a directory")
                render_directory(src, dst, recursive, namespace)
            elif src.is_file():
                if dst.exists() and dst.is_dir():
                    dst = dst / src.name
                elif not dst.exists():
                    dst.parent.mkdir(parents=True)
                    render_file(src, dst, recursive, namespace)
            else:
                raise ValueError("src must be either a file or directory.")
        if interval <= 0:
            break
        else:
            sleep(interval)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
