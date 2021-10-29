import itertools
import random
import sys
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells where each cell is (i,j),
    and a count of the number of those cells which are mines.
    """ 

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count # count of mines

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # Any time the number of cells is equal to the count, we know that all of that sentence’s cells must be mines
        # self.cells if len(self.cells) == self.count else None
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        else:
            return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # Any time we have a sentence whose count is 0, we know that all of that sentence’s cells must be safe
        #if self.count == 0:
        if not self.count:
            return self.cells
        else:
            return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If our AI knew the sentence {A, B, C} = 2, and we were told that C is a mine, we could remove C from the sentence and decrease the value of count (since C was a mine that contributed to that count), giving us the sentence {A, B} = 1

        # First check to see if cell is one of the cells included in the sentence.
        if cell in self.cells:
            # If cell is in the sentence, the function should update the sentence so that cell is no longer in the sentence, but still represents a logically correct sentence given that cell is known to be a mine. decrease the value of count
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # If our AI knew the sentence {A, B, C} = 2, we don’t yet have enough information to conclude anything. If we were told that C were safe, we could remove C from the sentence altogether, leaving us with the sentence {A, B} = 2 

        # First check to see if cell is one of the cells included in the sentence.
        if cell in self.cells:
            #If cell is in the sentence, the function should update the sentence so that cell is no longer in the sentence, but still represents a logically correct sentence given that cell is known to be safe.
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Mark the cell as one of the moves made
        self.moves_made.add(cell)
        # Mark the cell as a safe cell, updating any sentences that contain the cell as well
        self.mark_safe(cell)

        # Add a new sentence to the AI’s knowledge base
        # Based on the value of cell and count, to indicate that count of the cell’s neighbors are mines. 
        # Be sure to only include cells whose state is still undetermined in the sentence. do not include known mines or known safes
        cell_neighbors = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # ignore cell in question
                if (i,j) == cell:
                    continue

                if (i,j) in self.safes:
                    continue

                if (i,j) in self.moves_made:
                    continue

                if (i,j) in self.mines:
                    count -= 1
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    cell_neighbors.add((i,j))

        new_sentence = Sentence(cell_neighbors, count)
        # Add a new sentence to the AI’s knowledge base
        self.knowledge.append(new_sentence)

        # If, based on any of the sentences in self.knowledge, new cells can be marked as safe or as mines, then the function should do so.
        k = copy.deepcopy(self.knowledge)
        if k:
            for sentence in k:
                length = len(sentence.cells)
                # Remove empty sentences
                if length == 0 and sentence.count == 0:
                    k.remove(sentence)
                # Any time we have a sentence whose count is 0, we know that all of that sentences cells must be safe.
                if length >= 1 and sentence.count == 0:
                    print('length: ' + str(length) + ' count: ' + str(sentence.count) + ' cells: ' + str(sentence.cells))
                    for c in sentence.cells:
                        if c not in self.safes:
                            self.mark_safe(c)
                    if sentence in k:
                        k.remove(sentence)
                # Any time the number of cells is equal to the count, we know that all of that sentences cells must be mines.
                if length >=1 and length == sentence.count:
                    for c in sentence.cells:
                        if c not in self.mines:
                            self.mark_mine(c)
                    if sentence in k:
                        k.remove(sentence)
            self.knowledge = k
        

    

        # If, based on any of the sentences in self.knowledge, new sentences can be inferred (using the subset method described in the Background), then those sentences should be added to the knowledge base as well.
        new_knowledge = True

        while new_knowledge:
            new_knowledge = False

            if len(self.knowledge) >= 2:
                for sa, sb in itertools.combinations(self.knowledge, 2):
                    # Check if two sentences share any items.
                    if sa.cells == sb.cells:
                        continue  
                    # Check if two sentences intersect    
                    if sa.cells.intersection(sb.cells):
                        # Check if SentenceA  is Subset of SentenceB
                        if sa.cells.issubset(sb.cells):
                            new_cells = sb.cells - sa.cells
                            new_count = sb.count - sa.count
                            new_sentence = Sentence(new_cells, new_count)
                            if new_sentence not in self.knowledge:
                                self.knowledge.append(new_sentence)
                                # It may be possible to draw new inferences that weren’t possible before
                                new_knowledge = True
                        # Check if SentenceB is Subset of SentenceA
                        elif sb.cells.issubset(sa.cells):
                            new_cells = sa.cells - sb.cells
                            new_count = sa.count - sb.count
                            new_sentence = Sentence(new_cells, new_count) 
                            if new_sentence not in self.knowledge:
                                self.knowledge.append(new_sentence)
                                 # It may be possible to draw new inferences that weren’t possible before
                                new_knowledge = True

       

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safes_not_in_moves = self.safes - self.moves_made
        if len(safes_not_in_moves) >= 1:
            move = random.choice(list(safes_not_in_moves))
            self.moves_made.add(move)
            self.mark_safe(move)
            return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        print('length of mines' + str(len(self.mines)))

        #check available moves on board
        available_moves = (self.height * self.width) - (len(self.moves_made) + len(self.mines))
        if available_moves == 0:
            return None

        i = random.randint(0,self.width - 1)
        j = random.randint(0,self.width - 1)
        random_cell = set([(i,j)])


        if random_cell not in self.mines and random_cell not in self.moves_made:
            move = (i,j)
            self.moves_made.add(move)
            self.mark_safe(move)
            return i, j
        

# #testing
# if __name__ == '__main__':
#     globals()[sys.argv[1]](sys.argv[2])
