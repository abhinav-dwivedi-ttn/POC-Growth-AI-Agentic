from mcp.server.fastmcp import FastMCP

from data.mock_data import employees, user_policies, logs, errors


mcp = FastMCP("developer-support")


@mcp.tool()
def get_employee(employee_id: int) -> dict:
    """Get employee details by employee ID."""

    employee = employees.get(employee_id)

    if not employee:
        return {
            "error": f"Employee {employee_id} not found"
        }

    return employee


@mcp.tool()
def get_user_policy(employee_id: int) -> dict:
    """Get DPDP UserPolicy details for an employee."""

    policy = user_policies.get(employee_id)

    if not policy:
        return {
            "error": f"No UserPolicy found for employee {employee_id}"
        }

    return policy


@mcp.tool()
def search_logs(keyword: str) -> list:
    """Search application logs using a keyword."""

    return [
        log for log in logs
        if keyword.lower() in log.lower()
    ]


@mcp.tool()
def get_recent_errors(service: str) -> list:
    """Get recent errors for a service."""

    return [
        error
        for error in errors
        if error["service"].lower() == service.lower()
    ]


if __name__ == "__main__":
    mcp.run()