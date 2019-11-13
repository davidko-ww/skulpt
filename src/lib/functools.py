def partial(func, *args, **kwargs):
    def newfunc(*fargs, **fkwargs):
        kwargs.update(fkwargs)
        return func(*(args + fargs), **kwargs)
    return newfunc
    
