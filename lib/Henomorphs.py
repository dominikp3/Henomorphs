from lib.ColonyWarsTeritory import ColonyWarsTeritory
from lib.ColonyWars import ColonyWars
from lib.HenoActions import HenoActions
from lib.HenoInspect import HenoInspect
from lib.HenoPrint import HenoPrint
from lib.HenoRepair import HenoRepair
from lib.HenoSpec import HenoSpec
from lib.HenoZico import HenoZico


class Henomorphs(HenoPrint, HenoInspect, HenoActions, HenoRepair, HenoZico, HenoSpec, ColonyWarsTeritory):
    pass
