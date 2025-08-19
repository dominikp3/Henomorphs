from lib.HenoActions import HenoActions
from lib.HenoInspect import HenoInspect
from lib.HenoPrint import HenoPrint
from lib.HenoRepair import HenoRepair
from lib.HenoZico import HenoZico


class Henomorphs(HenoPrint, HenoInspect, HenoActions, HenoRepair, HenoZico):
    pass
