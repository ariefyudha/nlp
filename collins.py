import collections

# representation of a rule A -> B...Z
class Rule(object):
    def __init__(self, head, symbol, prob, type):
        self.head = head
        self.symbol = symbol
        self.prob = prob
        self.type = type
        self.key = head, symbol
    def __eq__(self, other):
        return self.key == other.key
    def __hash__(self):
        return hash(self.key)
    def __str__(self):
        return ','.join(self.head) + " ->" + self.type + " " + ' '.join(self.symbol) + " " + self.prob

# build a grammar from A -> B C | d
def get_grammar(string):
    grammar = set()
    for line in string.splitlines():
        head, symbol_str = line.split(' -> ')
        for symbol_str in symbol_str.split(' | '):
            symbol_str_list = symbol_str.split()
            symbol = tuple(symbol_str_list[1:-1])
            prob = symbol_str_list[-1]
            grammar.add(Rule(tuple(head.split(",")), symbol, prob, symbol_str_list[0]))
    return grammar

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

grammar_cnf = get_grammar('''\
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
for rule in grammar_cnf:
    print rule
gammas = collections.defaultdict(float)
gammas['S','dumped'] = 1.0

tree, probs, backs = collins(grammar_cnf, "workers dumped sacks into a bin".split(), gammas)
print "tree:",tree
print "probs:",probs
print "backs:",backs
