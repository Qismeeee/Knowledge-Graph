def normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip("/").removeprefix("./")


def org_id(org_name: str) -> str:
    return org_name


def repo_id(org_name: str, repo_name: str) -> str:
    return f"{org_name}/{repo_name}"


def workspace_id(org_name: str, repo_name: str, path: str = ".") -> str:
    return f"{org_name}/{repo_name}:ws:{path}"


def file_id(org_name: str, repo_name: str, file_path: str) -> str:
    return f"{org_name}/{repo_name}:{normalize_path(file_path)}"


def symbol_id(
    org_name: str, repo_name: str, file_path: str, kind: str, qualified_name: str
) -> str:
    return f"{org_name}/{repo_name}:{normalize_path(file_path)}#{kind}:{qualified_name}"


def indexrun_id(org_name: str, repo_name: str, commit_sha: str, epoch: int) -> str:
    return f"run:{org_name}/{repo_name}:{commit_sha[:8]}:{epoch}"
