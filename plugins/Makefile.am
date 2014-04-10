SUBDIRS = \
	volcap \
	$(NULL)

cronddir = $(sysconfdir)/cron.d
crond_DATA = \
	gluster-sysstat.crontab \
	$(NULL)

dist_glusternagiosplugins_PYTHON = \
	check_disk_and_inode.py \
	check_vol_utilization.py \
	check_vol_status.py \
	check_volume_status.py \
	cpu.py \
	discoverpeers.py \
	discoverlogicalcomponents.py \
	discoverhostparams.py \
	__init__.py \
	memory.py \
	network.py \
	sadf.py \
	swap.py \
	$(NULL)

EXTRA_DIST = \
	$(crond_DATA) \
	$(NULL)
