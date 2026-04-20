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
MAPPINGS_TEMPLATE_PATH = (
    PROJECT_ROOT
    / "netbox_unifi_sync"
    / "templates"
    / "netbox_unifi_sync"
    / "mappings.html"
)
SETTINGS_TEMPLATE_PATH = (
    PROJECT_ROOT
    / "netbox_unifi_sync"
    / "templates"
    / "netbox_unifi_sync"
    / "settings.html"
)
URLS_PATH = PROJECT_ROOT / "netbox_unifi_sync" / "urls.py"


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


def test_plugin_changelog_routes_and_links_are_registered():
    urls = URLS_PATH.read_text(encoding="utf-8")
    controllers_template = CONTROLLERS_TEMPLATE_PATH.read_text(encoding="utf-8")
    mappings_template = MAPPINGS_TEMPLATE_PATH.read_text(encoding="utf-8")
    settings_template = SETTINGS_TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "ObjectChangeLogView" in urls
    assert "settings_changelog" in urls
    assert "controller_changelog" in urls
    assert "mapping_changelog" in urls
    assert "controller_changelog" in controllers_template
    assert "mapping_changelog" in mappings_template
    assert "settings_changelog" in settings_template


def test_api_urls_have_reverseable_namespace():
    urls = URLS_PATH.read_text(encoding="utf-8")

    assert "namespace=\"api\"" in urls
    assert "netbox_unifi_sync_api" in urls


def test_plugin_update_views_snapshot_before_save():
    source = VIEWS_PATH.read_text(encoding="utf-8")

    assert "settings_obj.snapshot()" in source
    assert "controller.snapshot()" in source
    assert "mapping.snapshot()" in source
