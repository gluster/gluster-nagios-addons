cronddir = $(sysconfdir)/cron.d
crond_DATA = \
	gluster-sysstat.crontab \
	$(NULL)

dist_glusternagiosplugins_PYTHON = \
	check_disk_and_inode.py \
	cpu.py \
	__init__.py \
	memory.py \
	network.py \
	sadf.py \
	swap.py \
	$(NULL)

EXTRA_DIST = \
	$(crond_DATA) \
	$(NULL)
