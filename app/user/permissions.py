from dataclasses import dataclass

MANAGER_GROUP_PERMISSIONS = [
    "can_view_department_clients",
    "can_create_department_clients",
    "can_update_department_clients",
    "can_delete_department_clients",
    "can_view_department_sales",
    "can_create_department_sales",
    "can_update_department_sales",
    "can_delete_department_sales",
    "can_view_department_roadmaps",
    "can_create_department_roadmaps",
    "can_update_department_roadmaps",
    "can_delete_department_roadmaps",
]

TEAMLEADER_GROUP_PERMISSIONS = [
    "can_view_my_group_clients",
    "can_create_my_group_clients",
    "can_update_my_group_clients",
    "can_delete_my_group_clients",
    "can_view_my_group_sales",
    "can_create_my_group_sales",
    "can_update_my_group_sales",
    "can_delete_my_group_sales",
    "can_view_my_group_roadmaps",
    "can_create_my_group_roadmaps",
    "can_update_my_group_roadmaps",
    "can_delete_my_group_roadmaps",
]

TRADER_GROUP_PERMISSIONS = [
    "can_view_only_my_clients",
    "can_create_only_my_clients",
    "can_update_only_my_clients",
    "can_delete_only_my_clients",
    "can_view_only_my_sales",
    "can_create_only_my_sales",
    "can_update_only_my_sales",
    "can_delete_only_my_sales",
    "can_view_only_my_roadmaps",
    "can_create_only_my_roadmaps",
    "can_update_only_my_roadmaps",
    "can_delete_only_my_roadmaps",
]


@dataclass
class TraderPermissions:
    can_view_only_my_clients: str = "crm.can_view_only_my_clients"
    can_create_only_my_clients: str = "crm.can_create_only_my_clients"
    can_update_only_my_clients: str = "crm.can_update_only_my_clients"
    can_delete_only_my_clients: str = "crm.can_delete_only_my_clients"
    can_view_only_my_sales: str = "crm.can_view_only_my_sales"
    can_create_only_my_sales: str = "crm.can_create_only_my_sales"
    can_update_only_my_sales: str = "crm.can_update_only_my_sales"
    can_delete_only_my_sales: str = "crm.can_delete_only_my_sales"
    can_view_only_my_roadmaps: str = "crm.can_view_only_my_roadmaps"
    can_create_only_my_roadmaps: str = "crm.can_create_only_my_roadmaps"
    can_update_only_my_roadmaps: str = "crm.can_update_only_my_roadmaps"
    can_delete_only_my_roadmaps: str = "crm.can_delete_only_my_roadmaps"


@dataclass
class TeamleaderPermissions:
    can_view_my_group_clients: str = "crm.can_view_my_group_clients"
    can_create_my_group_clients: str = "crm.can_create_my_group_clients"
    can_update_my_group_clients: str = "crm.can_update_my_group_clients"
    can_delete_my_group_clients: str = "crm.can_delete_my_group_clients"
    can_view_my_group_sales: str = "crm.can_view_my_group_sales"
    can_create_my_group_sales: str = "crm.can_create_my_group_sales"
    can_update_my_group_sales: str = "crm.can_update_my_group_sales"
    can_delete_my_group_sales: str = "crm.can_delete_my_group_sales"
    can_view_my_group_roadmaps: str = "crm.can_view_my_group_roadmaps"
    can_create_my_group_roadmaps: str = "crm.can_create_my_group_roadmaps"
    can_update_my_group_roadmaps: str = "crm.can_update_my_group_roadmaps"
    can_delete_my_group_roadmaps: str = "crm.can_delete_my_group_roadmaps"


@dataclass
class ManagerPermissions:
    can_view_department_clients: str = "crm.can_view_department_clients"
    can_create_department_clients: str = "crm.can_create_department_clients"
    can_update_department_clients: str = "crm.can_update_department_clients"
    can_delete_department_clients: str = "crm.can_delete_department_clients"
    can_view_department_sales: str = "crm.can_view_department_sales"
    can_create_department_sales: str = "crm.can_create_department_sales"
    can_update_department_sales: str = "crm.can_update_department_sales"
    can_delete_department_sales: str = "crm.can_delete_department_sales"
    can_view_department_roadmaps: str = "crm.can_view_department_roadmaps"
    can_create_department_roadmaps: str = "crm.can_create_department_roadmaps"
    can_update_department_roadmaps: str = "crm.can_update_department_roadmaps"
    can_delete_department_roadmaps: str = "crm.can_delete_department_roadmaps"
