export default function Loader({ message = "Loading..." }) {
  return (
    <div className="loader">
      <div className="spinner" />
      <p>{message}</p>
    </div>
  );
}
