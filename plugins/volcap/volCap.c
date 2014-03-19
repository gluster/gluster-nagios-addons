#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <time.h>
#include <sys/types.h>
#include <sys/statvfs.h>
#include "/usr/include/glusterfs/api/glfs.h"
#include "/usr/include/glusterfs/api/glfs-handles.h"
#include <syslog.h>

#define USAGE_ERROR -1 
#define GLFS_NEW_FAILURE -2 
#define GLFS_INIT_FAILURE -3 
#define GLFS_STATVFS_FAILURE -4 
#define GLFS_FINI_FAILURE -5 
#define DEFAULT_TRANSPORT "tcp" 
#define DEFAULT_SERVER "127.0.0.1" 
#define DEFAULT_SERVER_PORT 24007

static PyObject *StatvfsError;

int get_volume_statvfs (const char *volume_name, const char *server_name, struct statvfs *buf)
{
  glfs_t *fs = NULL;
  int ret = 0;
  struct statvfs statvfsinfo = {0, };
  int rv = 0;

  if (!(volume_name && buf)) 
  {
    return USAGE_ERROR;
  }

  fs = glfs_new (volume_name);
  if (!fs)
  {
    //fprintf (stderr, "glfs_new: returned NULL\n");
    syslog (LOG_ERR, "glfs_new: returned NULL");
    return GLFS_NEW_FAILURE;
  }

  if (server_name)
  {
    ret = glfs_set_volfile_server(fs, DEFAULT_TRANSPORT, server_name, DEFAULT_SERVER_PORT);
  }
  else
  {
    ret = glfs_set_volfile_server(fs, DEFAULT_TRANSPORT, DEFAULT_SERVER, DEFAULT_SERVER_PORT);
  }

  ret = glfs_set_logging (fs, "/tmp/libg.txt", 2);

  ret = glfs_init (fs);
  if (ret != 0) 
  {
    //fprintf (stderr, "glfs_init() failed with code %d\n", ret);
    syslog (LOG_ERR, "glfs_init() failed with code %d",ret);
    rv = GLFS_INIT_FAILURE;
    goto out;
  }

  /*fprintf (stdout, "waiting for 3 seconds to initialize\n");*/
  sleep (3);

  ret = glfs_statvfs (fs, "/", &statvfsinfo);
  if (ret == 0)
  {
    *buf = statvfsinfo;
  }
  else
  {
    //fprintf (stderr, "glfs_statvfs() failed with [%d:%s] for \"/\"\n", ret, strerror (errno));
    syslog (LOG_ERR, "glfs_statvfs() failed with [%d:%s] for \"/\"\n", ret, strerror (errno));
    rv = GLFS_STATVFS_FAILURE;
  }

 out:
  ret = glfs_fini (fs);
  if (ret != 0)
  {
    //fprintf (stderr, "glfs_fini() failed with code %d\n", ret);
    syslog (LOG_ERR, "glfs_fini() failed with code %d\n", ret);
  }

  return rv;
}

static PyObject *glfspy_statvfs (PyObject *self, PyObject *args)
{
  char *volume_name = NULL;
  char *server_name = NULL;
  int port = 0;
  char *transport = NULL;
  struct statvfs buf = {0, };
  int rv = 0;
#define USAGE_ERROR -1 
#define GLFS_NEW_FAILURE -2 
#define GLFS_INIT_FAILURE -3 
#define GLFS_STATVFS_FAILURE -4 
#define GLFS_FINI_FAILURE -5 

  StatvfsError = PyErr_NewException("statvfs.error", NULL, NULL);
  setlogmask (LOG_UPTO (LOG_DEBUG));
  openlog ("statvfs", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_LOCAL1);
  syslog (LOG_INFO, "Invoking glfspy_statvfs to get the volume utlization");
  if (!PyArg_ParseTuple (args, "s|ziz", &volume_name, &server_name, &port, &transport))
  {
    PyErr_SetString(StatvfsError, "Argument parsing failed");
    return NULL;
  }

  rv = get_volume_statvfs (volume_name, server_name, &buf);
  closelog ();
  //return Py_BuildValue("i", rv);
  if(rv == 0)
    return Py_BuildValue("{s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i,s:i}","f_bsize",buf.f_bsize,"f_frsize",buf.f_frsize,"f_blocks",buf.f_blocks,"f_bfree",buf.f_bfree,"f_bavail",buf.f_bavail,"f_files",buf.f_files,"f_ffree",buf.f_ffree,"f_favail",buf.f_favail,"f_fsid",buf.f_fsid,"f_flag",buf.f_flag,"f_namemax",buf.f_namemax);
  else {
    if(rv == USAGE_ERROR)
      PyErr_SetString(StatvfsError, "Usage error");
    if(rv == GLFS_NEW_FAILURE)
      PyErr_SetString(StatvfsError, "glfs_new() failed");
    if(rv == GLFS_INIT_FAILURE)
      PyErr_SetString(StatvfsError, "glfs_init() failed");
    if(rv == GLFS_STATVFS_FAILURE)
      PyErr_SetString(StatvfsError, "glfs_statvfs() failed");
    //return Py_BuildValue("i", rv);
    return NULL;
  }
}


static PyMethodDef glfspy_methods[] = {
  { "statvfs", (PyCFunction)glfspy_statvfs, METH_VARARGS, NULL },
  { NULL, NULL, 0, NULL }
};


PyMODINIT_FUNC initcapacity ()
{
  Py_InitModule3 ("capacity", glfspy_methods, "gluster gfapi top level extension module.");
}
