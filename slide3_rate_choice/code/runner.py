import sys, os, time, matplotlib; matplotlib.use('Agg')
os.chdir(sys.argv[1])
QUIET = True
_t=time.time()
exec(compile(open(sys.argv[2],encoding='utf-8').read(), 'run_model.py', 'exec'))
print('done in', time.time()-_t)
