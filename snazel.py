import argparse
import os
import hashlib
import pathlib
import glob

import yaml

ROOT_DIR = "/Project"


def main():
    parser = argparse.ArgumentParser(prog="snazel")
    parser.add_argument("-v", "--version")

    subparsers = parser.add_subparsers(dest="cmd")

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("name", type=str)

    args = parser.parse_args()

    match args.cmd:
        case "build":
            build(args.name)


def build(name: str):
    (path, rule_name) = name.split(":")
    path = pathlib.Path(path.replace("//", ROOT_DIR + "/"))

    rule = parse_rules(path, rule_name)
    rule_hash = hash_dict_tuple(rule)

    # print(rule)
    print(rule_hash)
    # print(rule["srcs"])

    includes = []
    for include in rule["srcs"]["include"]:
        includes.extend(path.glob(include))

    excludes = []
    for exclude in rule["srcs"]["exclude"]:
        excludes.extend(path.glob(exclude))


    files =  sorted(set([i for i in includes if i not in excludes and os.path.isfile(i)]))

    # for file in files:
    #     print(file)

    files_hash = hash_files(files)
    print(files_hash)




def parse_rules(path: os.PathLike, rule_name: str):
    rule_file = path / "build.yml"
    with open(rule_file, "r") as f:
        rules = yaml.safe_load(f)

    return rules[rule_name]


def hash_dict_tuple(d, hash_algorithm="sha256"):
    hash_func = hashlib.new(hash_algorithm)

    # Convert dict to sorted tuple format
    dict_tuple = tuple(sorted((k, tuple(v) if isinstance(v, list) else v) for k, v in d.items()))

    # Hash the string representation of the tuple
    hash_func.update(str(dict_tuple).encode("utf-8"))

    return hash_func.hexdigest()

def hash_files(files: list[os.PathLike], hash_algorithm="sha256"):
    hash_func = hashlib.new(hash_algorithm)

    for file in files:
        hash_func.update(str(file).encode("utf-8"))

        with open(file, "rb") as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)


    return hash_func.hexdigest()


if __name__ == "__main__":
    main()
