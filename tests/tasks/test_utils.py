# -*- coding: utf-8 -*-
from tasks.utils import download_file
import os
from os.path import abspath, exists
import hashlib


def test_download_file():
    actual_local_filepath = None
    try:
        requested_local_filepath = 'icon.png'
        actual_local_filepath = download_file(
            url='https://github.com/WildMeOrg/houston/raw/main/app/static/images/icon.png',
            local_filepath=requested_local_filepath,
        )
        assert abspath(requested_local_filepath) == abspath(actual_local_filepath)

        with open(actual_local_filepath, 'rb') as file:
            data = file.read()
        hexdigest = hashlib.md5(data).hexdigest()
        assert hexdigest in [
            'b14755cf4d745b614726b86bdd066b03',
        ]
    except Exception as ex:
        raise ex
    finally:
        actual_local_filepath = abspath(actual_local_filepath)
        if actual_local_filepath is not None and exists(actual_local_filepath):
            os.remove(actual_local_filepath)
