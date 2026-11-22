"""Spawn works on Windows and Linux; the parent imposes a wall-clock deadline."""
import multiprocessing as mp
import logging
import os
import sys
import time


LOG = logging.getLogger(__name__)
PACKAGE = os.path.dirname(__file__) + os.sep


def _profile(frame, event, arg):
    if event == "call" and frame.f_code.co_filename.startswith(PACKAGE):
        LOG.debug("Hívás: %s.%s", frame.f_globals.get("__name__"), frame.f_code.co_name)


def enable_debug():
    sys.setprofile(_profile)


def _entry(pipe, function, args, logfile, debug):
    if logfile:
        logging.basicConfig(filename=logfile, level=logging.DEBUG if debug else logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s", encoding="utf-8")
    if debug:
        enable_debug()
    try:
        pipe.send((True, function(*args)))
    except Exception as error:
        # Do not transmit raw exception text: it can contain SQL or credentials.
        pipe.send((False, type(error).__name__))
    finally:
        pipe.close()


def bounded(function, args, seconds, *, logfile=None, debug=False):
    context = mp.get_context("spawn")
    reader, writer = context.Pipe(duplex=False)
    process = context.Process(target=_entry, args=(writer, function, args, logfile, debug))
    deadline = time.monotonic() + seconds
    process.start()
    writer.close()
    try:
        if not reader.poll(max(0, deadline - time.monotonic())):
            raise TimeoutError("A művelet túllépte az időkorlátot.")
        try:
            ok, value = reader.recv()
        except EOFError as error:
            raise RuntimeError("A munkafolyamat megszakadt.") from error
        if not ok:
            raise RuntimeError(f"Munkafolyamat-hiba: {value}")
        return value
    finally:
        reader.close()
        process.join(timeout=0.1)
        if process.is_alive():
            process.terminate()
            process.join(timeout=1)
        if process.is_alive():
            process.kill()
            process.join(timeout=1)
