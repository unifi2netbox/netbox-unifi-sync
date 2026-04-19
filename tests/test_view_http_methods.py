from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIEWS_PATH = PROJECT_ROOT / "netbox_unifi_sync" / "views.py"
CONTROLLERS_TEMPLATE_PATH = (
    PROJECT_ROOT
    / "netbox_unifi_sync"
    / "templates"
    / "netbox_unifi_sync"
    / "controllers.html"
)


def _decorator_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _decorator_name(node.func)
    return ""


def test_controller_test_views_are_post_only():
    source = VIEWS_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    decorators_by_function: dict[str, set[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        decorators_by_function[node.name] = {
            _decorator_name(decorator) for decorator in node.decorator_list
        }

    assert "require_POST" in decorators_by_function.get("controller_test_view", set())
    assert "require_POST" in decorators_by_function.get(
        "controller_test_api_view", set()
    )


def test_controller_list_template_uses_post_for_test_action():
    template = CONTROLLERS_TEMPLATE_PATH.read_text(encoding="utf-8")
    assert (
        "<form method=\"post\" action=\"{% url 'plugins:netbox_unifi_sync:controller_test' c.pk %}\""
        in template
    )


def test_dashboard_sync_permission_accepts_standard_add_permission():
    source = VIEWS_PATH.read_text(encoding="utf-8")
    template = (
        PROJECT_ROOT
        / "netbox_unifi_sync"
        / "templates"
        / "netbox_unifi_sync"
        / "dashboard.html"
    ).read_text(encoding="utf-8")

    assert "netbox_unifi_sync.run_sync" in source
    assert "netbox_unifi_sync.add_syncrun" in source
    assert "{% if can_queue_sync %}" in template


def test_controller_test_permission_accepts_standard_change_permission():
    source = VIEWS_PATH.read_text(encoding="utf-8")

    assert "def _can_test_controller" in source
    assert "netbox_unifi_sync.test_controller" in source
    assert "netbox_unifi_sync.change_unificontroller" in source
