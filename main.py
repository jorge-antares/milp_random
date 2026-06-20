import sys
import time
import random
import pandas as pd

from ortools.linear_solver import pywraplp



def solve_problem(data: pd.DataFrame, thresh: dict):
    if "value" not in data.columns:
        raise ValueError("Input data must contain a 'value' column.")
    if "umin" not in thresh or "umax" not in thresh:
        raise ValueError("thresh must contain both 'umin' and 'umax' keys.")

    umin = int(thresh["umin"])
    umax = int(thresh["umax"])

    if umin < 0 or umax < 0 or umin > umax:
        raise ValueError("Expected 0 <= umin <= umax.")
    if umax > len(data.index):
        raise ValueError("umax cannot exceed the number of rows in data.")

    # Algorithms: CBC_MIXED_INTEGER_PROGRAMMING, SAT, BOP, SCIP
    solver = pywraplp.Solver.CreateSolver("BOP") 

    if solver is None:
        raise RuntimeError("Solver is unavailable.")

    x = {i: solver.BoolVar(f"x_{k}") for k, i in enumerate(data.index)}
    # Relaxed version (for testing):
    #x = {i: solver.NumVar(0, 1, f"x_{k}") for k, i in enumerate(data.index)}
    objective_terms = [data.at[i, "value"] * x[i] for i in data.index]
    objective_expression = " + ".join(
        f"{data.at[i, 'value']}*x_{k}" for k, i in enumerate(data.index)
    )
    solver.Maximize(solver.Sum(objective_terms))
    solver.Add(solver.Sum(x[i] for i in data.index) >= umin)
    solver.Add(solver.Sum(x[i] for i in data.index) <= umax)

    status = solver.Solve()

    if status not in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        print("No feasible solution found.")
        return None

    print("Solution:")
    sum_x = 0
    count_non_integer = 0
    for i in data.index:
        x_current = x[i].solution_value()
        if x_current not in (0, 1):
            count_non_integer += 1
            print(f"  x[{i}] = {x_current} (non-integer)")
        #print(f"  x[{i}] = {x_current}")
        sum_x += x_current
    print(f"Sum of x: {sum_x}")
    print(f"Expected range for sum of x: [{umin}, {umax}]")
    print(f"Objective value: {solver.Objective().Value()}")
    print(f"Number of non-integer x values: {count_non_integer}")
    return solver


def create_synthetic_table(n: int, columns: dict) -> pd.DataFrame:
    data = {}
    for column_name, values in columns.items():
        if not values:
            raise ValueError(f"Column '{column_name}' must contain at least one value.")
        data[column_name] = [random.choice(values) for _ in range(n)]
    return pd.DataFrame(data)


def create_seconds_to_hms(seconds: int) -> str:
    if seconds < 0:
        raise ValueError("Seconds cannot be negative.")
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{remaining_seconds:02d}"


def main(n: int = 10):
    start_time = time.time()
    df = create_synthetic_table(
        n       = n,
        columns = {
            "value":    [ i for i in range(1, n)],
            "attrib_1": ["A", "B", "C", "D"],
        }
    )
    model = solve_problem(df, thresh={"umin": int(0.02 * n), "umax": int(0.03 * n)})
    end_time = time.time()
    print(f"Execution time: {create_seconds_to_hms(int(end_time - start_time))}")
    return None
    


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    main(n)