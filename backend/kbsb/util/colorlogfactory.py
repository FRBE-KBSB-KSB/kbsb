# copyright Ruben Decrop 2012 - 2015
# copyright Chessdevil Consulting BVBA 2015 - 2020

import colorlog

def cf(**kwargs):
    return colorlog.ColoredFormatter(
        fmt=kwargs['format'],
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_blue',
        },
        reset=True,
        style='%'        
    )