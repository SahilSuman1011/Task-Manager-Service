import { useState, useEffect } from 'react';
import { taskAPI } from './services/api';
import TaskForm from './components/TaskForm';
import TaskItem from './components/TaskItem';
import FilterBar from './components/FilterBar';

function App() {
  const [tasks, setTasks] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    search: '',
    ordering: '-created_at'
  });
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
    current_page: 1
  });

  useEffect(() => {
    fetchTasks();
    fetchSummary();
  }, [filters]);

  const fetchTasks = async (page = 1) => {
    setLoading(true);
    setError(null);
    try {
      const params = {
        page,
        ...Object.fromEntries(
          Object.entries(filters).filter(([key, value]) => value && value !== 'all')
        )
      };
      
      const data = await taskAPI.getTasks(params);
      setTasks(data.results);
      setPagination({
        count: data.count,
        next: data.next,
        previous: data.previous,
        current_page: page
      });
    } catch (err) {
      setError('Failed to fetch tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const data = await taskAPI.getSummary();
      setSummary(data);
    } catch (err) {
      console.error('Failed to fetch summary:', err);
    }
  };

  const handleCreateTask = async (taskData) => {
    try {
      await taskAPI.createTask(taskData);
      setShowForm(false);
      fetchTasks();
      fetchSummary();
    } catch (err) {
      setError('Failed to create task');
    }
  };

  const handleUpdateTask = async (taskData) => {
    try {
      await taskAPI.updateTask(editingTask.id, taskData);
      setEditingTask(null);
      setShowForm(false);
      fetchTasks();
      fetchSummary();
    } catch (err) {
      setError('Failed to update task');
    }
  };

  const handleDeleteTask = async (id) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    
    try {
      await taskAPI.deleteTask(id);
      fetchTasks();
      fetchSummary();
    } catch (err) {
      setError('Failed to delete task');
    }
  };

  const handleStatusChange = async (id, newStatus) => {
    try {
      if (newStatus === 'done') {
        await taskAPI.markDone(id);
      } else if (newStatus === 'in_progress') {
        await taskAPI.markInProgress(id);
      }
      fetchTasks();
      fetchSummary();
    } catch (err) {
      setError('Failed to update status');
    }
  };

  const handleEdit = (task) => {
    setEditingTask(task);
    setShowForm(true);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingTask(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Task Manager</h1>
          <p className="text-gray-600">Organize your tasks efficiently</p>
        </div>

        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="text-2xl font-bold text-gray-800">{summary.total_tasks}</div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
            <div className="bg-slate-100 p-4 rounded-lg shadow">
              <div className="text-2xl font-bold text-slate-800">{summary.todo_count}</div>
              <div className="text-sm text-slate-600">To Do</div>
            </div>
            <div className="bg-blue-100 p-4 rounded-lg shadow">
              <div className="text-2xl font-bold text-blue-800">{summary.in_progress_count}</div>
              <div className="text-sm text-blue-600">In Progress</div>
            </div>
            <div className="bg-green-100 p-4 rounded-lg shadow">
              <div className="text-2xl font-bold text-green-800">{summary.done_count}</div>
              <div className="text-sm text-green-600">Done</div>
            </div>
            <div className="bg-red-100 p-4 rounded-lg shadow">
              <div className="text-2xl font-bold text-red-800">{summary.overdue_count}</div>
              <div className="text-sm text-red-600">Overdue</div>
            </div>
            <div className="bg-orange-100 p-4 rounded-lg shadow">
              <div className="text-2xl font-bold text-orange-800">{summary.high_priority_count}</div>
              <div className="text-sm text-orange-600">High Priority</div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {!showForm && (
          <button onClick={() => setShowForm(true)} className="mb-6 bg-primary-600 text-white py-3 px-6 rounded-lg hover:bg-primary-700 transition-colors font-semibold shadow-md">
            + Create New Task
          </button>
        )}

        {showForm && (
          <div className="mb-6">
            <TaskForm onSubmit={editingTask ? handleUpdateTask : handleCreateTask} initialTask={editingTask} onCancel={handleCancelForm} />
          </div>
        )}

        <FilterBar filters={filters} onFilterChange={setFilters} onClearFilters={() => setFilters({ status: 'all', priority: 'all', search: '', ordering: '-created_at' })} />

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            <p className="mt-4 text-gray-600">Loading tasks...</p>
          </div>
        )}

        {!loading && tasks.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-500 text-lg">No tasks found</p>
          </div>
        )}

        {!loading && tasks.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {tasks.map(task => (
                <TaskItem key={task.id} task={task} onEdit={handleEdit} onDelete={handleDeleteTask} onStatusChange={handleStatusChange} />
              ))}
            </div>

            {pagination.count > 10 && (
              <div className="flex justify-center items-center gap-4 mt-6">
                <button onClick={() => fetchTasks(pagination.current_page - 1)} disabled={!pagination.previous} className={`px-4 py-2 rounded-lg font-semibold ${pagination.previous ? 'bg-primary-600 text-white hover:bg-primary-700' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}>
                  Previous
                </button>
                <span className="text-gray-600">Page {pagination.current_page} of {Math.ceil(pagination.count / 10)}</span>
                <button onClick={() => fetchTasks(pagination.current_page + 1)} disabled={!pagination.next} className={`px-4 py-2 rounded-lg font-semibold ${pagination.next ? 'bg-primary-600 text-white hover:bg-primary-700' : 'bg-gray-300 text-gray-500 cursor-not-allowed'}`}>
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default App;