cronddir = $(sysconfdir)/cron.d
crond_DATA = \
	gluster-sysstat.crontab \
	$(NULL)

dist_glusternagiosplugins_PYTHON = \
	check_disk_and_inode.py \
	check_remote_host.py \
	gluster_host_service_handler.py \
	sadf.py \
	$(NULL)

EXTRA_DIST = \
	$(crond_DATA) \
	__init__.py \
	$(NULL)
