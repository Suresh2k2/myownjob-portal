export default function EmptyState({ message, actionLabel, onAction }) {
  return (
    <div className="empty-state">
      <p>{message || "Nothing here yet."}</p>
      {actionLabel && onAction && (
        <button onClick={onAction} className="btn btn-primary">
          {actionLabel}
        </button>
      )}
    </div>
  );
}
