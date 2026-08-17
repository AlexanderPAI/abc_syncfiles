import hashlib
import os
import shutil
from pathlib import Path


BLOCKSIZE = 65536


def hash_file(path):
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()


def sync(source, dest):
    # обойти исходную папку и создать словарь имен и хэшей
    source_hashes = {}

    for folder, _, files in os.walk(source):
        for file in files:
            source_hashes[hash_file(Path(folder) / file)] = file

    seen = set() # отслеживать файлы, найденные в целевой папке

    # обойти целевую папку и создать словарь имен и хэшей
    for folder, _, files in os.walk(dest):
        for file in files:
            dest_path = Path(folder) / file
            dest_hash = hash_file(dest_path)
            seen.add(dest_hash)

            # если в целевой папке есть файл, которого нет в исходной,
            # удалить его
            if dest_hash not in source_hashes:
                dest_path.remove()

            # если в целевой папке есть файл, который имеет другой путь в исходной,
            # переместить его в правильный путь
            elif dest_hash in source_hashes and file != source_hashes[dest_hash]:
                shutil.move(dest_path, Path(folder) / source_hashes[dest_hash])

    # каждый файл, который появляется в исходной папке, но не в месте назначения, скопировать в
    # целевую папку
    for src_hash, file in source_hashes.items():
        if src_hash not in seen:
            shutil.copy(Path(source) / file, Path(dest) / file)






