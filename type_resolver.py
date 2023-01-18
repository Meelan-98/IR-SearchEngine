
def query_type_resolver(conditions):
    if conditions[0] == True:
        return("title_only")
    elif conditions[1] == True:
        return("metaphors_only")
    elif conditions[2] == True:
        return("composers_only")
    elif conditions[3] == True:
        return("anywhere")