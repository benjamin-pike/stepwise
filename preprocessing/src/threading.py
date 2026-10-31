import os

os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

import multiprocessing as mp
from tqdm.contrib.concurrent import process_map, thread_map

mp.set_start_method('fork', force = True)


def _call(func_and_args):
    func, args = func_and_args

    return func(*args)


def parallelize(func, *iterables, max_workers = None, chunksize = 1, use_threads = False):
    arg_tuples = [(func, args) for args in zip(*iterables)]
    mapper = thread_map if use_threads else process_map

    return mapper(
        _call, arg_tuples, desc = 'Processing', max_workers = max_workers, chunksize = chunksize, disable = False
    )
