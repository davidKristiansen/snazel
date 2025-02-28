import logging
from graphlib import TopologicalSorter

from snazel.rule import Rule

logger = logging.getLogger(__name__)


def build(rule_str: str):
    rules: dict[str, Rule] = dict()
    dependency_stack: list[str] = [rule_str]
    dependency_graph: dict[str, list[str]] = dict()

    while len(dependency_stack) != 0:
        dependency = dependency_stack.pop()
        if dependency in rules:
            continue

        rule = Rule(dependency)
        dependency_stack.extend(rule.dependencies)
        rules[str(rule)] = rule
        dependency_graph[str(rule)] = rule.dependencies

    ts = TopologicalSorter(dependency_graph)
    print(dependency_graph)
    print(tuple(ts.static_order()))



