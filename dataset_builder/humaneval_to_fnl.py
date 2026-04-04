"""
This script translates problems from the OpenAI HumanEval dataset into Fennel.

- Home: https://fennel-lang.org/
- Compiler: https://git.sr.ht/~technomancy/fennel
- Test library: https://git.sr.ht/~technomancy/faith
"""

import ast
from typing import List


class Translator:

    USub = "-"

    stop = ["\n(fn", "\n;", "\n("]

    def file_ext(self):
        return "fnl"

    def translate_prompt(
        self, name: str, args: List[ast.arg], _returns, description: str
    ) -> str:
        self.entry_point = name
        fnl_args = " ".join(arg.arg for arg in args)
        fnl_description = description.replace('"', '\\"')
        ref = """\
;; Generate in Fennel.
;;
;; Fennel compiles to Lua. All function calls are Lua functions.
;;
;; (fn add [a b] (+ a b)) ;; named function
;; (fn [a b] (+ a b)) ;; anonymous function
;; (lambda greet [x] (.. "hi " x)) ;; named, errors if x is nil
;; (lambda [x] (+ x 1)) ;; anonymous, errors if x is nil
;; (partial add 1) ;; partial application
;; (hashfn (+ $1 $2)) ;; shorthand anonymous function
;; #(+ $1 $2) ;; same as hashfn
;; (let [x 1 y (+ x 1)] y) ;; scoped bindings
;; (local name "fennel") ;; constant
;; (var i 0) ;; mutable variable
;; (set i (+ i 1)) ;; mutate var
;; (tset tbl :key "value") ;; set table field
;; (set (. tbl :key) "value") ;; same as tset
;; (if (> x 0) x) ;; one branch, nil otherwise
;; (if (> x 0) "pos" "non-pos") ;; two branches
;; (if (= x 1) "one" (= x 2) "two" "other") ;; three branches
;; (when (> x 0) (print x)) ;; side-effecting, no else
;; (do (local x 1) (+ x 2)) ;; block, returns last value
;; (for [i 1 10] (print i)) ;; numeric loop
;; (each [k v (pairs tbl)] (print k v)) ;; side-effecting iteration, also ipairs
;; (while (> n 0) (set n (- n 1))) ;; while loop
;; (collect [k v (pairs tbl)] (values k (+ v 1))) ;; table comprehension, nil filtered
;; (icollect [_ v (ipairs tbl)] (* v 2)) ;; sequential comprehension, nil filtered
;; (fcollect [i 1 5] (* i i)) ;; range comprehension, nil filtered
;; (accumulate [sum 0 _ v (ipairs tbl)] (+ sum v)) ;; fold
;; (faccumulate [sum 0 i 1 10] (+ sum i)) ;; range fold
;; (case x 0 "zero" 1 "one" _ "other") ;; pattern matching
;; (match x 0 "zero" 1 "one" _ "other") ;; like case, also matches locals
;; (values a b c) ;; multiple return values
;; (pick-values 2 (f)) ;; take first n values
;; (. tbl :key) ;; table lookup
;; (?. tbl :key :nested) ;; nil-safe lookup
;; (: str :sub 1 3) ;; method call, str:sub(1,3) in Lua
;; (.. "hello" " " "world") ;; string concatenation
;; (length tbl) ;; # operator
;; (doto [] (table.insert 1) (table.insert 2)) ;; insert as first arg, return value
;; (with-open [f (io.open "x")] (f:read "*a")) ;; auto-close file handles
;; (require :mylib) ;; load Lua module
;; (tail! (recurse (- n 1))) ;; assert tail call
;;
;; All other functions are Lua: string.*, table.*, math.*, ipairs, pairs,
;; tonumber, tostring, type, pcall, unpack, select, rawget, rawset, etc.
;;
;; Examples:
;;
;; (fn sum-positive [tbl]
;;   (accumulate [sum 0 _ v (ipairs tbl)]
;;     (if (> v 0) (+ sum v) sum)))
;;
;; (fn reverse-string [s]
;;   (var result "")
;;   (for [i (length s) 1 -1]
;;     (set result (.. result (string.sub s i i))))
;;   result)
;;
;; (fn filter-even [tbl]
;;   (icollect [_ v (ipairs tbl)]
;;     (if (= (% v 2) 0) v)))

"""
        return f'{ref}(fn {name} [{fnl_args}]\n  "{fnl_description}"\n  '

    def test_suite_prefix_lines(self, entry_point) -> List[str]:
        return [
            "(local faith (require :faith))",
            f"(local candidate {entry_point})",
            "(fn test-human-eval []",
        ]

    def test_suite_suffix_lines(self) -> List[str]:
        return [")", "{: test-human-eval}"]

    def deep_equality(self, left: str, right: str) -> str:
        return f"  (faith.= {right} {left})"  # Expected on the left.

    def gen_literal(self, c: bool | str | int | float):
        if type(c) is bool:
            return "true" if c else "false"
        elif type(c) is str:
            return f'"{c}"'
        elif c is None:
            return "nil"
        return repr(c)

    def gen_var(self, variable: str) -> str:
        return variable

    def gen_list(self, list: List[str]) -> str:
        return "[" + " ".join(list) + "]"

    def gen_tuple(self, tuple: List[str]) -> str:
        return "[" + " ".join(tuple) + "]"

    def gen_dict(self, keys: List[str], values: List[str]) -> str:
        pairs = " ".join(f"{k} {v}" for k, v in zip(keys, values))
        return "{" + pairs + "}"

    def gen_call(self, func: str, args: List[str]) -> str:
        return "(" + func + " " + " ".join(args) + ")"
