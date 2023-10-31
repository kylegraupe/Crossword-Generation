import backtracking
import forward_checking

if __name__ == '__main__':
    print(f'TASK 1: SIMPLE BACKTRACKING..')
    backtracking.execute_application()

    print(f'TASK 2: BACKTRACKING WITH FORWARD CHECKING HEURISTIC..')
    forward_checking.print_outputs()