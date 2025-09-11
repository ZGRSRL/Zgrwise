export default function SettingsPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <ul className="mt-4 space-y-2 text-sm">
        <li>• Obsidian export path</li>
        <li>• API base URL & key</li>
        <li>• RSS polling interval</li>
      </ul>
    </div>
  );
}