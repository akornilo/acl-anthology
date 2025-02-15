#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2019 Matt Post <post@cs.jhu.edu>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Uploads PDFs and other files to their correct place on aclweb.org.

Usage:

  [not yet implemented]
  upload_files.py [directory]

will upload all files in the directory to the correct place on the server,
under the assumption they all go to the same folder.

  upload_files.py [file1 [file2 [etc]]]

will upload individual files to their correct place on the server,
where each file may have a different target directory.

"""

import argparse
import os
import re
import subprocess
import sys


from anthology.utils import deconstruct_anthology_id


# Name for the SSH alias in ~/.ssh/config.
SSH_CONFIG_TARGET = 'aclweb'

# The root directory for files, currently containing pdf/ and attachments/
ACLWEB_FILE_ROOT = '/home3/aclwebor/anthology-files'


def upload_file(filepath: str):
    """
    Uploads regular PDFs or attachments to their correct place on the aclweb server.
    """

    relative_dest_path = ''

    os.chmod(filepath, 0o644)

    filename = os.path.basename(filepath)
    fileparts = filename.split('.')
    if len(fileparts) == 2:
        # e.g., P19-1001.pdf
        collection_id, volume_id, _ = deconstruct_anthology_id(fileparts[0])
        collection = collection_id[0]
        relative_dest_path = f'pdf/{collection}/{collection_id}/{filename}'

    elif len(fileparts) == 3:
        # e.g., P19-1001.Attachment.pdf
        collection_id, volume_id, _ = deconstruct_anthology_id(fileparts[0])
        relative_dest_path = f'attachments/{collection}/{collection_id}/{filename}'

    command = f'scp -q {filepath} aclweb:{ACLWEB_FILE_ROOT}/{relative_dest_path}'

    attempts = 1
    retcode = 1
    while attempts <= 3 and retcode != 0:
        # This fails sometimes for no reason, so try a couple of times
        retcode = subprocess.call(command, shell=True)
        if attempts > 1:
            print(f'-> Failed for some reason, attempt #{attempts}', file=sys.stderr)
        print(f'{command} -> {retcode}', file=sys.stderr)
        attempts += 1


def main(args):
    for file in args.files:
        upload_file(file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()

    main(args)
