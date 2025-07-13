"""
Thread Manager
Manages background threads and tasks for plugins and application components.
"""

import logging
import threading
from typing import Dict, Callable, Any, Optional
from concurrent.futures import ThreadPoolExecutor, Future
from PySide6.QtCore import QObject, QThread, QTimer, Signal, QMutex


class ManagedThread(QThread):
    """Custom QThread with monitoring capabilities."""
    
    # Signals
    task_started = Signal(str)  # thread_name
    task_finished = Signal(str, object)  # thread_name, result
    task_error = Signal(str, str)  # thread_name, error_message
    
    def __init__(self, name: str, target: Callable, *args, **kwargs):
        super().__init__()
        
        self.thread_name = name
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.result = None
        self.error = None
        self.is_running = False
        
    def run(self):
        """Execute the target function."""
        try:
            self.is_running = True
            self.task_started.emit(self.thread_name)
            
            self.result = self.target(*self.args, **self.kwargs)
            self.task_finished.emit(self.thread_name, self.result)
            
        except Exception as e:
            self.error = str(e)
            self.task_error.emit(self.thread_name, self.error)
            
        finally:
            self.is_running = False


class ThreadManager(QObject):
    """Manages all background threads and tasks."""
    
    # Signals
    thread_started = Signal(str)  # thread_name
    thread_finished = Signal(str, object)  # thread_name, result
    thread_error = Signal(str, str)  # thread_name, error
    threads_changed = Signal()  # thread count changed
    
    def __init__(self, max_workers: int = 10):
        super().__init__()
        
        self.logger = logging.getLogger("ThreadManager")
        self.max_workers = max_workers
        
        # Thread tracking
        self.active_threads: Dict[str, ManagedThread] = {}
        self.thread_executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures: Dict[str, Future] = {}
        
        # Monitoring
        self.mutex = QMutex()
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self._monitor_threads)
        self.monitor_timer.start(1000)  # Check every second
        
        # Statistics
        self.total_threads_started = 0
        self.total_threads_completed = 0
        self.total_threads_failed = 0
    
    def start_thread(self, name: str, target: Callable, *args, **kwargs) -> bool:
        """Start a new managed thread."""
        try:
            with QMutex():  # Thread-safe operation
                if name in self.active_threads:
                    self.logger.warning(f"Thread '{name}' already exists")
                    return False
                
                # Create and start thread
                thread = ManagedThread(name, target, *args, **kwargs)
                
                # Connect signals
                thread.task_started.connect(self._on_thread_started)
                thread.task_finished.connect(self._on_thread_finished)
                thread.task_error.connect(self._on_thread_error)
                thread.finished.connect(lambda: self._cleanup_thread(name))
                
                # Store and start
                self.active_threads[name] = thread
                thread.start()
                
                self.total_threads_started += 1
                self.threads_changed.emit()
                
                self.logger.info(f"Started thread: {name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start thread '{name}': {e}")
            return False
    
    def start_task(self, name: str, target: Callable, *args, **kwargs) -> bool:
        """Start a task using ThreadPoolExecutor."""
        try:
            if name in self.futures:
                self.logger.warning(f"Task '{name}' already exists")
                return False
            
            # Submit task to executor
            future = self.thread_executor.submit(target, *args, **kwargs)
            self.futures[name] = future
            
            # Add callback for completion
            future.add_done_callback(lambda f: self._task_completed(name, f))
            
            self.total_threads_started += 1
            self.threads_changed.emit()
            
            self.logger.info(f"Started task: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start task '{name}': {e}")
            return False
    
    def stop_thread(self, name: str) -> bool:
        """Stop a specific thread."""
        try:
            if name in self.active_threads:
                thread = self.active_threads[name]
                if thread.isRunning():
                    thread.requestInterruption()
                    thread.wait(5000)  # Wait up to 5 seconds
                    
                    if thread.isRunning():
                        thread.terminate()
                        thread.wait(1000)
                    
                self._cleanup_thread(name)
                return True
                
            elif name in self.futures:
                future = self.futures[name]
                future.cancel()
                del self.futures[name]
                self.threads_changed.emit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to stop thread '{name}': {e}")
            
        return False
    
    def get_thread_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get status information for a specific thread."""
        if name in self.active_threads:
            thread = self.active_threads[name]
            return {
                "name": name,
                "type": "QThread",
                "running": thread.isRunning(),
                "started": thread.isStarted(),
                "finished": thread.isFinished()
            }
        
        elif name in self.futures:
            future = self.futures[name]
            return {
                "name": name,
                "type": "Future",
                "running": future.running(),
                "done": future.done(),
                "cancelled": future.cancelled()
            }
        
        return None
    
    def get_all_threads_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active threads."""
        status = {}
        
        for name in self.active_threads:
            status[name] = self.get_thread_status(name)
        
        for name in self.futures:
            status[name] = self.get_thread_status(name)
        
        return status
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get thread manager statistics."""
        return {
            "active_threads": len(self.active_threads),
            "active_tasks": len(self.futures),
            "total_started": self.total_threads_started,
            "total_completed": self.total_threads_completed,
            "total_failed": self.total_threads_failed,
            "max_workers": self.max_workers
        }
    
    def shutdown_all_threads(self) -> None:
        """Shutdown all active threads and tasks."""
        self.logger.info("Shutting down all threads...")
        
        # Stop monitoring
        self.monitor_timer.stop()
        
        # Stop all QThreads
        for name in list(self.active_threads.keys()):
            self.stop_thread(name)
        
        # Cancel all futures
        for name, future in list(self.futures.items()):
            future.cancel()
        
        # Shutdown executor
        self.thread_executor.shutdown(wait=True)
        
        self.logger.info("All threads shut down")
    
    def _on_thread_started(self, thread_name: str):
        """Handle thread started signal."""
        self.thread_started.emit(thread_name)
        
    def _on_thread_finished(self, thread_name: str, result: Any):
        """Handle thread finished signal."""
        self.total_threads_completed += 1
        self.thread_finished.emit(thread_name, result)
        
    def _on_thread_error(self, thread_name: str, error: str):
        """Handle thread error signal."""
        self.total_threads_failed += 1
        self.thread_error.emit(thread_name, error)
        self.logger.error(f"Thread '{thread_name}' failed: {error}")
    
    def _cleanup_thread(self, name: str):
        """Clean up a finished thread."""
        if name in self.active_threads:
            del self.active_threads[name]
            self.threads_changed.emit()
    
    def _task_completed(self, name: str, future: Future):
        """Handle task completion."""
        try:
            if future.cancelled():
                self.logger.info(f"Task '{name}' was cancelled")
            elif future.exception():
                self.total_threads_failed += 1
                error = str(future.exception())
                self.thread_error.emit(name, error)
                self.logger.error(f"Task '{name}' failed: {error}")
            else:
                self.total_threads_completed += 1
                result = future.result()
                self.thread_finished.emit(name, result)
                self.logger.info(f"Task '{name}' completed")
                
        finally:
            if name in self.futures:
                del self.futures[name]
                self.threads_changed.emit()
    
    def _monitor_threads(self):
        """Monitor thread health and clean up dead threads."""
        dead_threads = []
        
        for name, thread in self.active_threads.items():
            if thread.isFinished() and not thread.isRunning():
                dead_threads.append(name)
        
        for name in dead_threads:
            self._cleanup_thread(name)
