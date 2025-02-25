import os
import sys
import logging
import logging.handlers
import multiprocessing
import traceback as tb
import datetime
import shutil

# Heavily inspired by https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
# with the help of
# https://stackoverflow.com/questions/48045978/how-to-log-to-single-file-with-multiprocessing-pool-apply-async

# Because you'll want to define the logging configurations for listener and workers, the
# listener and worker process functions take a configurer parameter which is a callable
# for configuring logging for that process. These functions are also passed to the queue,
# which they use for communication.
#
# In practice, you can configure the listener however you want


def listener_configurer(logfile, loglevel):
    root = logging.getLogger()
    if root.hasHandlers():
        root.handlers.clear()
    file_handler = logging.FileHandler(logfile, "a")
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s")
    file_handler.setFormatter(formatter)
    formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
    console_handler.setFormatter(formatter)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    root.setLevel(loglevel)


# This is the listener process top-level loop: wait for logging events
# (LogRecords)on the queue and handle them, quit when you get a None for a
# LogRecord.
def listener_process(queue, configurer, logfile, loglevel):
    try:
        configurer(logfile, loglevel)

        while True:
            record = queue.get()
            if record is None:
                break  # We send this as a sentinel to tell the listener to quit.
            logger = logging.getLogger(record.name)
            # logger.propagate = True
            logger.handle(record)  # No level or filter logic applied - just do it!
    except Exception:
        exc_type, exc_value, exc_tb = sys.exc_info()
        tbe = tb.TracebackException(
            exc_type,
            exc_value,
            exc_tb,
        )
        print("LOGGING ERROR: " + str.join("", tbe.format()), file=sys.stderr)


# The worker configuration is done at the start of the worker process run.
# Each process will run the logging configuration code when it starts.
def worker_configurer(queue, loglevel):
    h = logging.handlers.QueueHandler(queue)  # Just the one handler needed
    root = logging.getLogger()
    if root.hasHandlers():
        root.handlers.clear()
    root.addHandler(h)
    root.setLevel(loglevel)
    # root.propagate = True


# Example worker process with arguments comandline-args, list of todos to parallelize, what to execute in parallel
def worker(args, todolist, whattodo):

    #  Logging configuration
    SCRIPTNAME = "Example_worker"
    logdir = args.logdir
    logfile = str.join(os.sep, [os.path.abspath(logdir), SCRIPTNAME + ".log"])

    makelogdir(logdir)
    makelogfile(logfile)

    #  Multiprocessing with spawn
    nthreads = args.cores or 2
    multiprocessing.set_start_method("spawn")  # set multiprocessing start method to safe spawn
    pool = multiprocessing.Pool(processes=nthreads, maxtasksperchild=1)

    queue = multiprocessing.Manager().Queue(-1)
    listener = multiprocessing.Process(
        target=listener_process,
        args=(queue, listener_configurer, logfile, args.loglevel),
    )
    listener.start()

    worker_configurer(queue, args.loglevel)

    # log.info(logid+'Running '+SCRIPTNAME+' on '+str(args.cores)+' cores.')
    # log.info(logid+'CLI: '+sys.argv[0]+' '+'{}'.format(' '.join( [shlex.quote(s) for s in sys.argv[1:]] )))

    for todo in todolist:
        pool.apply_async(whattodo, args=(queue, worker_configurer, args.loglevel, todo, args))
    pool.close()
    pool.join()
    queue.put_nowait(None)
    listener.join()


def checklog():
    test = logging.getLogger()
    if not (test.hasHandlers()):
        return False
    else:
        if not len(test.handlers) > 1:
            return False
        else:
            return True


def makelogdir(logdir):
    if not os.path.isabs(logdir):
        logdir = os.path.abspath(logdir)
    if not os.path.exists(logdir):
        try:
            os.makedirs(logdir)
        except OSError:
            # If directory has already been created or is inaccessible
            if not os.path.exists(logdir):
                sys.exit("Problem creating directory " + logdir)


def makelogfile(logfile):
    if not os.path.isfile(os.path.abspath(logfile)) or os.stat(logfile).st_size == 0:
        open(logfile, "a").close()
    else:
        ts = str(
            datetime.datetime.fromtimestamp(os.path.getmtime(os.path.abspath(logfile))).strftime("%Y%m%d_%H_%M_%S_%f")
        )
        shutil.move(logfile, logfile.replace(".log", "") + "_" + ts + ".log")


def setup_logger(name, log_file, filemode="a", logformat=None, datefmt=None, level="WARNING"):
    """Function setup as many loggers as you want"""

    log = logging.getLogger(name)
    if log_file != "stderr":
        handler = logging.FileHandler(log_file, mode=filemode)
    else:
        handler = logging.StreamHandler(sys.stderr)

    handler.setFormatter(logging.Formatter(fmt=logformat, datefmt=datefmt))

    log.setLevel(level)
    log.addHandler(handler)

    return log


# logger.py ends here
