snakes = []
cols = 0
rows = 0
num_snakes = 0
matrix = []
wormholes = []

# with open("tests/00-example.txt") as topo_file:
with open("tests/wormhole.txt") as topo_file:
    count = 0
    for line in topo_file:
        variables = line[:-1].split(" ")
        if count == 0:
            cols = int(variables[0])
            rows = int(variables[1])
            num_snakes = int(variables[2])
        elif count == 1:
            for n in range(int(num_snakes)):
                snakes.append(int(variables[n]))
        else:
            row = []
            for n in range(int(cols)):
                row.append(variables[n])
                if variables[n] == "*":
                    wormholes.append((n, count-2))
            matrix.append(row)

        count += 1


print(f"wormholes: {wormholes}")
print(f"snakes: {snakes}")

max_snake = max(snakes)
dps = []
dps_path = []
for bound in range(1, max_snake + 1):
    if bound == 1:
        dp = list(map(lambda x: list(map(lambda y: 0 if y == "*" else int(y), x)), matrix))
        dp_path = [['' for _ in range(cols)] for _ in range(rows)]
    else:
        dp = [[0 for _ in range(cols)] for _ in range(rows)]
        dp_path = [['' for _ in range(cols)] for _ in range(rows)]
        for row in range(len(matrix)):
            for col in range(len(matrix[row])):
                                       
                adjacent_wormholes = []
                possible_next = []
                
                # for each adjacent cell, check if it's a wormhole
                for cell in [(col, (row-1)%rows, 'U'), (col, (row+1)%rows, 'D'), ((col-1)%cols, row, 'L'), ((col+1)%cols, row, 'R')]:
                    if (cell[0], cell[1]) in wormholes:
                        adjacent_wormholes.append(cell)
                    else:
                        possible_next.append(cell)
                        
                for adj in adjacent_wormholes:
                    for i, w in enumerate(wormholes):
                        possible_next.append((w[0], w[1], f"{adj[2]}{i}"))
                        # print((w[0], w[1], f"{adj[2]}{i}", bound-2, dps[bound-2][w[1]][w[0]]), end=' ')
                    # print()
                    
                # remove duplicates (can there actually be any??)
                # possible_next = list(set(possible_next))
                prev = dps[bound - 2]
                
                choices = [(prev[y % rows][x % cols], direction) for x, y, direction in possible_next]
                paths, direction = zip(*sorted(choices, key=lambda x: x[0], reverse=True))
                
                # paths[0] is optimal, but we can't always take the optimal path because it might overlap itself
                
                # check for overlaps:
                # cancelled
                
                assert len(paths) == len(direction)
                
                best_choice_index = 0
                
                # for possible_path_index in range(len(paths)):
                #     if not checkForOverlap(possible_path_index, dps_path, row, col, rows, cols, paths, wormholes):
                #         continue
                #     else:
                #         best_choice_index = paths[possible_path_index]
                    
                
                dp[row][col] = paths[best_choice_index] + (0 if matrix[row][col] == '*' else int(matrix[row][col]))
                dp_path[row][col] = direction[best_choice_index]
                # print(dp_path[4][5])
    dps.append(dp)
    dps_path.append(dp_path)


    
# do longest snakes first
import numpy as np
snakes = sorted(snakes, reverse=True)

free_positions = [[1 for _ in range(cols)] for _ in range(rows)]

# for r in dps_path[-1]:
#     print(r)

dps = np.array(dps)


MIN = np.iinfo(dps.dtype).min
flipDirection = {
    'U' : 'D',
    'D' : 'U',
    'L' : 'R',
    'R' : 'L',
}

for snake_length in snakes:
    # we will grow the snake from the optimal square
    optimal_square = np.argmax(dps[snake_length - 1])
    head = tail = (optimal_square % cols, optimal_square // cols)
    dps[:, head[0], head[1]] = MIN + 48 - snake_length
    visited = [head]
    for i in range(snake_length-1, 0, -1):
        # grow the snake
        growth_choices = {
            1 : (((head[0] - 1) % rows, head[1]), 1, 'U'), # head up
            2 : (((head[0] + 1) % rows, head[1]), 2, 'D'), # head down
            3 : ((head[0], (head[1] - 1) % cols), 3, 'L'), # head left
            4 : ((head[0], (head[1] + 1) % cols), 4, 'R'), # head right
            5 : (((tail[0] - 1) % rows, tail[1]), 5, 'U'), # tail up
            6 : (((tail[0] + 1) % rows, tail[1]), 6, 'D'), # tail down
            7 : ((tail[0], (tail[1] - 1) % cols), 7, 'L'), # tail left
            8 : ((tail[0], (tail[1] + 1) % cols), 8, 'R'), # tail right
        }
        choice = max([(dps[i, c[0], c[1]], growth_index, direction) for c, growth_index, direction in growth_choices.values()], key=lambda x: x[0])
        
        
        if choice[1] <= 4:
            head = growth_choices[choice[1]][0]
            dps[:, head[0], head[1]] = MIN + 48 - snake_length            
            
            visited.insert(1, flipDirection[choice[2]])
            
            # this needs to recalculate the growth_choices
            st = dps_path[i][head[0]][head[1]]
            if len(st) > 1:
                print(f"updating head from {head} to {wormholes[int(st[1:])]}")
                head = wormholes[int(st[1:])]
                
                visited.insert(1, head)
                
        else:
            tail = growth_choices[choice[1]][0]
            dps[:, tail[0], tail[1]] = MIN + 48 - snake_length
            
            # everything in tail is backwards:
            # - we flip any directions
            # - we append wormholes first
                        
            st = dps_path[i][tail[0]][tail[1]]
            if len(st) > 1:
                print(f"updating tail from {tail} to {wormholes[int(st[1:])]}")
                tail = wormholes[int(st[1:])]
                visited.append(tail)
                
            visited.append(choice[2])
        print(visited)
    
    print("-----------------")
    print(f"visited: {visited}")
        
np.set_printoptions(linewidth=100000)

print("------------------")

for r in dps[-1]:
    print(r)
