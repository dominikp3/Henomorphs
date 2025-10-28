import math
from lib.Colors import Colors
from lib.FileLogger import FileLogger


class Summarizer:
    def __init__(self, pol, zico, ylw):
        self._last_pol = self._g_last_pol = pol
        self._last_zico = self._g_last_zico = zico
        self._last_ylw = self._g_last_ylw = ylw

    def _printTokens(self, pol, zico, ylw, colorize=False, c_d=""):
        p_c, z_c, y_c = "", "", ""
        if colorize:
            p_c = Colors.OKGREEN if pol >= 0 else Colors.FAIL
            z_c = Colors.OKGREEN if zico >= 0 else Colors.FAIL
            y_c = Colors.OKGREEN if ylw >= 0 else Colors.FAIL
        print(f"{c_d}$POL: {p_c}{pol}")
        print(f"{c_d}$ZICO: {z_c}{zico}")
        print(f"{c_d}$YLW: {y_c}{ylw}{Colors.ENDC}")

    def printBalances(self):
        self._printTokens(self._last_pol, self._last_zico, self._last_ylw)

    def printSummary(self, pol, zico, ylw):
        if not (math.isclose(self._last_pol, pol) and math.isclose(self._last_zico, zico)):
            print(f"{Colors.OKBLUE}{"-" * 50}")
            print(f"{Colors.OKCYAN}Changes after operation: ")
            self._printTokens(pol - self._last_pol, zico - self._last_zico, ylw - self._last_ylw, True, Colors.OKBLUE)
            print(f"{Colors.OKCYAN}Total changes in current session: ")
            self._printTokens(pol - self._g_last_pol, zico - self._g_last_zico, ylw - self._g_last_ylw, True, Colors.OKBLUE)
            print(f"{Colors.OKBLUE}{"-" * 50}{Colors.ENDC}")
            FileLogger().log(f"CHANGES AFTER OPERATION: $POL: {pol - self._last_pol}, $ZICO: {zico - self._last_zico}, $YLW: {ylw - self._last_ylw}")
        self._last_pol, self._last_zico, self._last_ylw = pol, zico, ylw
