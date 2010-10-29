# common utilities for all CDE tests
import os, time
from subprocess import *

CDE_BIN = "/home/pgbovine/CDE/strace-4.5.20/cde"
CDE_EXEC = "./cde-exec"

# careful!!!
def clear_cde_root():
  os.system('rm -rf cde*')
  time.sleep(0.3) # to give os.system some time to work :)

def generic_lib_checks():
  assert os.path.islink('cde-root/lib/libc.so.6')
  assert os.readlink('cde-root/lib/libc.so.6') == 'libc-2.8.so'

def run_cde(argv, silent=False):
  (stdout, stderr) = Popen([CDE_BIN] + argv, stdout=PIPE, stderr=PIPE).communicate()
  if not silent:
    if stderr: 
      print "stderr:", stderr
  return (stdout, stderr)

def run_and_cmp_cde_exec(argv, prev_stdout, prev_stderr):
  # to make for a tougher test, move the entire directory to /tmp
  # and try to do a cde-exec run
  full_pwd = os.getcwd()
  full_pwd_renamed = full_pwd + '-renamed'
  cur_dirname = os.path.basename(full_pwd)
  tmp_test_dir = "/tmp/" + cur_dirname

  # careful with these commands! use 'finally' to clean up even after
  # exceptions!
  try:
    (stdout, stderr) = Popen(["rm", "-rf", tmp_test_dir], stdout=PIPE, stderr=PIPE).communicate()
    assert not stdout and not stderr
    (stdout, stderr) = Popen(["cp", "-aR", full_pwd, "/tmp"], stdout=PIPE, stderr=PIPE).communicate()
    assert not stdout and not stderr

    # rename full_pwd to make it impossible for the new version in /tmp
    # to reference already-existing files in full_pwd (a harsher test!)
    try:
      os.rename(full_pwd, full_pwd_renamed)

      # run the cde-exec test in tmp_test_dir
      os.chdir(tmp_test_dir)
      (stdout, stderr) = Popen([CDE_EXEC] + argv, stdout=PIPE, stderr=PIPE).communicate()
      assert stdout == prev_stdout
      assert stderr == prev_stderr

    finally:
      # rename it back to be nice :)
      os.rename(full_pwd_renamed, full_pwd)
      os.chdir(full_pwd) # make sure to chdir back!!!

  finally:
    # remove the version in tmp
    (stdout, stderr) = Popen(["rm", "-rf", tmp_test_dir], stdout=PIPE, stderr=PIPE).communicate()


def generic_test_runner(argv, checker_func):
  clear_cde_root()
  (stdout, stderr) = run_cde(argv)

  checker_func()

  generic_lib_checks()

  run_and_cmp_cde_exec(argv, stdout, stderr)

