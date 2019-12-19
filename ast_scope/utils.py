def name_of_alias(alias_node):
    if alias_node.asname is not None:
        return alias_node.asname
    return alias_node.name
