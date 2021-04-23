import re


class LinuxMount(object):
    def __init__(self, mount_line: str):
        self.fs_spec, on, self.fs_file, type, self.fs_vfstype, self.fs_mntopts = mount_line.strip().split()
        if on != "on" or type != "type":
            raise Exception()

        self.fs_mntopts = self.fs_mntopts.replace('(', '').replace(')', '')

        self.opts = {}
        for option in re.split(r'[,;]', self.fs_mntopts):
            if "=" in option:
                key, value = option.split('=')
            else:
                key, value = option, True
            self.opts[key] = value

    def __str__(self):
        return ' '.join([self.fs_spec, "on", self.fs_file, "type", self.fs_vfstype, self.fs_mntopts])
