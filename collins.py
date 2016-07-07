import collections

# representation of a rule A -> B...Z
class Rule(object):
    def __init__(self, head, symbol, prob, type):
        self.head = head
        self.symbol = symbol
        self.prob = prob
        self.type = type
        self.key = head, symbol, prob, type
    def __eq__(self, other):
        return self.key == other.key
    def __hash__(self):
        return hash(self.key)
    def __str__(self):
        return ','.join(self.head) + " ->" + self.type + " " + ' '.join(self.symbol) + " " + self.prob

# build a grammar from A -> BC | d
def get_grammar(string):
    grammar = set()
    for line in string.splitlines():
        head, tail_str = line.split(' -> ')
        for tail_str in tail_str.split(' | '):
            grammar.add(Rule((head,), tuple(tail_str.split()), '0', '0'))
    return grammar

# build a grammar from A -> 1 B C 0.1 | d 0.2
def get_lexicalized_grammar(string):
    grammar = set()
    for line in string.splitlines():
        head, symbol_str = line.split(' -> ')
        for symbol_str in symbol_str.split(' | '):
            symbol_str_list = symbol_str.split()
            symbol = tuple(symbol_str_list[1:-1])
            prob = symbol_str_list[-1]
            grammar.add(Rule(tuple(head.split(",")), symbol, prob, symbol_str_list[0]))
    return grammar

def chomsky_normal_form(grammar):
    grammar = set(grammar)
    nonterminals = set(rule.head for rule in grammar)
    
    #1
    for rule in list(grammar):
        if len(rule.symbol) >= 2:
            for i, symbol in enumerate(rule.symbol):
                if all(rule.head[0] != symbol for rule in grammar):
                    rule = new_symbol(grammar, rule, i, i + 1)
    
    #2
    for rule, symbol in unit_production(grammar, nonterminals):
        grammar.discard(rule)
        for rule2 in rules_start_with(grammar, symbol):
            grammar.add(Rule(rule.head, tuple(rule2.symbol), '0', '0'))
        if all(symbol not in rule.symbol for rule in grammar):
            for rule2 in rules_start_with(grammar, symbol):
                grammar.discard(rule2)
    
    #3
    for rule in multi_symbol_rules(grammar):
        new_symbol(grammar, rule, 0, 2)
    
    return grammar

# find unit production rules A -> B
def unit_production(grammar, nonterminals):
    while True:
        g = ((rule, rule.symbol[0])
         for rule in grammar
         if len(rule.symbol) == 1
         if rule.symbol[0] in nonterminals)
        yield g.next()

# find all rules start with the given symbol
def rules_start_with(grammar, symbol):
    return [rule for rule in grammar if rule.head[0] == symbol]

# create a new symbol
def new_symbol(grammar, rule, start, stop):
    symbols = rule.symbol
    new_head = '_'.join(symbols[start:stop]).upper()
    new_symbols = symbols[:start] + (new_head, ) + symbols[stop:]
    new_rule = Rule(rule.head, new_symbols, '0', '0')
    #print "new_symbol", grammar.size()
    grammar.discard(rule)
    grammar.add(new_rule)
    grammar.add(Rule((new_head, ), symbols[start:stop], '0', '0'))
    return new_rule

# find A -> BCD... rules
def multi_symbol_rules(grammar):
    while True:
        g = (rule for rule in grammar if len(rule.symbol) >= 3)
        yield g.next()

#cky algorithm
def cky(grammar, words):
    table = collections.defaultdict(set)
    for col, word in enumerate(words):
        col = col + 1
        for rule in grammar:
            if rule.symbol == (word,):
                table[col - 1, col].add(rule.head)
        for row in range(col - 2, -1, -1):
            for mid in range(row + 1, col):
                for rule in grammar:
                    if len(rule.symbol) == 2:
                        symbol1, symbol2 = rule.symbol
                        if symbol1 in table[row, mid] and symbol2 in table[mid, col]:
                            table[row, col].add(rule.head)
    return table

def collins(grammar, words, gammas):
    ddict = collections.defaultdict
    probs = ddict(float)
    backs = ddict(tuple)
    n = len(words)
    print "n:", n
    
    # base case
    for i in range(0,n):
        print "i:",i
        for rule in grammar:
            if words[i] == rule.symbol[0]:
                print i+1,i+1,i+1,rule.head[0],rule.prob
                probs[i+1,i+1,i+1,rule.head[0]] = float(rule.prob)
                backs[i+1,i+1,i+1,rule.head[0]] = None, None, None, None

    # recursive case
    for l in range(1,n):
        print "l:", l
        for i in range(1,n-l+1):
            j = i + l
            print "i:", i
            print "j:", j
            for rule in grammar:
                for h in range(i,j+1):
                    print "h:",h
                    print i,j,h,rule.head[0],"init value 0"
                    probs[i,j,h,rule.head[0]] = 0
                    for s in range(h,j):
                        for m in range(s+1,j+1):
                            if len(rule.symbol) == 2 and rule.type == '1' \
                            and probs[i,s,h,rule.symbol[0].split(",")[0]] > 0 \
                            and probs[s+1,j,m,rule.symbol[1].split(",")[0]]:
                                print "rule:",rule
                                print type(float(rule.prob))
                                print i,s,h,rule.symbol[0].split(",")[0]
                                print probs[i,s,h,rule.symbol[0].split(",")[0]]
                                print s+1,j,m,rule.symbol[1].split(",")[0]
                                print probs[s+1,j,m,rule.symbol[1].split(",")[0]]
                                p = float(rule.prob) * probs[i,s,h,rule.symbol[0].split(",")[0]] * probs[s+1,j,m,rule.symbol[1].split(",")[0]]
                                if p > probs[i,j,h,rule.head[0]]:
                                    print i,j,h,rule.head[0]
                                    probs[i,j,h,rule.head[0]] = p
                                    backs[i,j,h,rule.head[0]] = s,m,rule.symbol[0].split(",")[0],rule.symbol[1].split(",")[0]
                    for s in range(i,h):
                        for m in range(i,s+1):
                            if len(rule.symbol) == 2 and rule.type == '2' \
                            and probs[i,s,m,rule.symbol[0].split(",")[0]] > 0 \
                            and probs[s+1,j,h,rule.symbol[1].split(",")[0]] > 0:
                                p = float(rule.prob) * probs[i,s,m,rule.symbol[0].split(",")[0]] * probs[s+1,j,h,rule.symbol[1].split(",")[0]]
                                if p > probs[i,j,h,rule.head[0]]:
                                    print i,j,h,rule.head[0]
                                    probs[i,j,h,rule.head[0]] = p
                                    backs[i,j,h,rule.head[0]] = s,m,rule.symbol[0].split(",")[0],rule.symbol[1].split(",")[0]
    
    def get_tree(start, stop, h, symbol):
        print "get_tree", start, stop, h, symbol
        print backs[start, stop, h, symbol]
        s,m,Y,Z = backs[start, stop, h, symbol]
        if s is m is Y is Z is None:
            return '[%s,%s %s]' % (symbol, words[h-1], words[start-1])
        else:
            print "tree1:",start,s,h,Y
            print "tree2:",s+1,stop,m,Z
            if h <= s:
                tree1 = get_tree(start,s,h,Y)
                tree2 = get_tree(s+1,stop,m,Z)
            else:
                tree1 = get_tree(start,s,m,Y)
                tree2 = get_tree(s+1,stop,h,Z)
            return '[%s,%s %s %s]' % (symbol, words[h-1], tree1, tree2)
    
    prob = 0
    for gamma in gammas:
        for i in range(1,n+1):
            if gamma[0] == 'S' and gamma[1] == words[i-1]:
                if gammas[gamma] * probs[1, len(words), i, 'S'] > prob:
                    prob = gammas[gamma] * probs[1, len(words), i, 'S']
                    print "prob:", prob
                    h = i
    
    return get_tree(1, len(words), h, 'S'), prob, backs

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

lexicalized_grammar_cnf = get_lexicalized_grammar('''\
S,dumped -> 2 NNS,workers VP,dumped 1.0
NNS,workers -> 1 workers 0.5
NNS,sacks -> 1 sacks 0.5
VP,dumped -> 1 VBD_NNS,dumped PP,into 0.6
VP,dumped -> 1 VBD,dumped NP,sacks 0.4
VBD_NNS,dumped -> 1 VBD,dumped NNS,sacks 1.0
VBD,dumped -> 1 dumped 1.0
PP,into -> 1 P,into NP,bin 1.0
NP,sacks -> 1 NNS,sacks PP,into 0.5
P,into -> 1 into 1.0
NP,bin -> 2 DT,a NN,bin 0.5
DT,a -> 1 a 1.0
NN,bin -> 1 bin 1.0''')
gammas = collections.defaultdict(float)
gammas['S','dumped'] = 1.0

tree, probs, backs = collins(lexicalized_grammar_cnf, "workers dumped sacks into a bin".split(), gammas)
print "tree:",tree
print "probs:",probs
print "backs:",backs
