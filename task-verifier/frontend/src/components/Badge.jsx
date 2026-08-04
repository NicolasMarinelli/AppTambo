export default function Badge({ children, variant = "default" }) {
  const styles = {
    default: { background: "#1e2d45", color: "#8892a4" },
    success: { background: "rgba(0,212,170,0.15)", color: "#00d4aa" },
    danger:  { background: "rgba(255,77,109,0.15)", color: "#ff4d6d" },
    warning: { background: "rgba(255,180,0,0.15)", color: "#ffb400" },
    info:    { background: "rgba(96,165,250,0.15)", color: "#60a5fa" },
  };
  return (
    <span style={{
      ...styles[variant],
      padding: "3px 10px",
      borderRadius: "20px",
      fontSize: "12px",
      fontWeight: 600,
      fontFamily: "'Sora', sans-serif",
    }}>
      {children}
    </span>
  );
}