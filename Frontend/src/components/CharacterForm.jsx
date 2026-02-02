export default function CharacterForm() {
  return (
    <div className="p-6 bg-gray-800 rounded-xl shadow-lg">
      <h3 className="text-xl font-bold mb-4 text-white">Character Design</h3>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-gray-400 text-sm mb-1">Name</label>
          <input type="text" className="w-full p-2 bg-gray-700 rounded border border-gray-600 text-white" />
        </div>
        <div>
          <label className="block text-gray-400 text-sm mb-1">Role</label>
          <input type="text" className="w-full p-2 bg-gray-700 rounded border border-gray-600 text-white" />
        </div>
      </div>
    </div>
  );
}
