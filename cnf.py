import collections

# representation of a rule A -> B...Z
class Rule(object):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
        self.key = head, tail
    def __eq__(self, other):
        return self.key == other.key
    def __hash__(self):
        return hash(self.key)
    def __str__(self):
        return self.head + " -> " + ' '.join(self.tail)

# build a grammar from A -> BC | d
def get_grammar(string):
    grammar = set()
    for line in string.splitlines():
        head, tail_str = line.split(' -> ')
        for tail_str in tail_str.split(' | '):
            tail = tuple(tail_str.split())
            grammar.add(Rule(head, tail))
    return grammar

def chomsky_normal_form(grammar):
    grammar = set(grammar)
    nonterminals = set(rule.head for rule in grammar)
    
    #1
    for rule in list(grammar):
        if len(rule.tail) >= 2:
            for i, symbol in enumerate(rule.tail):
                if all(rule.head != symbol for rule in grammar):
                    rule = new_symbol(grammar, rule, i, i + 1)
    
    #2
    for rule, symbol in unit_production(grammar, nonterminals):
        grammar.discard(rule)
        for rule2 in rules_start_with(grammar, symbol):
            grammar.add(Rule(rule.head, tuple(rule2.tail)))
        if all(symbol not in rule.tail for rule in grammar):
            for rule2 in rules_start_with(grammar, symbol):
                grammar.discard(rule2)
    
    #3
    for rule in multi_symbol_rules(grammar):
        new_symbol(grammar, rule, 0, 2)
    
    return grammar

# find unit production rules A -> B
def unit_production(grammar, nonterminals):
    while True:
        g = ((rule, rule.tail[0])
         for rule in grammar
         if len(rule.tail) == 1
         if rule.tail[0] in nonterminals)
        yield g.next()

# find all rules start with the given symbol
def rules_start_with(grammar, symbol):
    return [rule for rule in grammar if rule.head == symbol]

# create a new symbol
def new_symbol(grammar, rule, start, stop):
    symbols = rule.tail
    new_head = '_'.join(symbols[start:stop]).upper()
    new_symbols = symbols[:start] + (new_head, ) + symbols[stop:]
    new_rule = Rule(rule.head, new_symbols)
    grammar.discard(rule)
    grammar.add(new_rule)
    grammar.add(Rule(new_head, symbols[start:stop]))
    return new_rule

# find A -> BCD... rules
def multi_symbol_rules(grammar):
    while True:
        g = (rule for rule in grammar if len(rule.tail) >= 3)
        yield g.next()

# cky algorithm
def cky(grammar, words):
    table = collections.defaultdict(set)
    for col, word in enumerate(words):
        col = col + 1
        for rule in grammar:
            if rule.tail == (word,):
                table[col - 1, col].add(rule.head)
        for row in range(col - 2, -1, -1):
            for mid in range(row + 1, col):
                for rule in grammar:
                    if len(rule.tail) == 2:
                        symbol1, symbol2 = rule.tail
                        if symbol1 in table[row, mid] and symbol2 in table[mid, col]:
                            table[row, col].add(rule.head)
    return table

grammar = get_grammar('''\
A -> B C D | E
E -> g F
B -> b
C -> c
D -> d
F -> f''')

grammar_cnf = chomsky_normal_form(grammar)
for rule in grammar_cnf:
    print rule

grammar = get_grammar('''\
S -> NP VP | Aux NP VP | VP
NP -> Pronoun | Proper-Noun | Det Nominal
Nominal -> Noun | Nominal Noun | Nominal PP
VP -> Verb | Verb NP | Verb NP PP | Verb PP | VP PP
PP -> Preposition NP
Det -> that | this | a
Noun -> book | flight | meal | money
Verb -> book | include | prefer
Pronoun -> I | she | me
Proper-Noun -> Houston | TWA
Aux -> does
Preposition -> from | to | on | near | through''')

grammar_cnf = chomsky_normal_form(grammar)
for rule in grammar_cnf:
    print rule

words = 'book a flight through Houston'.split()
table = cky(grammar_cnf, words)
for key, value in table.iteritems():
    print key, value
