export default function ErrorState({ message, onRetry }) {
  return (
    <div className="error-state">
      <p className="error-message">{message || "Something went wrong."}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn btn-primary">
          Retry
        </button>
      )}
    </div>
  );
}
