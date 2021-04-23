"""Custom errors.
"""


class WslException(Exception):
    pass


class WsdlPerquisiteFailed(WslException):
    pass


class IncompatiblePlatform(WsdlPerquisiteFailed):
    pass


class WslCommandFailed(WslException):
    pass


class WslNoInstalledDistributions(WslCommandFailed):
    pass


class WslExportFailed(WslCommandFailed):
    pass


class WslImportFailed(WslCommandFailed):
    pass


class WslImportFailedDuplicate(WslImportFailed):
    pass


class WslImportFailedInstallLocationInUse(WslImportFailed):
    pass


class WslUnregisterFailed(WslCommandFailed):
    pass
