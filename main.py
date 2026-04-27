from __future__ import annotations

import sys
import os
from pathlib import Path
from typing import List

# Permet de charger le module compilé s'il est placé à la racine du projet
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

os.add_dll_directory(r"C:\msys64\ucrt64\bin")

import tau1_cpp  # type: ignore
print(tau1_cpp.tau1_execution_time_ms(1000))

from analysis import compute_statistics, choose_c1_from_measurements, print_statistics
from scheduler import (
    build_task_set,
    export_schedule_csv,
    plot_case_comparison,
    plot_gantt,
    schedule_to_dataframe, 
    utilization,
    hyperperiod,
    generate_jobs,
    schedule_non_preemptive,
    check_schedule,
    total_waiting_time,
    total_idle_time,
    print_task_set,
    print_jobs,
    print_schedule_table,
)


def measure_tau1_execution_times(
    runs: int = 1000,
    num_digits: int = 200,
    seed: int = 42,
) -> List[float]:
    tau1_cpp.seed_rng(seed)
    times_ms: List[float] = []
    for _ in range(runs):
        t = tau1_cpp.tau1_execution_time_ms(num_digits)
        times_ms.append(float(t))
    return times_ms


def main() -> None:
    print("=== STEP 1: Measure τ1 in C++ ===")
    times_ms = measure_tau1_execution_times(
    runs=1000,
    num_digits=200,
    seed=42,
    )

    print("\n=== STEP 2: Statistics ===")
    stats = compute_statistics(times_ms)
    print_statistics(stats)

    c1 = choose_c1_from_measurements(stats, safety_factor=1.10)
    print(f"\nChosen C1 with 10% safety margin = {c1:.6f} ms")

    print("\n=== STEP 3: Build task set ===")
    tasks = build_task_set(c1)
    print_task_set(tasks)

    u = utilization(tasks)
    print(f"\nUtilization U = {u:.6f}")
    print(f"Basic utilization test (U <= 1): {u <= 1.0}")
    #if u > 1.0:
        #print("\nERROR: The task set is not schedulable because U > 1.")
        #print("Reduce num_digits for τ1 and run again.")
    #return

    hp = hyperperiod(tasks)
    print(f"Hyperperiod = {hp}")

    print("\n=== STEP 4: Generate jobs ===")
    jobs = generate_jobs(tasks, hp)
    print(f"Number of jobs over one hyperperiod = {len(jobs)}")
    print_jobs(jobs, limit=40)

    print("\n=== STEP 5: Non-preemptive schedule, no deadline miss allowed ===")
    scheduled_1, _ = schedule_non_preemptive(jobs, allow_tau5_miss=False)
    print_schedule_table(scheduled_1, limit=60)
    feasible_1 = check_schedule(scheduled_1, allow_tau5_miss=False)
    waiting_1 = total_waiting_time(scheduled_1)
    idle_1 = total_idle_time(scheduled_1)
    print(f"\nFeasible (no miss allowed): {feasible_1}")
    print(f"Total waiting time: {waiting_1:.6f}")
    print(f"Total idle time: {idle_1:.6f}")

    df1 = schedule_to_dataframe(scheduled_1)
    print("\n=== STEP 5B: Table for Case 1 ===")
    print(df1.to_string(index=False))
    export_schedule_csv(scheduled_1, "schedule_case1.csv")
    plot_gantt(scheduled_1, "Gantt Chart - Case 1 (No deadline miss)", "gantt_case1.png")




    print("\n=== STEP 6: Non-preemptive schedule, τ5 may miss ===")
    scheduled_2, _ = schedule_non_preemptive(jobs, allow_tau5_miss=True)
    print_schedule_table(scheduled_2, limit=60)
    feasible_2 = check_schedule(scheduled_2, allow_tau5_miss=True)
    waiting_2 = total_waiting_time(scheduled_2)
    idle_2 = total_idle_time(scheduled_2)
    print(f"\nFeasible (τ5 may miss): {feasible_2}")
    print(f"Total waiting time: {waiting_2:.6f}")
    print(f"Total idle time: {idle_2:.6f}")

    df2 = schedule_to_dataframe(scheduled_2)
    print("\n=== STEP 6B: Table for Case 2 ===")
    print(df2.to_string(index=False))
    export_schedule_csv(scheduled_2, "schedule_case2.csv")
    plot_gantt(scheduled_2, "Gantt Chart - Case 2 (τ5 may miss)", "gantt_case2.png")

    print("\n=== STEP 7: Comparison ===")
    print(f"Case 1 waiting: {waiting_1:.6f}")
    print(f"Case 1 idle   : {idle_1:.6f}")
    print(f"Case 2 waiting: {waiting_2:.6f}")
    print(f"Case 2 idle   : {idle_2:.6f}")

    plot_case_comparison(waiting_1, idle_1, waiting_2, idle_2, "comparison.png")
if __name__ == "__main__":
    main()