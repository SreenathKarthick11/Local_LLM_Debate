# ui/geometry.py
"""
Static geometry mirroring the fixed split ratios in ui/layout.py.
Keep this in sync if layout.py's splits ever change.
"""

HEADER_H = 3
FOOTER_H = 1

TOP_RATIO, MIDDLE_RATIO, BOTTOM_RATIO = 3, 2, 1
ROUTER_RATIO, RESOURCES_RATIO, DEBATE_RATIO = 1, 1, 2


def compute_regions(width: int, height: int):
    body_h = max(0, height - HEADER_H - FOOTER_H)

    ratio_total = TOP_RATIO + MIDDLE_RATIO + BOTTOM_RATIO
    top_h = body_h * TOP_RATIO // ratio_total
    middle_h = body_h * MIDDLE_RATIO // ratio_total
    bottom_h = body_h - top_h - middle_h  # remainder, matches Layout's own rounding behavior

    top_y0 = HEADER_H
    top_y1 = top_y0 + top_h

    middle_y0 = top_y1
    middle_y1 = middle_y0 + middle_h

    bottom_y0 = middle_y1
    bottom_y1 = bottom_y0 + bottom_h

    # --- top row: router / resources / agent_a / agent_b ---
    col_total = ROUTER_RATIO + RESOURCES_RATIO + DEBATE_RATIO
    router_w = width * ROUTER_RATIO // col_total
    resources_w = width * RESOURCES_RATIO // col_total
    debate_w = width - router_w - resources_w

    router_x0, router_x1 = 0, router_w
    resources_x0, resources_x1 = router_w, router_w + resources_w
    debate_x0 = router_w + resources_w
    agent_a_x0, agent_a_x1 = debate_x0, debate_x0 + debate_w // 2
    agent_b_x0, agent_b_x1 = agent_a_x1, width

    # --- middle row: critique_a / critique_b (even split) ---
    critique_a_x0, critique_a_x1 = 0, width // 2
    critique_b_x0, critique_b_x1 = width // 2, width

    # --- bottom row: judge / runtime (even split) ---
    judge_x0, judge_x1 = 0, width // 2
    runtime_x0, runtime_x1 = width // 2, width

    return {
        "router": (router_x0, top_y0, router_x1, top_y1),
        "resources": (resources_x0, top_y0, resources_x1, top_y1),
        "agent_a": (agent_a_x0, top_y0, agent_a_x1, top_y1),
        "agent_b": (agent_b_x0, top_y0, agent_b_x1, top_y1),
        "critique_a": (critique_a_x0, middle_y0, critique_a_x1, middle_y1),
        "critique_b": (critique_b_x0, middle_y0, critique_b_x1, middle_y1),
        "judge": (judge_x0, bottom_y0, judge_x1, bottom_y1),
        "runtime": (runtime_x0, bottom_y0, runtime_x1, bottom_y1),
    }


def viewport_size(box):
    """Content width/height inside a Panel's border+default padding."""
    x0, y0, x1, y1 = box
    width = max(1, (x1 - x0) - 4)   # 2 border cols + 2 padding cols
    height = max(1, (y1 - y0) - 2)  # top+bottom border rows
    return width, height


def hit_test(regions: dict, col: int, row: int):
    """col/row are 1-indexed terminal coordinates from mouse reports."""
    x, y = col - 1, row - 1
    for name, (x0, y0, x1, y1) in regions.items():
        if x0 <= x < x1 and y0 <= y < y1:
            return name
    return None