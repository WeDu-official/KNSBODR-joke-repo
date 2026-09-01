"""
General sliding-puzzle solver using A*.

Works with arbitrary width × height boards.

Examples:

    3x3:
        2 5 3
        1 0 8
        4 6 7

    4x4:
        1  2  3  4
        5  6  7  8
        9 10 11 12
       13 14  0 15

0 represents the empty space.
"""

import heapq
from itertools import count


# ---------------------------------------------------------
# Puzzle representation
# ---------------------------------------------------------

class Puzzle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.size = width * height

        # Goal:
        # 1 2 3
        # 4 5 6
        # 7 8 0
        self.goal = tuple(range(1, self.size)) + (0,)

        # Goal position of every tile
        self.goal_position = {}

        for index, tile in enumerate(self.goal):
            row = index // width
            col = index % width
            self.goal_position[tile] = (row, col)

    # -----------------------------------------------------
    # Manhattan-distance heuristic
    # -----------------------------------------------------

    def heuristic(self, state):
        """
        Sum of Manhattan distances of all tiles.

        h(n) =
            Σ |current_row - goal_row|
              + |current_col - goal_col|
        """

        distance = 0

        for index, tile in enumerate(state):

            # Don't calculate distance for empty space
            if tile == 0:
                continue

            current_row = index // self.width
            current_col = index % self.width

            goal_row, goal_col = self.goal_position[tile]

            distance += abs(current_row - goal_row)
            distance += abs(current_col - goal_col)

        return distance

    # -----------------------------------------------------
    # Generate legal moves
    # -----------------------------------------------------

    def neighbors(self, state):
        """
        Generate all boards reachable in one move.

        Returns:

            new_state, moved_tile, direction
        """

        empty = state.index(0)

        row = empty // self.width
        col = empty % self.width

        moves = []

        # tile above moves down
        if row > 0:
            moves.append((-1, 0, "DOWN"))

        # tile below moves up
        if row < self.height - 1:
            moves.append((1, 0, "UP"))

        # tile left moves right
        if col > 0:
            moves.append((0, -1, "RIGHT"))

        # tile right moves left
        if col < self.width - 1:
            moves.append((0, 1, "LEFT"))

        for dr, dc, direction in moves:

            new_row = row + dr
            new_col = col + dc

            other = new_row * self.width + new_col

            new_state = list(state)

            moved_tile = new_state[other]

            # Swap tile and empty space
            new_state[empty], new_state[other] = (
                new_state[other],
                new_state[empty],
            )

            yield tuple(new_state), moved_tile, direction

    # -----------------------------------------------------
    # Solvability
    # -----------------------------------------------------

    def inversions(self, state):
        """
        Count inversions.

        An inversion occurs when a larger numbered tile
        appears before a smaller numbered tile.
        """

        tiles = [x for x in state if x != 0]

        result = 0

        for i in range(len(tiles)):
            for j in range(i + 1, len(tiles)):
                if tiles[i] > tiles[j]:
                    result += 1

        return result

    def solvable(self, state):
        """
        Determine whether the puzzle can reach the goal.

        For odd-width boards:
            inversions must be even.

        For even-width boards:
            inversions + blank-row-from-bottom must be odd.
        """

        inv = self.inversions(state)

        # Odd width
        if self.width % 2 == 1:
            return inv % 2 == 0

        # Even width
        empty = state.index(0)

        empty_row = empty // self.width

        # Bottom row = 1
        row_from_bottom = self.height - empty_row

        return (inv + row_from_bottom) % 2 == 1

    # -----------------------------------------------------
    # A* search
    # -----------------------------------------------------

    def solve(self, start):
        """
        Solve the puzzle using A*.

        Returns:

            list of states from start → goal
        """

        if start == self.goal:
            return [start]

        if not self.solvable(start):
            return None

        # Priority queue entries:
        #
        # (f, tie_breaker, g, state)
        #
        # f = g + h
        #
        # The tie breaker prevents Python from trying
        # to compare tuples containing board states.
        queue = []

        counter = count()

        start_h = self.heuristic(start)

        heapq.heappush(
            queue,
            (
                start_h,
                next(counter),
                0,
                start,
            ),
        )

        # Cheapest known cost to each state
        g_score = {
            start: 0
        }

        # Used to reconstruct the solution
        came_from = {}

        while queue:

            f, _, g, current = heapq.heappop(queue)

            # Ignore outdated queue entries
            if g != g_score.get(current):
                continue

            # Goal reached
            if current == self.goal:
                return self.reconstruct_path(
                    came_from,
                    current,
                )

            for (
                neighbor,
                moved_tile,
                direction,
            ) in self.neighbors(current):

                new_g = g + 1

                old_g = g_score.get(
                    neighbor,
                    float("inf"),
                )

                if new_g < old_g:

                    g_score[neighbor] = new_g

                    came_from[neighbor] = (
                        current,
                        moved_tile,
                        direction,
                    )

                    h = self.heuristic(neighbor)
                    f = new_g + h

                    heapq.heappush(
                        queue,
                        (
                            f,
                            next(counter),
                            new_g,
                            neighbor,
                        ),
                    )

        return None

    # -----------------------------------------------------
    # Reconstruct solution
    # -----------------------------------------------------

    def reconstruct_path(self, came_from, current):

        path = [current]
        moves = []

        while current in came_from:

            previous, tile, direction = came_from[current]

            moves.append(
                (tile, direction)
            )

            current = previous
            path.append(current)

        path.reverse()
        moves.reverse()

        return path

    # -----------------------------------------------------
    # Print board
    # -----------------------------------------------------

    def print_board(self, state):

        digits = len(str(self.size - 1))

        for row in range(self.height):

            values = state[
                row * self.width:
                (row + 1) * self.width
            ]

            print(
                " ".join(
                    (
                        " " * digits
                        if value == 0
                        else f"{value:>{digits}}"
                    )
                    for value in values
                )
            )

        print()


# ---------------------------------------------------------
# Read puzzle from user
# ---------------------------------------------------------

def read_puzzle(width, height):

    print(
        f"Enter the {width} × {height} puzzle."
    )

    print(
        "Use 0 for the empty space."
    )

    values = []

    for row in range(height):

        while True:

            line = input(
                f"Row {row + 1}: "
            )

            try:
                numbers = [
                    int(x)
                    for x in line.split()
                ]
            except ValueError:
                print("Please enter numbers.")
                continue

            if len(numbers) != width:
                print(
                    f"Enter exactly {width} numbers."
                )
                continue

            values.extend(numbers)
            break

    state = tuple(values)

    expected = set(range(width * height))

    if set(state) != expected:
        raise ValueError(
            f"Puzzle must contain every number "
            f"from 0 to {width * height - 1} exactly once."
        )

    return state


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("╔══════════════════════════════╗")
    print("║      A* PUZZLE SOLVER       ║")
    print("╚══════════════════════════════╝")
    print()

    width = int(input("Width: "))
    height = int(input("Height: "))

    if width < 2 or height < 2:
        raise ValueError(
            "Width and height must both be at least 2."
        )

    puzzle = Puzzle(width, height)

    start = read_puzzle(width, height)

    print()
    print("Starting board:")
    puzzle.print_board(start)

    print(
        "Manhattan distance:",
        puzzle.heuristic(start),
    )

    if not puzzle.solvable(start):

        print()
        print("❌ This puzzle is mathematically unsolvable.")
        return

    print()
    print("🤖 Running A*...")

    solution = puzzle.solve(start)

    if solution is None:

        print(
            "No solution found."
        )

        return

    print()
    print(
        f"✅ Solved in {len(solution) - 1} moves!"
    )

    print()

    for i, state in enumerate(solution):

        print(
            f"Step {i}:"
        )

        puzzle.print_board(state)


if __name__ == "__main__":
    main()
