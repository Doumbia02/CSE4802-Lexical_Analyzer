"""
CSE 4802 Compiler Design Lab - Section 1B: Assignment 1
Lexical Analyzer with Token Classification and Statistics
"""

import re
import sys
from collections import defaultdict

# ─────────────────────────────────────────────
#  Token definitions
# ─────────────────────────────────────────────

KEYWORDS = {
    'int', 'float', 'char', 'double', 'long', 'short', 'unsigned', 'signed',
    'void', 'if', 'else', 'while', 'for', 'do', 'return', 'break', 'continue',
    'switch', 'case', 'default', 'struct', 'union', 'typedef', 'enum',
    'const', 'static', 'extern', 'sizeof', 'printf', 'scanf', 'include', 'main'
}

# Multi-char operators must come BEFORE single-char  (Longest Match Rule)
MULTI_CHAR_OPERATORS = [
    ('++', 'INCR_DECR_OP'),
    ('--', 'INCR_DECR_OP'),
    ('+=', 'ASSIGNMENT_OP'),
    ('-=', 'ASSIGNMENT_OP'),
    ('*=', 'ASSIGNMENT_OP'),
    ('/=', 'ASSIGNMENT_OP'),
    ('%=', 'ASSIGNMENT_OP'),
    ('&=', 'ASSIGNMENT_OP'),
    ('|=', 'ASSIGNMENT_OP'),
    ('^=', 'ASSIGNMENT_OP'),
    ('<<=', 'ASSIGNMENT_OP'),
    ('>>=', 'ASSIGNMENT_OP'),
    ('<<', 'BITWISE_OP'),
    ('>>', 'BITWISE_OP'),
    ('==', 'RELATIONAL_OP'),
    ('!=', 'RELATIONAL_OP'),
    ('<=', 'RELATIONAL_OP'),
    ('>=', 'RELATIONAL_OP'),
    ('&&', 'LOGICAL_OP'),
    ('||', 'LOGICAL_OP'),
    ('->', 'ARITHMETIC_OP'),   # pointer member access
]

SINGLE_CHAR_OPERATORS = {
    '+': 'ARITHMETIC_OP',
    '-': 'ARITHMETIC_OP',
    '*': 'ARITHMETIC_OP',
    '/': 'ARITHMETIC_OP',
    '%': 'ARITHMETIC_OP',
    '<': 'RELATIONAL_OP',
    '>': 'RELATIONAL_OP',
    '!': 'LOGICAL_OP',
    '&': 'BITWISE_OP',
    '|': 'BITWISE_OP',
    '^': 'BITWISE_OP',
    '~': 'BITWISE_OP',
    '=': 'ASSIGNMENT_OP',
}

DELIMITERS = set('(){},;[].')

# ─────────────────────────────────────────────
#  Regex patterns
# ─────────────────────────────────────────────

RE_FLOAT     = re.compile(r'^\d+\.\d+([eE][+-]?\d+)?')
RE_INT       = re.compile(r'^\d+')
RE_ID        = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*')
RE_CHAR_LIT  = re.compile(r"^'(\\.|[^\\'])'")
RE_STR_LIT   = re.compile(r'^"(\\.|[^\\"])*"')
RE_INVALID_ID= re.compile(r'^\d+[a-zA-Z_]\w*')   # e.g. 9abc

# ─────────────────────────────────────────────
#  Lexer
# ─────────────────────────────────────────────

class Lexer:
    def __init__(self):
        self.tokens = []          # list of (token_type, lexeme, line)
        self.errors = []          # list of (message, line)
        self.symbol_table = {}    # identifier → {count, first_line}

        # counters
        self.stats = defaultdict(int)

    # ── public entry point ──────────────────
    def tokenize(self, source_code: str):
        lines = source_code.splitlines()
        for line_no, line in enumerate(lines, start=1):
            self._scan_line(line, line_no)
        return self.tokens

    # ── scan one line ───────────────────────
    def _scan_line(self, line: str, line_no: int):
        i = 0
        n = len(line)

        while i < n:
            # Skip whitespace
            if line[i] in ' \t\r':
                i += 1
                continue

            # Skip single-line comments
            if line[i:i+2] == '//':
                break

            remaining = line[i:]

            # ── String literal ───────────────
            m = RE_STR_LIT.match(remaining)
            if m:
                lexeme = m.group()
                self._add_token('STRING_CONST', lexeme, line_no)
                i += len(lexeme)
                continue

            # ── Character literal ────────────
            m = RE_CHAR_LIT.match(remaining)
            if m:
                lexeme = m.group()
                self._add_token('CHAR_CONST', lexeme, line_no)
                i += len(lexeme)
                continue

            # ── Multi-char operators (longest match) ──
            matched = False
            # Sort by length desc so >>= matched before >>
            for op, op_type in sorted(MULTI_CHAR_OPERATORS, key=lambda x: -len(x[0])):
                if remaining.startswith(op):
                    self._add_token(op_type, op, line_no)
                    i += len(op)
                    matched = True
                    break
            if matched:
                continue

            # ── Single-char operator ─────────
            if line[i] in SINGLE_CHAR_OPERATORS:
                self._add_token(SINGLE_CHAR_OPERATORS[line[i]], line[i], line_no)
                i += 1
                continue

            # ── Delimiter ────────────────────
            if line[i] in DELIMITERS:
                self._add_token('DELIMITER', line[i], line_no)
                i += 1
                continue

            # ── Invalid identifier (9abc) ────
            m = RE_INVALID_ID.match(remaining)
            if m:
                lexeme = m.group()
                self.errors.append((f"Invalid identifier: '{lexeme}'", line_no))
                i += len(lexeme)
                continue

            # ── Float constant ───────────────
            m = RE_FLOAT.match(remaining)
            if m:
                lexeme = m.group()
                self._add_token('FLOAT_CONST', lexeme, line_no)
                i += len(lexeme)
                continue

            # ── Integer constant ─────────────
            m = RE_INT.match(remaining)
            if m:
                lexeme = m.group()
                self._add_token('INTEGER_CONST', lexeme, line_no)
                i += len(lexeme)
                continue

            # ── Identifier or keyword ────────
            m = RE_ID.match(remaining)
            if m:
                lexeme = m.group()
                if lexeme in KEYWORDS:
                    self._add_token('KEYWORD', lexeme, line_no)
                else:
                    self._add_token('IDENTIFIER', lexeme, line_no)
                    # Symbol table
                    if lexeme not in self.symbol_table:
                        self.symbol_table[lexeme] = {'count': 0, 'first_line': line_no}
                    self.symbol_table[lexeme]['count'] += 1
                i += len(lexeme)
                continue

            # ── Unknown character ────────────
            self.errors.append((f"Unknown symbol: '{line[i]}'", line_no))
            i += 1

    # ── helper ──────────────────────────────
    def _add_token(self, token_type: str, lexeme: str, line_no: int):
        self.tokens.append((token_type, lexeme, line_no))
        self.stats[token_type] += 1

    # ── statistics ──────────────────────────
    def get_statistics(self):
        s = self.stats
        total = sum(s.values())
        keywords     = s['KEYWORD']
        identifiers  = s['IDENTIFIER']
        int_const    = s['INTEGER_CONST']
        float_const  = s['FLOAT_CONST']
        char_const   = s['CHAR_CONST']
        str_const    = s['STRING_CONST']
        constants    = int_const + float_const + char_const + str_const
        arith        = s['ARITHMETIC_OP']
        relat        = s['RELATIONAL_OP']
        logical      = s['LOGICAL_OP']
        bitwise      = s['BITWISE_OP']
        assign       = s['ASSIGNMENT_OP']
        incr_decr    = s['INCR_DECR_OP']
        operators    = arith + relat + logical + bitwise + assign + incr_decr
        delimiters   = s['DELIMITER']

        return {
            'Total Tokens':                 total,
            'Keywords':                     keywords,
            'Identifiers':                  identifiers,
            'Constants':                    constants,
            'Integer Constants':            int_const,
            'Float Constants':              float_const,
            'Character Constants':          char_const,
            'String Constants':             str_const,
            'Operators':                    operators,
            'Arithmetic Operators':         arith,
            'Relational Operators':         relat,
            'Logical Operators':            logical,
            'Bitwise Operators':            bitwise,
            'Assignment Operators':         assign,
            'Increment/Decrement Operators':incr_decr,
            'Delimiters':                   delimiters,
        }

# ─────────────────────────────────────────────
#  Pretty printers
# ─────────────────────────────────────────────

def print_token_stream(tokens):
    print("\n" + "="*55)
    print("  TOKEN STREAM")
    print("="*55)
    for tok_type, lexeme, line_no in tokens:
        print(f"  <{tok_type}, {lexeme}>   [line {line_no}]")

def print_statistics(stats):
    print("\n" + "="*55)
    print("  TOKEN STATISTICS")
    print("="*55)
    for label, value in stats.items():
        print(f"  {label:<38} : {value}")

def print_symbol_table(symbol_table):
    print("\n" + "="*55)
    print("  SYMBOL TABLE")
    print("="*55)
    print(f"  {'Identifier':<20} {'Count':>6}   {'First Line':>10}")
    print("  " + "-"*40)
    for ident, info in sorted(symbol_table.items()):
        print(f"  {ident:<20} {info['count']:>6}   {info['first_line']:>10}")

def print_errors(errors):
    if errors:
        print("\n" + "="*55)
        print("  LEXICAL ERRORS")
        print("="*55)
        for msg, line_no in errors:
            print(f"  [Line {line_no}] ERROR: {msg}")

# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            with open(sys.argv[1], 'r') as f:
                source = f.read()
        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(1)
    else:
        print("No input file provided. Using built-in sample input.\n")
        source = SAMPLE_INPUT

    print("SOURCE CODE:")
    print("-" * 55)
    print(source)

    lexer = Lexer()
    tokens = lexer.tokenize(source)

    print_token_stream(tokens)
    print_statistics(lexer.get_statistics())
    print_symbol_table(lexer.symbol_table)
    print_errors(lexer.errors)

    print("\n" + "="*55)
    print("  Lexical analysis complete.")
    print("="*55)