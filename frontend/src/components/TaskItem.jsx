const TaskItem = ({ task, onEdit, onDelete, onStatusChange }) => {
  const getPriorityColor = (priority) => {
    const colors = {
      1: 'bg-gray-100 text-gray-800',
      2: 'bg-blue-100 text-blue-800',
      3: 'bg-yellow-100 text-yellow-800',
      4: 'bg-orange-100 text-orange-800',
      5: 'bg-red-100 text-red-800',
    };
    return colors[priority] || colors[3];
  };

  const getStatusColor = (status) => {
    const colors = {
      todo: 'bg-slate-100 text-slate-800',
      in_progress: 'bg-blue-100 text-blue-800',
      done: 'bg-green-100 text-green-800',
    };
    return colors[status] || colors.todo;
  };

  const formatDate = (dateString) => {
    if (!dateString) return null;
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-lg font-semibold text-gray-800 flex-1">
          {task.title}
        </h3>
        <div className="flex gap-2">
          <span className={`px-2 py-1 rounded text-xs font-semibold ${getPriorityColor(task.priority)}`}>
            P{task.priority}
          </span>
          <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusColor(task.status)}`}>
            {task.status.replace('_', ' ').toUpperCase()}
          </span>
        </div>
      </div>

      {task.description && (
        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
          {task.description}
        </p>
      )}

      <div className="flex flex-wrap gap-2 text-xs text-gray-500 mb-3">
        <span>Created: {formatDate(task.created_at)}</span>
        {task.due_date && (
          <span className={task.is_overdue ? 'text-red-600 font-semibold' : ''}>
            Due: {formatDate(task.due_date)}
            {task.is_overdue && ' (Overdue!)'}
          </span>
        )}
      </div>

      <div className="flex gap-2">
        {task.status !== 'done' && (
          <>
            {task.status === 'todo' && (
              <button
                onClick={() => onStatusChange(task.id, 'in_progress')}
                className="flex-1 bg-blue-500 text-white py-1 px-3 rounded text-sm hover:bg-blue-600"
              >
                Start
              </button>
            )}
            <button
              onClick={() => onStatusChange(task.id, 'done')}
              className="flex-1 bg-green-500 text-white py-1 px-3 rounded text-sm hover:bg-green-600"
            >
              Complete
            </button>
          </>
        )}
        <button
          onClick={() => onEdit(task)}
          className="flex-1 bg-gray-200 text-gray-700 py-1 px-3 rounded text-sm hover:bg-gray-300"
        >
          Edit
        </button>
        <button
          onClick={() => onDelete(task.id)}
          className="flex-1 bg-red-500 text-white py-1 px-3 rounded text-sm hover:bg-red-600"
        >
          Delete
        </button>
      </div>
    </div>
  );
};

export default TaskItem;