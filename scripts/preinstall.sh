#!/usr/bin/env bash
# Check and create the scripting_users POSIX group if not exist already.
# Parameters scripting_group and scripting_gid will be passed from mvn
/usr/bin/getent group ${scripting_group} > /dev/null 2>&1 || /usr/sbin/groupadd -g ${scripting_gid} ${scripting_group}
