import argparse

def parse_grep_args(args):
    parser = argparse.ArgumentParser(prog='grep', add_help=False)
    parser.add_argument('-r', action='store_true', help='search recursively in subdirectories')
    parser.add_argument('-i', action='store_true', help='case-insensitive search')
    parser.add_argument('pattern', help='pattern to search for')
    parser.add_argument('path', help='file or directory to search in')

    try:
        return parser.parse_args(args)
    except SystemExit:
        return None

def parse_cp_args(args):
    parser = argparse.ArgumentParser(prog='cp', add_help=False)
    parser.add_argument('-r', action='store_true', help='copy directories recursively')
    parser.add_argument('source', help='source file or directory')
    parser.add_argument('destination', help='destination path')

    try:
        return parser.parse_args(args)
    except SystemExit:
        return None

def parse_ls_args(args):
    parser = argparse.ArgumentParser(prog='ls', add_help=False)
    parser.add_argument('-l', action='store_true', help='detailed listing')
    parser.add_argument('path', nargs='?', help='path to list')

    try:
        return parser.parse_args(args)
    except SystemExit:
        return None

def parse_mv_args(args):
    parser = argparse.ArgumentParser(prog='mv', add_help=False)
    parser.add_argument('source', help='source file or directory')
    parser.add_argument('destination', help='destination path or new name')

    try:
        return parser.parse_args(args)
    except SystemExit:
        return None

def parse_rm_args(args):
    parser = argparse.ArgumentParser(prog='rm', add_help=False)
    parser.add_argument('-r', action='store_true', help='remove directories recursively')
    parser.add_argument('path', help='file or directory path to remove')

    try:
        return parser.parse_args(args)
    except SystemExit:
        return None

def parse_tar_args(args):
    parser = argparse.ArgumentParser(prog='tar', add_help=False)
    parser.add_argument('folder', help='directory to archive')
    parser.add_argument('name', help='name of the tar archive')

    try:
        return parser.parse_args(args)
    except SystemExit:
        return None

def parse_untar_args(args):
    parser = argparse.ArgumentParser(prog='untar', add_help=False)
    parser.add_argument('archive', help='path to tar archive')

    try:
        return parser.parse_args(args)
    except SystemExit:
        return None

def parse_unzip_args(args):
    parser = argparse.ArgumentParser(prog='unzip', add_help=False)
    parser.add_argument('archive', help='path to zip archive')

    try:
        return parser.parse_args(args)
    except SystemExit:
        return None

def parse_zip_args(args):
    parser = argparse.ArgumentParser(prog='zip', add_help=False)
    parser.add_argument('folder', help='directory to zip')
    parser.add_argument('name', help='name of the zip archive')

    try:
        return parser.parse_args(args)
    except SystemExit:
        return None