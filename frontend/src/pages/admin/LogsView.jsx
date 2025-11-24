const mockLogs = [
  {
    id: 1,
    admin: "admin@layr.com",
    action: "UPDATE_STOCK",
    detail: { article_id: "108775015", from: 45, to: 60 },
    timestamp: "2025-11-20T10:25:00Z"
  },
  {
    id: 2,
    admin: "analyst@layr.com",
    action: "REFRESH_MV",
    detail: { target: "mv_daily_sales" },
    timestamp: "2025-11-20T09:15:00Z"
  }
];

export default function LogsView() {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-semibold text-gray-900">Admin Logs</h2>
        <p className="text-gray-500 text-sm">Track critical changes made by administrators.</p>
      </div>

      <div className="bg-white border rounded-xl overflow-hidden shadow-sm">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-left text-gray-600 uppercase text-xs tracking-wide">
            <tr>
              <th className="px-4 py-3">Log ID</th>
              <th className="px-4 py-3">Admin</th>
              <th className="px-4 py-3">Action</th>
              <th className="px-4 py-3">Details</th>
              <th className="px-4 py-3">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {mockLogs.map(log => (
              <tr key={log.id} className="border-t">
                <td className="px-4 py-3 font-mono text-xs text-gray-500">{log.id}</td>
                <td className="px-4 py-3 text-gray-800">{log.admin}</td>
                <td className="px-4 py-3 text-gray-600">{log.action}</td>
                <td className="px-4 py-3">
                  <pre className="text-xs bg-gray-50 border rounded p-2 overflow-auto">
{JSON.stringify(log.detail, null, 2)}
                  </pre>
                </td>
                <td className="px-4 py-3 text-gray-600">{new Date(log.timestamp).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-gray-500">
        * Replace mock data with /admin/logs API once backend auditing is available.
      </p>
    </div>
  );
}

