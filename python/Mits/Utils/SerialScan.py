# Win32 serial port scanner from PySerial.
import ctypes
import serial
def ValidHandle(value):
NULL = 0
class GUID(ctypes.Structure):
class SP_DEVINFO_DATA(ctypes.Structure):
class SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
PSP_DEVICE_INTERFACE_DATA = ctypes.POINTER(SP_DEVICE_INTERFACE_DATA)
PSP_DEVICE_INTERFACE_DETAIL_DATA = ctypes.c_void_p
class dummy(ctypes.Structure):
SetupDiDestroyDeviceInfoList = ctypes.windll.setupapi.SetupDiDestroyDeviceInfoList
SetupDiGetClassDevs = ctypes.windll.setupapi.SetupDiGetClassDevsA
SetupDiEnumDeviceInterfaces = ctypes.windll.setupapi.SetupDiEnumDeviceInterfaces
SetupDiGetDeviceInterfaceDetail = ctypes.windll.setupapi.SetupDiGetDeviceInterfaceDetailA
SetupDiGetDeviceRegistryProperty = ctypes.windll.setupapi.SetupDiGetDeviceRegistryPropertyA

GUID_CLASS_COMPORT = GUID(0x86e0d1e0L, 0x8089, 0x11d0,
DIGCF_PRESENT = 2
class WinScan():
    def comports(available_only=True):
            if not SetupDiEnumDeviceInterfaces(
            dwNeeded = DWORD()
            # hardware ID
            # friendly name
        SetupDiDestroyDeviceInfoList(g_hdi)
'''
    for order, port, desc, hwid in sorted(comports()):
    #
    try:
    #