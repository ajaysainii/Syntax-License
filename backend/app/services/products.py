SYNTAX_PRODUCT_CANONICAL = "syntax"
SYNTAX_PRODUCT_ALIASES = {
    "syntax",
    "syntax-cli",
    "syntax-desktop",
}


def normalize_product_name(product: str) -> str:
    normalized = product.strip().lower()
    if normalized in SYNTAX_PRODUCT_ALIASES:
        return SYNTAX_PRODUCT_CANONICAL
    return normalized


def product_match_names(product: str) -> set[str]:
    normalized = normalize_product_name(product)
    if normalized == SYNTAX_PRODUCT_CANONICAL:
        return set(SYNTAX_PRODUCT_ALIASES)
    return {normalized}
