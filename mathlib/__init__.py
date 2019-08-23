import abc
import math
import os
import functools

from . import core
from . import ui
from . import io
from . import utils
from . import tree
from .web import app

from .core import *
from .ui import *
from .io import *
from .utils import *
from .tree import *
from .web.app import *

__all__ = ['math', 'abc', 'os', 'functools']
__all__.extend(core.__all__)
__all__.extend(ui.__all__)
__all__.extend(io.__all__)
__all__.extend(app.__all__)
__all__.extend(tree.__all__)

# default_lexer_grammar = 'mathlib/io/lexer_grammar'
# default_parser_grammar = 'mathlib/io/parser_grammar'
default_lexer_grammar = os.path.join(os.path.dirname(io.__file__), 'lexer_grammar')
default_parser_grammar = os.path.join(os.path.dirname(io.__file__), 'parser_grammar')
