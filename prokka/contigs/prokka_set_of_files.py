import argparse
import itertools
import multiprocessing
import os
import pprint
import re
import subprocess

import pandas as pd

def get_files(dirname):
    fastas =  os.listdir(dirname)
    return [os.path.join(dirname, f) for f in fastas]

def run_prokka(fasta, threads):
    fname = os.path.basename(fasta)
    path_chunks = fname.rstrip('.fa').split('/')
    # remove '' from end
    path_chunks = [p for p in path_chunks if len(p) > 0]
    print(path_chunks)

    dirname = path_chunks[-1]
    print('dirname: {}'.format(dirname))
    # make a dir in this prokka place for the annotations
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    stdout_path =  os.path.join(dirname, 'prokka.out')
    stdout = open(stdout_path, 'w') 
    stderr_path =  os.path.join(dirname, 'prokka.err')
    stderr = open(stderr_path, 'w') 

    label = re.sub('_group[_0-9]+', '', dirname) 
    cmd = ['prokka', fasta, '--force', 'ON', 
            '--locustag', label, '--genus', label, '--species', label, '--strain', 'label', 
            '--outdir', dirname,
            '--metagenome', 'ON', '--cpus', threads]
    print('----- command to run -------')
    command_string = ' '.join([str(s) for s in cmd])
    print('run command:\n{}'.format(command_string))
    subprocess.check_call(cmd, stdout=stdout, stderr=stderr)

    stdout.close()
    stderr.close()

    
def test_call(x):
    #subprocess.call(['echo', 'x', ';', 'echo', x])
    cmd = ['echo', x]
    print(' '.join(cmd))
    subprocess.call(cmd)

def run_all(source_contig_dir, threads_per_prokka):
    # print 
    fastas = os.listdir(source_contig_dir)
    fastas = [os.path.join(source_contig_dir, f) for f in fastas]
    fastas = [os.path.abspath(f) for f in fastas]
    pprint.pprint("fastas found at {}: {}".format(source_contig_dir, fastas))
    count = multiprocessing.cpu_count()
    print('you have {} cpus to work with, and want {} threads per prokka call'.format(
        count, threads_per_prokka))
    processes = min(count // threads_per_prokka, len(fastas))
    print('use {} pool.map processes'.format(processes))

    pool = multiprocessing.Pool(processes=processes)
    #pool.map(test_call, ['a', 'b', 'c'])
    #pool.map(test_call, fastas)
    #pool.map(run_prokka, fastas)
    processes = itertools.repeat(str(processes))
    args = list(zip(fastas, processes))
    pprint.pprint(args)
    pool.starmap(run_prokka, args)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("ref_folder", help="folder containing fastas to annotate with Prokka")
    parser.add_argument("threads_per_run", type=int, help="number of threads for each prokka call")
    args = parser.parse_args()
    if args.ref_folder is None:
        args.print_help()
    else: 
        #print('prepare commands for fasta files in {}'.format(args.ref_folder))
        #prepare_commands(args.ref_folder, args.threads_per_run)
        run_all(args.ref_folder, args.threads_per_run)

