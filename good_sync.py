import hashlib
import shutil
import os

from pathlib import Path

BLOCKSIZE = 65536

source_files = {}
dest_files = {}


def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()


def read_paths_and_hashes(root):
    """Функция, которая просто выполняет операции ввода-вывода"""
    hashes = {}
    for folder, _, files in os.walk(root):
        for file in files:
            hashes[hash_file(Path(folder) / file)] = file
    return hashes


def determine_actions(src_hashes, dest_hashes, source, dest):
    """Функция, которая просто выполняет бизнес-логику"""
    for sha, filename in src_hashes.items():
        if sha not in dest_hashes:
            source_path = Path(source) / filename
            dest_path = Path(dest) / filename
            yield 'copy', source_path, dest_path
        elif dest_hashes[sha] != filename:
            old_dest_path = Path(dest) / dest_hashes[sha]
            new_dest_path = Path(dest) / filename
            yield 'move', old_dest_path, new_dest_path

    for sha, filename in dest_hashes.items():
        if sha not in src_hashes:
            yield 'delete', dest / filename





def sync(source, dest):
    # шаг 1 - собрать входные данные
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)

    # шаг 2 - вызвать функциональное ядро
    actions = determine_actions(source_hashes, dest_hashes, source, dest)

    # шаг 3 - применить операции ввода-вывода
    for action, *paths in actions:
        if action == "copy":
            shutil.copyfile(*paths)
        if action == "move":
            shutil.move(*paths)
        if action == "delete":
            os.remove(*paths[0])

