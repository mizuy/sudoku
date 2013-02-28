
import sys, os
from itertools import product

def iexcept(index):
    "return range(1,10) except index"
    return set(range(0,9))-set([index])

def iterate_box(bx, by):
    for ix,iy in product(range(3), xrange(3)):
        yield 3*bx+ix, 3*by+iy

def chunks(n, l):
    return [l[x: x+n] for x in xrange(0, len(l), n)]

class InconsistentCell(Exception):
    pass

class Retry(Exception):
    pass

class Cell(object):
    def __init__(self, value=None):
        self.value = None
        self.candidate = set(range(1,10))
        if not not value:
            self.set(value)

    def copy(self):
        ret = Cell()
        ret.value = self.value
        ret.candidate = self.candidate.copy()
        return ret

    def __str__(self):
        if self.fixed():
            return str(self.value)
        else:
            return '_'

    __repr__ = __str__

    def fixed(self):
        return not not self.value

    def get(self):
        return value

    def set(self, value):
        if self.fixed():
            raise Exception('already filled.')
        self.value = value
        self.candidate = set([value])

    def update_conflicts(self, conflicts):
        self.candidate -= conflicts
        l = len(self.candidate)
        if l==1:
            self.set(self.candidate.pop())
            return True
        elif l==0:
            raise InconsistentCell('no candidate')
        return False

    def check_uniquify(self, conflicts):
        s = self.candidate - conflicts
        if len(s)==1:
            self.set(s.pop())
            return True
        elif len(s)>1:
            raise InconsistentCell('conflicts')
        return False



class Sudoku(object):
    def __init__(self, init=[]):
        self.matrix = [Cell(x) for x in init]

    def copy(self):
        ret = Sudoku()
        ret.matrix = [x.copy() for x in self.matrix]
        return ret

    def __eq__(self, rhs):
        return hash(self)==hash(rhs)

    def __hash__(self):
        return hash(''.join([str(x) for x in self.matrix]))

    def iter_unfixed(self):
        for x in range(9):
            for y in range(9):
                c = self.get(x,y)
                if c.fixed():
                    continue
                else:
                    yield x,y,c

    def finished(self):
        if self.filled()==81:
            return True
        else:
            return False

    def filled(self):
        return sum(1 for x in self.matrix  if x.fixed())

    def __str__(self):
        ret = '{0}\n'.format(self.filled())
        for y in range(9):
            l = chunks(3, ''.join(str(self.get(x,y)) for x in range(9)))
            ret += '|'.join(l)+'\n'
            if y==2 or y==5:
                ret += '---+---+---\n'

        return ret
    __repr__ = __str__

    def get(self, x, y):
        return self.matrix[y*9+x]

    def _update_candidate(self):
        for x,y,c in self.iter_unfixed():
            row = set(self.get(x, fy).value for fy in range(9))
            col = set(self.get(fx, y).value for fx in range(9))
            box = set(self.get(fx, fy).value for fx,fy in iterate_box(x/3, y/3))
            if c.update_conflicts(row|col|box):
                return True

        for x,y,c in self.iter_unfixed():
            sy = reduce(set.union, (self.get(x,ty).candidate for ty in range(9) if ty!=y))
            if c.check_uniquify(sy):
                return True
            sx = reduce(set.union, (self.get(tx,y).candidate for tx in range(9) if tx!=x))
            if c.check_uniquify(sy):
                return True
            sb = reduce(set.union, (self.get(tx, ty).candidate 
                for tx,ty in iterate_box(x/3, y/3) if (tx,ty)!=(x,y)))
            if c.check_uniquify(sb):
                return True
        return False

    def update_candidate(self):
        while 1:
            update = self._update_candidate()
            if update:
                continue
            else:
                break

    def backtrack(self, depth=1):
        results = set()
        while 1:
            try:
                self.update_candidate()
                if self.finished():
                    return set([self])
            except InconsistentCell:
                return set()

            try:
                for x,y,c in self.iter_unfixed():
                    candidate = c.candidate.copy()
                    for cd in candidate:
                        next = self.copy()
                        #print '=>'*depth,x,y,c,c.candidate,' try ',cd
                        next.get(x,y).set(cd)
                        answers = next.backtrack(depth+1)
                        for a in  answers:
                            results.add(a)
                        if len(answers)==0:
                            #print '=>'*depth,x,y,c,c.candidate,'remove',cd
                            self.get(x,y).candidate.discard(cd)
                            raise Retry()
            except Retry:
                continue
            break
        return results


SAMPLES = [
'000060004,600000370,500000000,102900006,030000000,009300008,305009020,000005400,018200700',
'870200300,000640100,600000007,060010000,000090400,050004070,020030000,090006000,005000001',
'005020040,008500000,100030000,700060050,000400600,950000000,000800103,030104002,000370004',
'010900050,080000084,000103000,600000070,002470000,900008403,165000800,000050006,400000020',
'100007090,030020008,009600500,005300900,010080002,600004000,300000010,040000007,007000300'
]

def main():
    if len(sys.argv)>2:
        problems = [sys.argv[1]]
    else:
        problems = SAMPLES
    for problem in problems:
        problem = ''.join(problem.split(','))
        if len(problem)!=9*9:
            print 'invalid problem'
        ints = list(int(x) for x in list(problem))
        sudoku = Sudoku(ints)
        print sudoku
        results = sudoku.backtrack()
        print results

if __name__ == '__main__':
    main()
