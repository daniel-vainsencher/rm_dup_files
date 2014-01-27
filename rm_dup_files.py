import os
from os import path
import functools
from itertools import zip_longest


def read_file_blocks(f):
    for block in iter(functools.partial(f.read, 8192), b''):
        yield block


def files_identical(first_name, second_name):
    with open(first_name, mode='rb') as f_a:
        with open(second_name, mode='rb') as f_b:
            for buf1, buf2 in zip_longest(read_file_blocks(f_a), read_file_blocks(f_b)):
                if buf1 != buf2:
                    return False

    return True


def to_utf(a):
    return ''.join(['0x'+hex(ord(x))[2:] if ord(x) > 127 else x for x in a])


def remove_duplicate_files(to_decimate, baseline):
    for (dir_path, dir_names, file_names) in os.walk(to_decimate):
        print('Entering dir {} '.format(to_utf(dir_path)))
        rel_path = path.relpath(dir_path, to_decimate)

        # if a directory is not in the baseline, ensure walk will not enter it.
        for a in dir_names:
            print('Checking existence of {} '.format(to_utf(a)))
            target_dir = path.join(baseline, rel_path, a)
            if not os.path.exists(target_dir):
                dir_names.remove(a)

        for fn in file_names:
            print('Testing filename {} '.format(to_utf(fn)))
            source_file_name = path.join(to_decimate, rel_path, fn)
            target_file_name = path.join(baseline, rel_path, fn)
            if os.path.exists(target_file_name):
                source_stat = os.stat(source_file_name)
                target_stat = os.stat(target_file_name)
                if source_stat.st_size != target_stat.st_size:
                    print('{} differently sized than corresponding target.'.format(to_utf(source_file_name)))
                    # should check other stats, but not now
                elif not files_identical(source_file_name, target_file_name):
                    print('{} differs in content from corresponding target.'.format(to_utf(source_file_name)))
                else:
                    print('{} is identical to corresponding target, removing.'.format(to_utf(source_file_name)))
                    os.remove(source_file_name)

        if not os.listdir(dir_path):
            print('{} is empty, removing.'.format(to_utf(dir_path)))
            os.rmdir(dir_path)