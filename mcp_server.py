import datetime
from logging import DEBUG, INFO, Formatter, FileHandler, getLogger
import os
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP

# MCPサーバの起動時に環境変数として事前に設定しておく
# API_TOKENはTest Managerの然るべきユーザ権限で発行しておく
API_TOKEN = os.getenv("API_TOKEN")
DJANGO_API_BASE_URL = os.getenv("DJANGO_API_BASE_URL")


logger = getLogger(__name__)
handler = FileHandler("./mcp.log")
logger.addHandler(handler)
logger.setLevel(DEBUG)
handler.setLevel(DEBUG)
handler.setFormatter(Formatter("%(asctime)s %(levelname)7s %(message)s"))

logger.info(f"Launching Test Manager MCP Server (url: {DJANGO_API_BASE_URL})")

mcp = FastMCP("Test Manager on MCP")


def _api_get(api_url: str, timeout: int = 10) -> Any:
    headers = {"Authorization": f"Token {API_TOKEN}"}
    try:
        response = requests.get(api_url, headers=headers, timeout=timeout)
        return response.json()
    except RuntimeError as e:
        return {"error": f"get_projects() failed (url: {api_url}, message: {str(e)})"}


@mcp.resource("tm://projects")
def get_projects():
    """シナリオテストのプロジェクト一覧を取得する"""
    logger.debug("get_projects()")
    return _api_get(f"{DJANGO_API_BASE_URL}/api/projects/")


@mcp.resource("tm://test_sessions/{project_id}")
def get_test_sessions(project_id):
    """指定したプロジェクトIDのテストセッション一覧を取得する"""
    logger.debug(f"get_test_sessions(project_id: {project_id})")
    return _api_get(f"{DJANGO_API_BASE_URL}/api/projects/{project_id}/test-sessions/")


@mcp.resource("tm://test_executions/{session_id}")
def get_test_execution_detail(session_id: int):
    """指定したテストセッションのテスト実行状況を取得する"""
    logger.debug(f"get_test_execution_detail(session_id: {session_id})")
    return _api_get(f"{DJANGO_API_BASE_URL}/api/test-sessions/{session_id}/execute/")


@mcp.resource("tm://test_case/{test_case_id}")
def get_test_case(test_case_id: int):
    """指定したテストケースの詳細を取得する"""
    logger.debug(f"get_test_case(test_case_id: {test_case_id})")
    return _api_get(f"{DJANGO_API_BASE_URL}/api/testcases/{test_case_id}")


@mcp.tool()
def create_new_test_session(project_id: int, session_name: str = None) -> int:
    """指定したプロジェクトに対して新しいテストセッションを作成して、そのテストセッションのIDを得る"""
    if not session_name:
        now = datetime.datetime.now()
        session_name = "MCPセッション {}".format(now.strftime("%Y-%m-%d %H:%M"))
    logger.debug(f"create_new_session(project_id: {project_id}, session_name: {session_name})")

    api_url = f"{DJANGO_API_BASE_URL}/api/projects/{project_id}/test-sessions/"
    headers = {"Authorization": f"Token {API_TOKEN}"}
    json_data = {
        "project": project_id,
        "name": session_name,
        "description": "Description",
        "executed_by": "testuser",
        "environment": "Test Env",
    }
    try:

        response = requests.post(api_url, headers=headers, json=json_data, timeout=10)
        return response.json()
    except RuntimeError as e:
        return {"error": f"Failed to fetch projects: {str(e)}"}


def _mark_as_completed(test_session_id: int, test_case_id: int, status: str):
    """指定したテストセッション中のテストケースが完了状態にする。
    statusは"PASS", "FAIL", "BLOCKED", "SKIPPED"のいずれか"""
    assert status in ["PASS", "FAIL", "BLOCKED", "SKIPPED"]
    api_url = f"{DJANGO_API_BASE_URL}/api/test-sessions/{test_session_id}/execute/"
    headers = {"Authorization": f"Token {API_TOKEN}"}
    json_data = {
        "test_case_id": test_case_id,
        "status": status,
    }
    try:
        response = requests.post(api_url, headers=headers, json=json_data, timeout=10)
        return response.json()
    except RuntimeError as e:
        return {"error": f"Failed to fetch projects: {str(e)}"}


@mcp.tool()
def mark_as_passed(test_session_id: int, test_case_id: int) -> int:
    """指定したテストセッション中のテストケースが成功したと記録する"""
    return _mark_as_completed(test_session_id=test_session_id,
                             test_case_id=test_case_id,
                             status="PASS")


@mcp.tool()
def mark_as_failed(test_session_id: int, test_case_id: int) -> int:
    """指定したテストセッション中のテストケースが失敗したと記録する"""
    return _mark_as_completed(test_session_id=test_session_id,
                             test_case_id=test_case_id,
                             status="FAIL")


@mcp.tool()
def mark_as_blocked(test_session_id: int, test_case_id: int) -> int:
    """指定したテストセッション中のテストケースがブロックされたと記録する"""
    return _mark_as_completed(test_session_id=test_session_id,
                             test_case_id=test_case_id,
                             status="BLOCKED")


@mcp.tool()
def mark_as_skipped(test_session_id: int, test_case_id: int) -> int:
    """指定したテストセッション中のテストケースをスキップする"""
    return _mark_as_completed(test_session_id=test_session_id,
                             test_case_id=test_case_id,
                             status="SKIPPED")
