"""
This script translates problems from the OpenAI HumanEval dataset into Scheme.

The Scheme standard used: R7RS (latest, as of 2026-02-12)

- Compiler: https://www.gnu.org/software/guile/
- Language specification: https://r7rs.org/
- Test library: https://srfi.schemers.org/srfi-64/srfi-64.html
"""

import ast
from typing import List


class Translator:

    USub = "-"

    stop = ["\n(define", "\n;", "\n("]

    def file_ext(self):
        return "scm"

    def translate_prompt(
        self, name: str, args: List[ast.arg], _returns, description: str
    ) -> str:
        scm_preamble = "(import (scheme base))"
        scm_args = " ".join([arg.arg for arg in args])
        scm_description = description.replace('"', '\\"')
        self.entry_point = name
        return f'{scm_preamble}\n(define ({name} {scm_args})\n"{scm_description}"\n'

    def test_suite_prefix_lines(self, entry_point) -> List[str]:
        return [
            '(import (srfi srfi-64))', # test library
            f'(define candidate {entry_point})',
            '(test-begin "HumanEval")'
        ]

    # TODO Delete?
    def test_suite_suffix_lines(self) -> List[str]:
        return ['(test-end)']

    def deep_equality(self, left: str, right: str) -> str:
        return f"(test-equal {left} {right})"

    def gen_literal(self, c: bool | str | int | float):
        if type(c) is bool:
            return "t" if c else "nil"
        elif type(c) is str:
            return f'"{c}"'
        elif c is None:
            return "nil"
        return repr(c)

    def gen_var(self, variable: str) -> str:
        return variable

    def gen_list(self, list: List[str]) -> str:
        return "(list " + " ".join(list) + ")"

    def gen_tuple(self, tuple: List[str]) -> str:
        return "(list " + " ".join(tuple) + ")"

    def gen_dict(self, keys: List[str], values: List[str]) -> str:
        pairs = " ".join(f"(cons {k} {v})" for k, v in zip(keys, values))
        return "(list " + pairs + ")"

    def gen_call(self, func: str, args: List[str]) -> str:
        return "(" + func + " " + " ".join(args) + ")"
