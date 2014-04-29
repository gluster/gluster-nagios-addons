SUBDIRS = \
	volcap \
	$(NULL)

initdir = $(sysconfdir)/init.d
init_DATA = \
	glusterpmd \
	$(NULL)

cronddir = $(sysconfdir)/cron.d
crond_DATA = \
	gluster-sysstat.crontab \
	$(NULL)

dist_glusternagiosplugins_PYTHON = \
	check_disk_and_inode.py \
	check_gluster_syslog.py \
	check_vol_utilization.py \
	check_vol_status.py \
	check_volume_status.py \
	check_proc_status.py \
	cpu.py \
	discoverpeers.py \
	discover_volumes.py \
	discoverhostparams.py \
	configure_gluster_node.py \
	__init__.py \
	memory.py \
	network.py \
	nscautils.py \
	sadf.py \
	swap.py \
	$(NULL)

EXTRA_DIST = \
	$(init_DATA) \
	$(crond_DATA) \
	$(NULL)
