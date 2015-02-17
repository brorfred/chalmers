import sys
from chalmers.program import Program
import logging
from clyent.logs import setup_logging
from chalmers import config
from argparse import ArgumentParser
logger = logging.getLogger('chalmers')
cli_logger = logging.getLogger('cli-logger')

def main():

    parser = ArgumentParser()
    parser.add_argument('--root', help='chalmers root config directory')
    args = parser.parse_args()

    if args.root:
        config.set_relative_dirs(args.root)


    logfile = config.main_logfile()
    setup_logging(logger, logging.INFO, use_color=False, logfile=logfile, show_tb=True)
    name = sys.argv[1]
    cli_logger.error("Starting program: %s" % name)
    prog = Program(name)
    prog.start_sync()

if __name__ == '__main__':
    main()
