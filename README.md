# dask-scheduler-performance


Scripts to track time where Dask scheduler is spending time

```
# To display the perf.data header info, please use --header/--header-only options.
#
#
# Total Lost Samples: 0
#
# Samples: 42K of event 'cycles'
# Event count (approx.): 35393776560
#
# Overhead  Command         Shared Object                                     Symbol
# ........  ..............  ................................................  ...................................................
#
    20.46%  dask-scheduler  python3.8                                         [.] _PyEval_EvalFrameDefault
     6.24%  dask-scheduler  python3.8                                         [.] PyObject_GetAttr
     2.99%  dask-scheduler  python3.8                                         [.] _PyObject_GetMethod
     2.56%  dask-scheduler  python3.8                                         [.] _PyFunction_Vectorcall
     2.55%  dask-scheduler  python3.8                                         [.] member_get
     2.53%  dask-scheduler  python3.8                                         [.] lookdict_unicode_nodummy
     2.06%  dask-scheduler  python3.8                                         [.] _PyEval_EvalCodeWithName
     2.03%  dask-scheduler  [kernel.kallsyms]                                 [k] do_syscall_64
     1.97%  dask-scheduler  python3.8                                         [.] collect.constprop.434
```
