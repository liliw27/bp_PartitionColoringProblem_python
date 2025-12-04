"""
将 PCP 算例（如 n20p5t2s1.pcp）尝试映射为“充电时间区间”：

- 边 (i,j) ⇒ 两个时间区间必须有重叠；
- 非边 ⇒ 两个时间区间必须无重叠。

做法：
- 使用 Gurobi 搭一个小 MILP，搜索一组区间 [s_i, e_i]（整数端点），
  满足上面的交叠/不交叠约束；
- 若无可行解，则说明该图不能严格表示为区间图；
- 若有解，则导出一个简单的 EV 算例 JSON，便于后续实验。

只演示用：默认读取 data/Table2_random_instances/n20p5t2s1.pcp。
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

import gurobipy as gp
from gurobipy import GRB

from test.pcp_reader import PCPReader


def load_pcp_graph(path: str):
    """读取 PCP 文件并返回 (graph, 顶点数, 边集合)。"""
    reader = PCPReader()
    graph = reader.read_pcp_file(path)

    n = len(graph.vertices)
    edges: set[Tuple[int, int]] = set()
    for e in graph.edges:
        i = e.source.id
        j = e.target.id
        if i == j:
            continue
        if i > j:
            i, j = j, i
        edges.add((i, j))

    return graph, n, edges


def build_interval_mip(n: int, edges: set[Tuple[int, int]], horizon: int = 48):
    """构建“区间嵌入”MILP 模型：为 n 个顶点构造时间区间。

    当前假设：
    - 每个充电时段长度固定为 2 小时；
    - 可用时间窗口为 [0, horizon]，这里 horizon = 48（小时）。
    """
    m = gp.Model("pcp_interval_embedding")
    m.Params.OutputFlag = 0

    # 时间端点与长度（整数）
    s = m.addVars(n, lb=0, ub=horizon, vtype=GRB.CONTINUOUS, name="s")
    # 充电时段长度固定为 2 小时
    l = m.addVars(n, lb=0.5, ub=horizon, vtype=GRB.CONTINUOUS, name="l")

    # 非边用二进制变量表示左右相对顺序
    # y_ij = 0 ⇒ i 在 j 左边：s_i + l_i <= s_j
    # y_ij = 1 ⇒ j 在 i 左边：s_j + l_j <= s_i
    y = {}

    M = horizon  # big-M

    # 边约束：区间必须有交集
    for i in range(n):
        for j in range(i + 1, n):
            if (i, j) in edges:
                # s_i <= s_j + l_j - 1  且  s_j <= s_i + l_i - 1
                m.addConstr(s[i] <= s[j] + l[j] - 1, name=f"edge_overlap1_{i}_{j}")
                m.addConstr(s[j] <= s[i] + l[i] - 1, name=f"edge_overlap2_{i}_{j}")
            else:
                # 非边：区间必须不相交
                var = m.addVar(vtype=GRB.BINARY, name=f"y_{i}_{j}")
                y[(i, j)] = var
                # i 在 j 左边 或 j 在 i 左边（二者至少一个成立）
                # s_i + l_i <= s_j + M*(1 - y_ij)
                m.addConstr(
                    s[i] + l[i] <= s[j] + M * (1 - var),
                    name=f"nonedge1_{i}_{j}",
                )
                # s_j + l_j <= s_i + M*y_ij
                m.addConstr(
                    s[j] + l[j] <= s[i] + M * var,
                    name=f"nonedge2_{i}_{j}",
                )

    # 目标随意：例如最小化总时长，主要是为了求一个可行解
    m.setObjective(gp.quicksum(l[i] for i in range(n)), GRB.MINIMIZE)
    return m, s, l


def solve_intervals_for_pcp(path: str, horizon: int = 48):
    graph, n, edges = load_pcp_graph(path)
    m, s, l = build_interval_mip(n, edges, horizon=horizon)
    m.optimize()

    if m.Status != GRB.OPTIMAL:
        print(f"图可能不是区间图：在 horizon={horizon} 下未找到满足边/非边语义的时间区间。")
        return None, None, None

    intervals: Dict[int, Tuple[int, int]] = {}
    for i in range(n):
        si = int(round(s[i].X))
        li = int(round(l[i].X))
        intervals[i] = (si, si + li)

    return graph, intervals, m.ObjVal


def export_ev_instance_from_intervals(
    graph, intervals: Dict[int, Tuple[int, int]], out_path: str, num_chargers: int | None = None
):
    """基于区间结果导出一个简单的 EV 充电算例 JSON。"""
    if num_chargers is None:
        # 简单起见，设为分区数的一半（向上取整）
        num_chargers = max(1, (len(graph.partitions) + 1) // 2)

    time_horizon = max(e for (_, e) in intervals.values())

    vehicles = []
    # 每个 partition = 一辆车；partition.vertex_list 中的每个顶点是该车的一个候选方案
    for pid, partition in enumerate(graph.partitions):
        cand = []
        for v in partition.vertex_list:
            if v.id not in intervals:
                continue
            s, e = intervals[v.id]
            cand.append(
                {
                    "vertex_id": v.id,
                    "charger_id": 0,  # 这里只做时间重叠演示，暂设为同一桩
                    "start": s,
                    "end": e,
                }
            )
        vehicles.append(
            {
                "id": pid,
                "duration": None,  # 可选：也可以存 e - s
                "candidates": cand,
            }
        )

    inst = {
        "source_pcp": os.path.basename(out_path),
        "time_horizon": time_horizon,
        "num_chargers": num_chargers,
        "vehicles": vehicles,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(inst, f, ensure_ascii=False, indent=2)

    print(f"EV instance written to {out_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pcp_path = os.path.join(
        base_dir, "data", "Table2_random_instances", "n20p5t2s1.pcp"
    )

    print(f"Solving interval embedding for PCP instance: {pcp_path}")
    graph, intervals, obj = solve_intervals_for_pcp(pcp_path, horizon=48)
    if intervals is None:
        exit(1)

    print("Found intervals (vertex_id: [start, end)):")
    for vid in sorted(intervals.keys()):
        s, e = intervals[vid]
        print(f"  v{vid}: [{s}, {e})")

    out_dir = os.path.join(base_dir, "data", "ev_from_pcp")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ev_from_n20p5t2s1.json")
    export_ev_instance_from_intervals(graph, intervals, out_path)


