import argparse
from datetime import datetime
from functools import partial
import logging
import multiprocessing
from pathlib import Path
import secrets
import sys
import time

from . import __version__, database, feedback, grading, inputs, output
from .config import load
from .runtime import bounded, configure_cli_output, enable_debug

LOG = logging.getLogger(__name__)


def main(argv=None):
    parser = argparse.ArgumentParser(description="SQL feladatsorok javítása tanári javítókulccsal")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("folder", type=Path, help="A solution.sql és a hallgatói .sql fájlok mappája")
    parser.add_argument("--config", type=Path, default=Path("config.json"))
    parser.add_argument("--output", type=Path, default=Path("eredmenyek"))
    parser.add_argument("-d", "--debug", action="store_true", help="Részletes függvényhívás-napló")
    parser.add_argument("--ai", action="store_true", help="Hiteles visszajelzés és külön helyi AI-javaslat tanári ellenőrzésre")
    parser.add_argument("--spec-output", action="store_true",
                        help="A specifikáció szerinti tabulátoros XLS-összesítő")
    args = parser.parse_args(argv)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    directory = args.output.resolve() / stamp
    base = Path(__file__).resolve().parent.parent
    try:
        directory.mkdir(parents=True, exist_ok=False)
        logdir = base / "logs"
        logdir.mkdir(exist_ok=True)
        logfile = logdir / (stamp + ".log")
        logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                            format="%(asctime)s %(levelname)s %(message)s",
                            handlers=[logging.FileHandler(logfile, encoding="utf-8"), logging.StreamHandler()])
        worker = partial(bounded, logfile=logfile, debug=args.debug)
        if args.debug:
            enable_debug()
    except OSError as error:
        print(f"Nem hozható létre a futási vagy naplómappa: {error}", file=sys.stderr)
        return 2
    LOG.info("Program indul | bemenet=%s config=%s kimenet=%s debug=%s ai=%s",
             args.folder, args.config, directory, args.debug, args.ai)
    exit_code = 2
    try:
        config = load(args.config)
        database.validate_configuration(config)
        folder = args.folder.resolve()
        tasks, pregen, cases, excluded = inputs.key(folder, config.max_input_bytes)
        paths = sorted(path for path in folder.iterdir() if path.is_file()
                       and path.suffix.casefold() == ".sql" and path.name.casefold() not in excluded)
        if not paths:
            raise ValueError("Nincs feldolgozható hallgatói .sql fájl.")
        try:
            info = worker(database.check, (config,), config.connect_seconds + 5)
        except (TimeoutError, RuntimeError):
            raise ValueError("Nem sikerült az adatbázis-kapcsolat ellenőrzése; ellenőrizd a szolgáltatást és a konfigurációt.") from None
        LOG.info("Adatbázis: %s | %s", config.engine, info)
        reports, seen = [], set()
        incomplete = False
        deadline = time.monotonic() + config.batch_seconds
        for path in paths:
            if time.monotonic() >= deadline:
                LOG.error("A munkamenet időkorlátja lejárt; maradt feldolgozatlan beadás.")
                incomplete = True
                break
            LOG.info("Beadás indul: %s", path.name)
            try:
                name, neptun, answers = inputs.submission(path, {task.id for task in tasks}, config.max_input_bytes)
                if neptun in seen:
                    raise ValueError("Ismétlődő Neptun-kód; a második fájl nem pontozható automatikusan.")
            except (OSError, ValueError) as error:
                LOG.error("Bemeneti hiba | %s: %s", path.name, error)
                incomplete = True
                continue
            seen.add(neptun)
            results = []
            for task in tasks:
                tokens = [(secrets.token_hex(8), secrets.token_hex(8)) for _ in cases]
                started = False
                try:
                    remaining = min(config.task_seconds, deadline - time.monotonic())
                    if remaining <= 0:
                        raise TimeoutError()
                    started = True
                    result = worker(grading.grade_task,
                                     (config, task, answers.get(task.id), pregen, cases, tokens), remaining)
                except (TimeoutError, RuntimeError) as error:
                    LOG.error("Feladat %s | munkafolyamat: %s", task.id, type(error).__name__)
                    result = grading.base_result(task)
                    if started and database.needs_timeout_cleanup(config):
                        pending = [token for pair in tokens for token in pair]
                        try:
                            worker(database.cleanup, (config, pending), config.connect_seconds + 5)
                        except (TimeoutError, RuntimeError):
                            labels = database.cleanup_labels(config, pending)
                            LOG.error("Adatbázis-takarítás kézi ellenőrzést igényel (%s): %s",
                                      config.engine, ", ".join(labels) or "nincs objektumlista")
                results.append(result)
                LOG.info("Feladat %s: %s", task.id, result["status"])
            report = grading.report(name, neptun, results)
            destination = output.individual(directory, report)
            reports.append(report)
            incomplete |= report["points"] is None
            LOG.info("Beadás vége: %s | %s/%s | %s", path.name,
                     output.point_label(report["points"]), report["maximum"], destination)
        summary = output.summary(directory, reports, tasks, spec_output=args.spec_output)
        excel = "" if args.spec_output else f"Excel-összesítő: {summary.with_suffix('.xlsx')}\n"
        print(f"Eredmények: {directory}\nÖsszesítő: {summary}\n{excel}Napló: {logfile}", flush=True)
        exit_code = 2 if incomplete else 0
        if args.ai and reports:
            feedback.fill(directory, reports, config, worker=worker)
    except KeyboardInterrupt:
        LOG.warning("Megszakítva; a mentett pontlapok és AI-javaslatok megmaradtak.")
        exit_code = 130
    except (ValueError, OSError) as error:
        exit_code = 2
        LOG.error("%s", error)
    finally:
        LOG.info("Program vége | kilépési kód: %s", exit_code)
        if args.debug:
            sys.setprofile(None)
    return exit_code


if __name__ == "__main__":
    multiprocessing.freeze_support()
    configure_cli_output()
    raise SystemExit(main())
