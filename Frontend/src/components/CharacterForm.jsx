export default function CharacterForm() {
  return (
    <div className="mt-4 border-t border-zinc-700 pt-4">
      <h4 className="text-lg font-medium text-zinc-300 mb-3">Character Details</h4>
      <input className="w-full p-2 mb-3 bg-zinc-800 border border-zinc-700 rounded text-white" placeholder="Character Name" />
      <textarea className="w-full p-2 bg-zinc-800 border border-zinc-700 rounded text-white min-h-[80px]" placeholder="Character Description" />
    </div>
  );
}
