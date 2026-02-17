import React from 'react';

export function CategoryFilter({ categories, selectedCategory, onSelect }) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Categories</h2>
      <div className="flex gap-2 flex-wrap">
        <button
          onClick={() => onSelect(null)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
            selectedCategory === null
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Videos ({categories.reduce((sum, cat) => sum + cat.video_count, 0)})
        </button>
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => onSelect(category.id)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              selectedCategory === category.id
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            style={{
              ...(selectedCategory === category.id ? {} : { backgroundColor: `${category.color}20`, color: category.color })
            }}
          >
            {category.name} ({category.video_count})
          </button>
        ))}
      </div>
    </div>
  );
}