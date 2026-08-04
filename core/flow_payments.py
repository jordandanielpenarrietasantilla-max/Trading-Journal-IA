def _commerce_order(
    *,
    user_id: str,
    plan_code: str,
) -> str:
    """
    Genera un commerceOrder único de máximo 45 caracteres.

    Flow rechaza valores superiores a 45 caracteres.
    El user_id y el plan completo siguen viajando por
    separado dentro del campo optional.
    """

    normalized_plan = str(
        plan_code
        or ""
    ).strip().upper()

    plan_aliases = {
        "PRO_MONTHLY": "PM",
        "PRO_ANNUAL": "PA",
    }

    plan_tag = plan_aliases.get(
        normalized_plan,
        "PX",
    )

    clean_user = re.sub(
        r"[^A-Za-z0-9]",
        "",
        str(
            user_id
            or ""
        ),
    )[:8]

    if not clean_user:
        clean_user = "USER"

    unique = uuid.uuid4().hex[:20]

    commerce_order = (
        f"AX-{plan_tag}-"
        f"{clean_user}-"
        f"{unique}"
    )

    return commerce_order[:45]
