from prettytable import PrettyTable

from .common import *
from .. import colors
from ..local_file import LocalFile


def process_add(file_type, solution_type, files):
    if not load_session():
        fatal('No session known. Use relogin or init first.')
    real_file_type = file_type
    if file_type in ['checker', 'validator', 'interactor']:
        if len(files) != 1:
            fatal('can''t set several ' + file_type + 's')
        file_type = 'source'
    if solution_type is not None:
        if file_type != 'solution':
            fatal('solution type can be set only on solutions')
        if solution_type == 'MAIN':
            solution_type = 'MA'
    table = PrettyTable(['File type', 'Polygon name', 'Local path', 'Status'])
    for filename in files:
        local = global_vars.problem.get_local_by_filename(os.path.basename(filename))
        if local is not None:
            print('file %s already added, use commit instead' % os.path.basename(filename))
            status = colors.warning('Already added')
        else:
            local = LocalFile(os.path.basename(filename),
                              os.path.dirname(filename),
                              str(os.path.basename(filename).split('.')[0]),
                              file_type
                              )
            if solution_type is not None:
                local.tag = solution_type
            if local.upload():
                status = colors.success('Uploaded')
                global_vars.problem.local_files.append(local)
                if real_file_type != file_type:
                    global_vars.problem.set_utility_file(local.polygon_filename, real_file_type)
            else:
                status = colors.error('Error')
        table.add_row([local.type, local.polygon_filename, local.filename, status])
    print(table)
    save_session()


def add_parser(subparsers):
    parser_add = subparsers.add_parser(
            'add',
            help="Upload files to polygon"
    )
    parser_add.add_argument('file_type', choices=['solution', 'resource', 'source', 'checker', 'validator', 'interactor'],
                            help='Type of file to add')
    parser_add.add_argument('-t', dest='solution_type',
                            choices=['MAIN', 'OK', 'RJ', 'TL', 'WA', 'PE', 'ML', 'RE', 'TO'],
                            help='Solution type')
    parser_add.add_argument('file', nargs='+', help='List of files to add')
    parser_add.set_defaults(func=lambda options: process_add(options.file_type, options.solution_type, options.file))
