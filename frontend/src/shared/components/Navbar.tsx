import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <nav
      style={{
        padding: "1rem",
        background: "#222",
        color: "white",
        display: "flex",
        gap: "1rem",
      }}
    >
      <Link to="/" style={{ color: "white" }}>Dashboard</Link>
      <Link to="/products" style={{ color: "white" }}>Products</Link>
      <Link to="/login" style={{ color: "white" }}>Login</Link>
    </nav>
  );
}