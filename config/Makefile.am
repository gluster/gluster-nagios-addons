rsyslogconfdir = $(sysconfdir)/rsyslog.d
rsyslogconf_DATA = \
	glusternagios.conf \
	$(NULL)

nagiosconfdir = $(sysconfdir)/nagios
nagiosconf_DATA = \
	nagios_server.conf \
	$(NULL)

sudodir = $(sysconfdir)/sudoers.d/
sudo_DATA = \
	nrpe \
	$(NULL)

EXTRA_DIST = \
	$(nagiosconf_DATA) \
	$(rsyslogconf_DATA) \
	$(sudo_DATA) \
	$(NULL)
