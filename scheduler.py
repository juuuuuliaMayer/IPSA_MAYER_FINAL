from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from tracemalloc import start
from tracemalloc import start
from turtle import color
from turtle import color
from typing import List, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt



def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b)


@dataclass
class Task:
    name: str
    C: float
    T: int
    D: Optional[int] = None

    def __post_init__(self) -> None:
        if self.D is None:
            self.D = self.T


@dataclass
class Job:
    task_name: str
    job_id: int
    release: float
    deadline: float
    execution: float
    start: Optional[float] = None
    finish: Optional[float] = None
    waiting: Optional[float] = None
    response_time: Optional[float] = None
    missed_deadline: Optional[bool] = None

    def clone(self) -> "Job":
        return Job(
            task_name=self.task_name,
            job_id=self.job_id,
            release=self.release,
            deadline=self.deadline,
            execution=self.execution,
            start=self.start,
            finish=self.finish,
            waiting=self.waiting,
            response_time=self.response_time,
            missed_deadline=self.missed_deadline,
        )


def hyperperiod(tasks: List[Task]) -> int:
    hp = tasks[0].T
    for t in tasks[1:]:
        hp = lcm(hp, t.T)
    return hp


def utilization(tasks: List[Task]) -> float:
    return sum(t.C / t.T for t in tasks)


def generate_jobs(tasks: List[Task], hp: int) -> List[Job]:
    jobs: List[Job] = []
    for task in tasks:
        num_jobs = hp // task.T
        for j in range(num_jobs):
            release = j * task.T
            absolute_deadline = release + task.D
            jobs.append(
                Job(
                    task_name=task.name,
                    job_id=j + 1,
                    release=float(release),
                    deadline=float(absolute_deadline),
                    execution=float(task.C),
                )
            )
    jobs.sort(key=lambda x: (x.release, x.deadline, x.task_name, x.job_id))
    return jobs


def is_job_allowed_to_miss(job: Job, allow_tau5_miss: bool) -> bool:
    return allow_tau5_miss and job.task_name == "τ5"


def choose_job_greedy(
    ready_jobs: List[Job],
    current_time: float,
    allow_tau5_miss: bool = False,
) -> Optional[Job]:

    candidates: List[Tuple[Tuple[float, ...], Job]] = []

    for job in ready_jobs:
        finish = current_time + job.execution
        miss = finish > job.deadline

        # Case 1 : aucun job ne peut rater
        if miss and not is_job_allowed_to_miss(job, allow_tau5_miss):
            continue

        waiting = current_time - job.release
        slack = job.deadline - finish

        # Case 2 : si τ5 peut rater, on la repousse après les autres tâches
        tau5_penalty = 1.0 if allow_tau5_miss and job.task_name == "τ5" else 0.0

        key = (
            tau5_penalty,
            job.deadline,
            waiting,
            slack,
            job.execution,
            float(job.job_id),
        )

        candidates.append((key, job))

    if candidates:
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1]

    return None

def schedule_non_preemptive(
    jobs: List[Job],
    allow_tau5_miss: bool = False,
) -> Tuple[List[Job], float]:
    unscheduled = [job.clone() for job in jobs]
    scheduled: List[Job] = []
    current_time = 0.0
    total_idle = 0.0

    while unscheduled:
        ready = [job for job in unscheduled if job.release <= current_time]

        if not ready:
            next_release = min(job.release for job in unscheduled)
            total_idle += next_release - current_time
            current_time = next_release
            ready = [job for job in unscheduled if job.release <= current_time]

        chosen = choose_job_greedy(ready, current_time, allow_tau5_miss=allow_tau5_miss)

        if chosen is None:
            # Aucun job "faisable" selon la contrainte; on choisit le plus urgent
            ready.sort(key=lambda x: (x.deadline, x.release, x.task_name, x.job_id))
            chosen = ready[0]

        chosen.start = current_time
        chosen.finish = current_time + chosen.execution
        chosen.waiting = chosen.start - chosen.release
        chosen.response_time = chosen.finish - chosen.release
        chosen.missed_deadline = chosen.finish > chosen.deadline

        scheduled.append(chosen)
        unscheduled.remove(chosen)
        current_time = chosen.finish

    return scheduled, total_idle


def check_schedule(scheduled_jobs: List[Job], allow_tau5_miss: bool = False) -> bool:
    for job in scheduled_jobs:
        if job.missed_deadline:
            if is_job_allowed_to_miss(job, allow_tau5_miss):
                continue
            return False
    return True


def total_waiting_time(scheduled_jobs: List[Job]) -> float:
    return sum(job.waiting or 0.0 for job in scheduled_jobs)


def total_idle_time(scheduled_jobs: List[Job]) -> float:
    idle = 0.0
    current = 0.0
    for job in scheduled_jobs:
        if job.start is not None and job.start > current:
            idle += job.start - current
        if job.finish is not None:
            current = job.finish
    return idle


def build_task_set(c1_value_ms: float) -> List[Task]:
    # Hypothèse: toutes les unités sont en millisecondes
    # Deadlines implicites: D = T
    return [
        Task("τ1", c1_value_ms, 10),
        Task("τ2", 3.0, 10),
        Task("τ3", 2.0, 20),
        Task("τ4", 2.0, 20),
        Task("τ5", 2.0, 40),
        Task("τ6", 2.0, 40),
        Task("τ7", 3.0, 80),
    ]


def print_task_set(tasks: List[Task]) -> None:
    print("Task set")
    print("Task\tC\tT\tD")
    for t in tasks:
        print(f"{t.name}\t{t.C:.6f}\t{t.T}\t{t.D}")


def print_jobs(jobs: List[Job], limit: int = 50) -> None:
    print("Jobs")
    print("Job\tRelease\tDeadline\tExecution")
    for job in jobs[:limit]:
        print(
            f"{job.task_name}_{job.job_id}\t"
            f"{job.release:.3f}\t"
            f"{job.deadline:.3f}\t"
            f"{job.execution:.3f}"
        )
    if len(jobs) > limit:
        print(f"... {len(jobs) - limit} more jobs")


def print_schedule_table(scheduled_jobs: List[Job], limit: int = 100) -> None:
    print("Schedule")
    print("Job\tRelease\tStart\tFinish\tDeadline\tWaiting\tResponse\tMiss")
    for job in scheduled_jobs[:limit]:
        print(
            f"{job.task_name}_{job.job_id}\t"
            f"{job.release:.3f}\t"
            f"{job.start:.3f}\t"
            f"{job.finish:.3f}\t"
            f"{job.deadline:.3f}\t"
            f"{job.waiting:.3f}\t"
            f"{job.response_time:.3f}\t"
            f"{job.missed_deadline}"
        )
    if len(scheduled_jobs) > limit:
        print(f"... {len(scheduled_jobs) - limit} more jobs")



#UTILS FOR ANALYZE SCHEDULES
def schedule_to_dataframe(scheduled_jobs: List[Job]) -> pd.DataFrame:
    rows = []
    for job in scheduled_jobs:
        rows.append({
            "job": f"{job.task_name}_{job.job_id}",
            "task": job.task_name,
            "job_id": job.job_id,
            "release_ms": job.release,
            "start_ms": job.start,
            "finish_ms": job.finish,
            "deadline_ms": job.deadline,
            "execution_ms": job.execution,
            "waiting_ms": job.waiting,
            "response_ms": job.response_time,
            "missed_deadline": job.missed_deadline,
        })
    return pd.DataFrame(rows)

#EXPORT CSV
def export_schedule_csv(scheduled_jobs: List[Job], filename: str) -> None:
    df = schedule_to_dataframe(scheduled_jobs)
    df.to_csv(filename, index=False)


#GANTT DIAGRAM

def plot_gantt(scheduled_jobs: List[Job], title: str, filename: str | None = None) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))

    task_names = sorted({job.task_name for job in scheduled_jobs})
    y_pos = {task: i for i, task in enumerate(task_names)}

    for job in scheduled_jobs:
        y = y_pos[job.task_name]
        start = job.start
        duration = job.execution
        color = "red" if job.missed_deadline else None
        ax.barh(y, duration, left=start, height=0.6, edgecolor="black", color=color)
        ax.text(start + duration / 2, y, f"{job.task_name}_{job.job_id}",
                va="center", ha="center", fontsize=8)

        # deadline marker
        ax.plot([job.deadline, job.deadline], [y - 0.3, y + 0.3], linestyle="--")

    ax.set_yticks(list(y_pos.values()))
    ax.set_yticklabels(task_names)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Tasks")
    ax.set_title(title)
    ax.grid(True, axis="x", linestyle=":")

    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=200, bbox_inches="tight")
    plt.show()

#Comparaison between the two cases(no miss vs tau5 may miss)
def plot_case_comparison(waiting_1: float, idle_1: float,
                         waiting_2: float, idle_2: float,
                         filename: str | None = None) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))

    labels = ["Case 1\nNo miss", "Case 2\nτ5 may miss"]
    waiting = [waiting_1, waiting_2]
    idle = [idle_1, idle_2]

    x = [0, 1]
    width = 0.35

    ax.bar([i - width/2 for i in x], waiting, width=width, label="Total waiting")
    ax.bar([i + width/2 for i in x], idle, width=width, label="Total idle")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Time (ms)")
    ax.set_title("Comparison of scheduling cases")
    ax.legend()
    ax.grid(True, axis="y", linestyle=":")

    plt.tight_layout()
    if filename:
        plt.savefig(filename, dpi=200, bbox_inches="tight")
    plt.show()