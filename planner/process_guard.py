"""Bounded subprocess tree; Windows Job Object closes all descendant processes."""
import ctypes
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


class WindowsJob:
    def __init__(self):
        from ctypes import wintypes as w
        class Basic(ctypes.Structure):
            _fields_ = [('process_time',ctypes.c_int64),('job_time',ctypes.c_int64),
                        ('flags',w.DWORD),('min_ws',ctypes.c_size_t),('max_ws',ctypes.c_size_t),
                        ('active',w.DWORD),('affinity',ctypes.c_size_t),('priority',w.DWORD),('scheduling',w.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(k,ctypes.c_uint64) for k in ('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
        class Extended(ctypes.Structure):
            _fields_ = [('basic',Basic),('io',IO),('process_memory',ctypes.c_size_t),
                        ('job_memory',ctypes.c_size_t),('peak_process',ctypes.c_size_t),('peak_job',ctypes.c_size_t)]
        self.api = ctypes.WinDLL('kernel32',use_last_error=True)
        self.api.CreateJobObjectW.argtypes=[ctypes.c_void_p,w.LPCWSTR]
        self.api.CreateJobObjectW.restype=w.HANDLE
        self.api.SetInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD]
        self.api.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE]
        self.api.CloseHandle.argtypes=[w.HANDLE]
        self.api.TerminateJobObject.argtypes=[w.HANDLE,w.UINT]
        self.api.QueryInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD,ctypes.c_void_p]
        self.handle=self.api.CreateJobObjectW(None,None)
        if not self.handle: raise ctypes.WinError(ctypes.get_last_error())
        info=Extended(); info.basic.flags=0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not self.api.SetInformationJobObject(self.handle,9,ctypes.byref(info),ctypes.sizeof(info)):
            self.close()
            raise ctypes.WinError(ctypes.get_last_error())

    def attach_and_resume(self, process):
        if not self.api.AssignProcessToJobObject(self.handle,int(process._handle)):
            raise ctypes.WinError(ctypes.get_last_error())
        resume=ctypes.WinDLL('ntdll').NtResumeProcess
        resume.argtypes=[ctypes.c_void_p]; resume.restype=ctypes.c_long
        if resume(int(process._handle)) != 0: raise RuntimeError('NtResumeProcess failed')

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle=None

    def terminate_and_wait(self, timeout=10):
        from ctypes import wintypes as w
        class Accounting(ctypes.Structure):
            _fields_ = [(n,ctypes.c_int64) for n in ('user','kernel','period_user','period_kernel')] + [
                (n,w.DWORD) for n in ('faults','total','active','terminated')]
        if not self.api.TerminateJobObject(self.handle,3):
            raise ctypes.WinError(ctypes.get_last_error())
        deadline=time.monotonic()+timeout
        while True:
            info=Accounting()
            if not self.api.QueryInformationJobObject(self.handle,1,ctypes.byref(info),ctypes.sizeof(info),None):
                raise ctypes.WinError(ctypes.get_last_error())
            if info.active==0:
                return {'confirmed':True,'active_processes':0,'total_processes':info.total}
            if time.monotonic()>=deadline:raise RuntimeError('owned Windows job did not terminate')
            time.sleep(.01)


def _posix_cleanup(process, timeout=10):
    # The leader can already have exited while descendants still own the group.
    try:os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    process.wait(timeout=timeout)
    deadline=time.monotonic()+timeout
    while True:
        try:os.killpg(process.pid,0)
        except ProcessLookupError:
            return {'confirmed':True,'active_processes':0,'group_disappeared':True}
        # On Linux, unreaped zombies are terminal and cannot execute or write.
        if Path('/proc/self/stat').exists():
            live=[]
            for entry in Path('/proc').iterdir():
                if not entry.name.isdigit():continue
                try:fields=(entry/'stat').read_text().rsplit(')',1)[1].split()
                except (FileNotFoundError,ProcessLookupError):continue
                if int(fields[2])==process.pid and fields[0] not in ('Z','X'):live.append(entry.name)
            if not live:
                return {'confirmed':True,'active_processes':0,'linux_non_zombie_group_members':0}
        if time.monotonic()>=deadline:raise RuntimeError('owned POSIX process group did not terminate')
        time.sleep(.01)


def _wait_posix_leader(process, deadline):
    # Keep the exited leader unreaped until killpg: its reserved PID prevents
    # an unrelated group from acquiring that numeric ID before cleanup.
    while True:
        result=os.waitid(os.P_PID,process.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT)
        if result is not None:
            return result.si_status if result.si_code==os.CLD_EXITED else -result.si_status
        if time.monotonic()>=deadline:raise subprocess.TimeoutExpired(process.args,0)
        time.sleep(min(.01,max(0,deadline-time.monotonic())))


def run_guarded(command, *, timeout, log_path, cwd=None, deadline_monotonic=None):
    if timeout<=0:raise ValueError('positive timeout required')
    if os.name!='nt' and not all(hasattr(os,n) for n in ('waitid','P_PID','WEXITED','WNOHANG','WNOWAIT','CLD_EXITED')):
        raise RuntimeError('POSIX waitid/WNOWAIT required to retain owned process-group identity')
    started=time.perf_counter()
    deadline=min(time.monotonic()+timeout,deadline_monotonic) if deadline_monotonic is not None else time.monotonic()+timeout
    process=None
    timed_out=False
    cleaned=False
    launch_options={}
    # CPython's Windows venv redirector spawns another interpreter. Launch the
    # same underlying interpreter directly while retaining its venv identity,
    # so authenticated worker-parent checks still refer to this live parent.
    # Other interpreters/commands are never substituted.
    if (os.name=='nt' and sys.implementation.name=='cpython' and sys.prefix!=sys.base_prefix
        and os.path.normcase(os.path.abspath(command[0]))==os.path.normcase(os.path.abspath(sys.executable))):
        base=getattr(sys,'_base_executable',None)
        if not base or not Path(base).is_file():raise RuntimeError('venv base interpreter unavailable')
        launch_options={'executable':base,'env':dict(os.environ,__PYVENV_LAUNCHER__=sys.executable)}
    job=WindowsJob() if os.name=='nt' else None
    try:
        with open(log_path,'wb') as log:
            process=subprocess.Popen(command,cwd=cwd,stdout=log,stderr=subprocess.STDOUT,
                creationflags=0x4 | subprocess.CREATE_NO_WINDOW if job else 0,
                start_new_session=not bool(job),**launch_options)
            if job: job.attach_and_resume(process)
            try:
                wait_seconds=max(0,deadline-time.monotonic())
                code=process.wait(timeout=wait_seconds) if job else _wait_posix_leader(process,deadline)
                if time.monotonic()>deadline:
                    timed_out=True;code=3
            except subprocess.TimeoutExpired:
                timed_out=True
                code=3
            execution_seconds=time.perf_counter()-started
            cleanup_started=time.perf_counter()
            cleanup=job.terminate_and_wait() if job else _posix_cleanup(process)
            cleaned=True
            process.wait(timeout=10)
            cleanup['seconds']=time.perf_counter()-cleanup_started
        return dict(exit_code=code,raw_exit_code=process.returncode,timed_out=timed_out,
                    argv=list(map(str,command)),launch_executable=str(launch_options.get('executable',command[0])),
                    venv_identity_preserved=bool(launch_options),
                    seconds=time.perf_counter()-started,execution_seconds=execution_seconds,
                    cleanup=cleanup,tree_guard='Windows_Job_Object' if job else 'POSIX_process_group')
    finally:
        try:
            if process is not None and not cleaned:
                if job:
                    job.terminate_and_wait()
                    if process.poll() is None:process.kill()  # also covers failed assignment
                    process.wait(timeout=10)
                else:_posix_cleanup(process)
        finally:
            if job:job.close()
