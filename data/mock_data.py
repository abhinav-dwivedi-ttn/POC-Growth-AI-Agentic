employees = {
    1024: {
        "id": 1024,
        "username": "john.doe",
        "legal_entity": "INDIA",
        "status": "ACTIVE"
    }
}

user_policies = {
    1024: {
        "employee_id": 1024,
        "policy_type": "DPDP",
        "verified": False,
        "event": "EXIT"
    }
}

logs = [
    "Employee 1024 found with ACTIVE status",
    "DPDP policy assignment started for employee 1024",
    "Existing UserPolicy found for employee 1024",
    "UserPolicy event EXIT - skipping policy assignment",
    "DPDP policy assignment completed"
]

errors = [
    {
        "service": "policy-service",
        "error": "UserPolicy skipped because event=EXIT",
        "employee_id": 1024
    }
]