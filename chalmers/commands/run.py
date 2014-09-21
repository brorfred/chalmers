'''
'''
from __future__ import unicode_literals, print_function

import logging
from os import path
import os

from chalmers import errors
from chalmers.config import dirs
from chalmers.program import Program


log = logging.getLogger('chalmers.add')

def main(args):

    program_dir = path.join(dirs.user_data_dir, 'programs')
    if not args.name:
        args.name = args.command[0]

    if not path.isdir(program_dir):
        os.makedirs(program_dir)

    program_defn = path.join(program_dir, '{args.name}.yaml'.format(args=args))
    if path.isfile(program_defn):
        raise errors.ChalmersError("Program with name '{args.name}' already exists.  \n"
                                   "Use the -n/--name option to change the name or \n"
                                   "Run 'chalmers remove {args.name}' to remove it \n"
                                   "or 'chalmers set' to update the parameters".format(args=args))

    stdout = args.stdout or path.join(dirs.user_log_dir, '{args.name}.stdout.log'.format(args=args))
    daemon_log = args.daemon_log or path.join(dirs.user_log_dir, '{args.name}.daemon.log'.format(args=args))

    if args.redirect_stderr:
        stderr = None
    else:
        stderr = args.stderr or path.join(dirs.user_log_dir, '{args.name}.stderr.log'.format(args=args))

    definition = {
                    'name': args.name,
                    'command': args.command,
                    'stdout': stdout,
                    'stderr': stderr,
                    'daemon_log': daemon_log,
                    'redirect_stderr': args.redirect_stderr
                    }

    state = {'paused': args.paused}

    prog = Program.create(args.name, definition, state)
    prog.save_state()

    if not args.paused:
        log.info('Starting program {args.name}'.format(args=args))
        prog.start(daemon=args.daemon)


    if args.daemon:
        prog.save()
        log.info('Added program {args.name}'.format(args=args))
    else:
        log.info('Program {args.name} exited'.format(args=args))


def add_parser(subparsers):
    parser = subparsers.add_parser('run',
                                      help='Manage a command to run',
                                      description=__doc__)
    #===============================================================================
    #
    #===============================================================================
    group = parser.add_argument_group('Starting State') \
                  .add_mutually_exclusive_group()

    group.add_argument('--start', action='store_false', dest='paused', default=False,
                       help="Start program automatically (default)")
    group.add_argument('--paused', action='store_true', dest='paused',
                       help="don't start program automatically")

    group.add_argument('--daemon', action='store_true', default=True,
                       help="Run command in the background")
    group.add_argument('-w', '--wait', '--no-daemon', action='store_false', dest='daemon',
                       help="Run command in the foreground")
    #===========================================================================
    #
    #===========================================================================
    group = parser.add_argument_group('Process Output:')
    group.add_argument('--stdout')
    group.add_argument('--stderr')
    group.add_argument('--daemon-log')
    group.add_argument('--redirect-stderr', action='store_true')
    #===========================================================================
    #
    #===========================================================================
    parser.add_argument('-n', '--name')
    parser.add_argument('command', nargs='+', metavar='COMMAND')
    parser.set_defaults(main=main, state='pause')
