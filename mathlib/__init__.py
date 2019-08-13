import math
from . import core
from . import ui
from . import io
from . import utils
from .web import app

from .core import *
from .ui import *
from .io import *
from .utils import *
from .web.app import *

__all__ = ['math']
__all__.extend(core.__all__)
__all__.extend(ui.__all__)
__all__.extend(io.__all__)
__all__.extend(app.__all__)

default_lexer_grammar = 'mathlib/io/lexer_grammar'
default_parser_grammar = 'mathlib/io/parser_grammar'
