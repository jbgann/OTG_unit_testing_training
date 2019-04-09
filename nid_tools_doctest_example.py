import subprocess
import operator

#Don't worry about this class definition if you don't
#understand object oriented programming. All it does is define
#a new type of error for us
class NonexistentNodeError(Exception):
    pass

#broken, can you tell why?
def getNodeNumbersFromRange(rng):
    """
    >>> getNodeNumbersFromRange("111")
    [111]
    >>> getNodeNumbersFromRange("111-113")
    [111,112,113]
    """
    if "-" not in rng:
        return [int(rng)]
    #if the syntax between the square brackets below is unfamiliar
    #google "python list comprehensions"
    start, stop = [int(x) for x in rng.split("-")]
    return range(start,stop)


def get_node_list_from_pdsh_notation(annotation):
    """
    >>> get_node_list_from_pdsh_notation("nid12345")
    ['nid12345']
    >>> get_node_list_from_pdsh_notation("nid[00123-00125]")
    ['nid00123','nid00124','nid00125']
    """
    group_begin = annotation.find("[")
    if group_begin == -1: #find returns -1 if the substring isn't found
        return [annotation]
    prelude = annotation[:group_begin]
    groups = annotation[group_begin+1 : -1].split(",")
    groups = map(getNodeNumbersFromRange, groups)
    nids = reduce(operator.add, groups)
    nids = [prelude + str(nid).zfill(5) for nid in nids]
    return nids

def get_state(nid):
    """
    We can't write a doctest here because the function return
    value is dependent on system state!
    """
    slurm_info = subprocess.check_output("ssh cori sinfo",shell=True)
    slurm_info = slurm_info.splitlines()
    slurm_info = [line.split() for line in slurm_info]
    for entry in slurm_info[1:]:
        state = entry[4]
        nodelist = entry[5]
        if nid in get_node_list_from_pdsh_notation(nodelist):
            return state
    raise NonexistentNodeError
