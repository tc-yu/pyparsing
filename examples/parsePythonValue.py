# parsePythonValue.py
#
# Copyright, 2006, by Paul McGuire
#
import pyparsing as pp


cvtBool = lambda t: t[0] == "True"
cvtInt = lambda toks: int(toks[0])
cvtReal = lambda toks: float(toks[0])
cvtTuple = lambda toks: tuple(toks.asList())
cvtDict = lambda toks: dict(toks.asList())
cvtList = lambda toks: [toks.asList()]

# define punctuation as suppressed literals
lparen, rparen, lbrack, rbrack, lbrace, rbrace, colon, comma = map(
    pp.Suppress, "()[]{}:,"
)

integer = pp.Regex(r"[+-]?\d+").setName("integer").setParseAction(cvtInt)
real = pp.Regex(r"[+-]?\d+\.\d*([Ee][+-]?\d+)?").setName("real").setParseAction(cvtReal)
tupleStr = pp.Forward().set_name("tuple_expr")
listStr = pp.Forward().set_name("list_expr")
dictStr = pp.Forward().set_name("dict_expr")

unistr = pp.unicodeString().setParseAction(lambda t: t[0][2:-1])
quoted_str = pp.quotedString().setParseAction(lambda t: t[0][1:-1])
boolLiteral = pp.oneOf("True False", asKeyword=True).setParseAction(cvtBool)
noneLiteral = pp.Keyword("None").setParseAction(pp.replaceWith(None))

listItem = (
    real
    | integer
    | quoted_str
    | unistr
    | boolLiteral
    | noneLiteral
    | pp.Group(listStr)
    | tupleStr
    | dictStr
).set_name("list_item")

tupleStr <<= (
    lparen + pp.Optional(pp.delimitedList(listItem, allow_trailing_delim=True)) + rparen
)
tupleStr.setParseAction(cvtTuple)

listStr <<= (
    lbrack + pp.Optional(pp.delimitedList(listItem, allow_trailing_delim=True)) + rbrack
)
listStr.setParseAction(cvtList, lambda t: t[0])

dictEntry = pp.Group(listItem + colon + listItem).set_name("dict_entry")
dictStr <<= (
    lbrace + pp.Optional(pp.delimitedList(dictEntry, allow_trailing_delim=True)) + rbrace
)
dictStr.setParseAction(cvtDict)

if __name__ == "__main__":

    tests = """['a', 100, ('A', [101,102]), 3.14, [ +2.718, 'xyzzy', -1.414] ]
               [{0: [2], 1: []}, {0: [], 1: [], 2: []}, {0: [1, 2]}]
               { 'A':1, 'B':2, 'C': {'a': 1.2, 'b': 3.4} }
               3.14159
               42
               6.02E23
               6.02e+023
               1.0e-7
               'a quoted string'"""

    listItem.runTests(tests)
