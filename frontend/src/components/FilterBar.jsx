const FilterBar = ({ filters, onFilterChange, onClearFilters }) => {
  const handleChange = (e) => {
    const { name, value } = e.target;
    onFilterChange({
      ...filters,
      [name]: value
    });
  };

  const hasActiveFilters = Object.values(filters).some(val => val !== '' && val !== 'all');

  return (
    <div className="bg-white p-4 rounded-lg shadow-md mb-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">Status</label>
          <select name="status" value={filters.status || 'all'} onChange={handleChange} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option value="all">All Statuses</option>
            <option value="todo">To Do</option>
            <option value="in_progress">In Progress</option>
            <option value="done">Done</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">Priority</label>
          <select name="priority" value={filters.priority || 'all'} onChange={handleChange} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option value="all">All Priorities</option>
            <option value="1">1 - Lowest</option>
            <option value="2">2 - Low</option>
            <option value="3">3 - Medium</option>
            <option value="4">4 - High</option>
            <option value="5">5 - Highest</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">Search</label>
          <input type="text" name="search" value={filters.search || ''} onChange={handleChange} placeholder="Search tasks..." className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-1">Sort By</label>
          <select name="ordering" value={filters.ordering || '-created_at'} onChange={handleChange} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option value="-created_at">Newest First</option>
            <option value="created_at">Oldest First</option>
            <option value="-priority">Highest Priority</option>
            <option value="priority">Lowest Priority</option>
          </select>
        </div>
      </div>
      {hasActiveFilters && (
        <div className="mt-3 flex justify-end">
          <button onClick={onClearFilters} className="text-sm text-primary-600 hover:text-primary-800 font-semibold">Clear All Filters</button>
        </div>
      )}
    </div>
  );
};

export default FilterBar;