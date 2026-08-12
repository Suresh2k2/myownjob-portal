const STATUS_COLORS = {
  pending: { bg: "#fef3c7", color: "#92400e" },
  reviewed: { bg: "#dbeafe", color: "#1e40af" },
  shortlisted: { bg: "#d1fae5", color: "#065f46" },
  rejected: { bg: "#fee2e2", color: "#991b1b" },
  accepted: { bg: "#d1fae5", color: "#065f46" },
};

export default function StatusBadge({ status }) {
  const colors = STATUS_COLORS[status] || { bg: "#f1f5f9", color: "#475569" };
  return (
    <span
      className="status-badge"
      style={{ backgroundColor: colors.bg, color: colors.color }}
    >
      {status}
    </span>
  );
}
