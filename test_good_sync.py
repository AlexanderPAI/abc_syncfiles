import shutil
import tempfile
from pathlib import Path

from good_sync import sync, determine_actions


def test_when_a_file_exists_in_the_source_not_the_destination():
    src_hashes = {'hash1': 'fn1'}
    dest_hashes = {}

    actions = determine_actions(src_hashes, dest_hashes, Path('/src'), Path('/dest'))
    assert list(actions) == [('copy', Path('/src/fn1'), Path('/dest/fn1'))]


def test_when_a_file_has_been_renamed_in_the_source():
    src_hashes = {'hash1': 'fn1'}
    dest_hashes = {'hash1': 'fn2'}

    actions = determine_actions(src_hashes, dest_hashes, Path('/src'), Path('/dest'))
    assert list(actions) == [('move', Path('/dest/fn2'), Path('/dest/fn1'))]