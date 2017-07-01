def recursive_set_with_slice(base, grid, i):
    for gkey in grid:
        if type(base[gkey]) is dict:
            base[gkey] = recursive_set_with_slice(base[gkey], grid[gkey], i)
        else:
            base[gkey] = grid[gkey][i]
    return base

def chainer_random_search(base_config, trials_config, N):
    title = base_config['title'][:]
    for i in range(N):
        config = recursive_set_with_slice(base_config, trials_config, i)
        config['title'] = title+' hp[{}]'.format(i)
        print 'Experiment {} config: {}'.format(i, config)
        run_experiment(config, '101693')
    print "All Done"
