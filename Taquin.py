import random
import itertools
import collections
import time


class Puzzle:
    """
    Une classe représentant un puzzle
    - 'table' devrait être une liste carrée de listes avec des entrées entières 0 ... largeur ^ 2 - 1
        par exemple. [[1,2,3], [4,0,6], [7,5,8]]
    """

    def __init__(self, table):
        self.largeur = len(table[0])
        self.table = table

    @property
    def est_resolu(self):
        """
        Le puzzle est résolu si les nombres sont en ordre croissant de gauche à droite
        et que '0' est en dernière position sur le plateau
        """
        n = self.largeur * self.largeur
        return str(self) == ''.join(map(str, range(1, n))) + '0'

    @property
    def actions(self):
        """
        Retourner la liste de (move, action).
        """

        def create_move(p1, p2):
            return lambda: self._move(p1, p2)

        moves = []
        for i, j in itertools.product(range(self.largeur), range(self.largeur)):
            """
            Le mouvement du trou
            """
            direcs = {'D': (i, j - 1),
                      'G': (i, j + 1),
                      'B': (i - 1, j),
                      'H': (i + 1, j)}

            for action, (r, c) in direcs.items():
                if 0 <= r < self.largeur and 0 <= c < self.largeur and self.table[r][c] == 0:
                    move = create_move((i, j), (r, c)), action
                    moves.append(move)
        return moves

    @property
    def manhattan(self):
        distance = 0
        for i in range(3):
            for j in range(3):
                if self.table[i][j] != 0:
                    x, y = divmod(self.table[i][j] - 1, 3)
                    distance += abs(x - i) + abs(y - j)
        return distance

    def shuffle(self):
        """
        Retourner un nouveau puzzle qui a été mélangé avec 50 coups aléatoires
        """
        puzzle = self
        for _ in range(50):
            puzzle = random.choice(puzzle.actions)[0]()
        return puzzle

    def copy(self):
        """
        Retourner un nouveau puzzle avec le même table que 'self'
        """
        table = []
        for row in self.table:
            table.append([x for x in row])
        return Puzzle(table)

    def _move(self, p1, p2):
        """
        Retourner un nouveau puzzle où les positions «p1» et «p2» ont été échangées.
        """
        copy = self.copy()
        i, j = p1
        r, c = p2
        copy.table[i][j], copy.table[r][c] = copy.table[r][c], copy.table[i][j]
        return copy

    def pprint(self):
        for row in self.table:
            print(row)
        print()

    def __str__(self):
        return ''.join(map(str, self))

    def __iter__(self):
        for row in self.table:
            yield from row


class Noeud:
    """
    Une classe représentant un etat (noeud de la recherche binaire) de Puzzle
     - 'puzzle' est une instance de Puzzle
     - 'parent' est le noeud précédent généré par le solveur
     - 'action' est l'action pour produire l'etat de puzzle
    """

    def __init__(self, puzzle, parent=None, action=None):
        self.puzzle = puzzle
        self.parent = parent
        self.action = action
        if self.parent is not None:
            self.g = parent.g + 1
        else:
            self.g = 0

    @property
    def etat(self):
        """
        Retourne l'etat de puzzle
        """
        return str(self)

    @property
    def chemin(self):
        """
        Retourne un chemin d'un noeud depuis la racine 'parent'
        """
        noeud, p = self, []
        while noeud:
            p.append(noeud)
            noeud = noeud.parent
        yield from reversed(p)

    @property
    def est_resolu(self):
        """ Vérifier si le 'puzzle' est résolu"""
        return self.puzzle.est_resolu

    @property
    def actions(self):
        """ L'actions pour accéder à l'état actuel """
        return self.puzzle.actions

    @property
    def h(self):
        """"h"""
        return self.puzzle.manhattan

    @property
    def f(self):
        """"f"""
        return self.h + self.g

    def __str__(self):
        return str(self.puzzle)


class Solution:
    """
    Resoudre d'un puzzle
    - 'initial' est un etat de Puzzle
    """

    def __init__(self, initial):
        self.initial = initial

    def resoudre(self):
        """
        Effectuer une première recherche en largeur et retourner un chemin vers la solution
        """
        queue = collections.deque([Noeud(self.initial)])
        rs = set()
        rs.add(queue[0].etat)
        while queue:
            queue = collections.deque(sorted(list(queue), key=lambda noeud: noeud.f))
            noeud = queue.popleft()
            if noeud.est_resolu:
                return noeud.chemin

            for move, action in noeud.actions:
                enfant = Noeud(move(), noeud, action)

                if enfant.etat not in rs:
                    queue.appendleft(enfant)
                    rs.add(enfant.etat)


# test
table = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
puzzle = Puzzle(table)
print('Puzzle avant melange : ')
puzzle.pprint()
puzzle = puzzle.shuffle()
print('Puzzle apres melange : ')
puzzle.pprint()
s = Solution(puzzle)
t_init = time.time()
p = s.resoudre()
t_final = time.time()

steps = 0
for noeud in p:
    print(noeud.action)
    noeud.puzzle.pprint()
    steps += 1

print("Nombre de déplacements: " + str(steps))
print("Durée de la recherche: " + str(t_final - t_init) + " second(s)")
