import logging
from graphlib import TopologicalSorter

from snazel.rule import Rule
from snazel.path import cwd

logger = logging.getLogger(__name__)


def build(rule_str: str):
    rules: dict[str, Rule] = dict()
    root_rule = Rule(rule_str, workdir=cwd)
    rules[str(root_rule)] = root_rule

    dependency_stack: list[str] = root_rule._dependencies
    dependency_graph: dict[str, list[str]] = dict()
    dependency_graph[str(root_rule)] = root_rule.dependencies

    while len(dependency_stack) != 0:
        dependency = dependency_stack.pop()
        if dependency in rules:
            continue

        rule = Rule(dependency)
        dependency_stack.extend(rule._dependencies)
        rules[str(rule)] = rule
        dependency_graph[str(rule)] = rule.dependencies

    ts = TopologicalSorter(dependency_graph)
    print(tuple(ts.static_order()))



