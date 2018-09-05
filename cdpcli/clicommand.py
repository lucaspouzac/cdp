import subprocess, threading
import logging, verboselogs
import timeit

LOG = verboselogs.VerboseLogger('clicommand')
LOG.addHandler(logging.StreamHandler())
LOG.setLevel(logging.INFO)

class CLICommand(object):

    def __init__(self, dry_run = 1):
        self._dry_run = dry_run
        LOG.verbose('Dry-run init %s' % self._dry_run)

    def run_command(self, command, dry_run = None, timeout = None):
        LOG.info('')
        LOG.info('******************** Run command ********************')
        LOG.info(command)
        return self.run(command, dry_run, timeout)

    def run(self, command, dry_run = None, timeout = None):
        start = timeit.default_timer()
        self._process = None
        self._output = []

        if dry_run is None:
            self._real_dry_run = self._dry_run
        else:
            self._real_dry_run = dry_run

        def target():
            LOG.info('---------- Output ----------')
            # If dry-run option, no execute command
            if not self._real_dry_run:
                self._process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
                while True:
                    line = self._process.stdout.readline()
                    if line.strip() == '' and self._process.poll() is not None:
                        break
                    if line:
                        self._output.append(line.strip())
                        LOG.info(line)

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout if timeout is None else float(timeout))

        if thread.is_alive():
            self._process.terminate()
            thread.join()

        LOG.info('---------- Time: %s s' % (round(timeit.default_timer() - start, 3)))
        if self._process is not None and self._process.returncode != 0:
            LOG.warning('---------- ERROR ----------')
            raise ValueError()

        LOG.info('')

        return self._output
