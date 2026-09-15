import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface BackButtonProps {
  fallback?: string;
  label?: string;
}

export default function BackButton({
  fallback = "/dashboard",
  label = "Back",
}: BackButtonProps) {
  const navigate = useNavigate();

  const handleBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate(fallback);
    }
  };

  return (
    <button
      type="button"
      onClick={handleBack}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "8px",
        padding: "9px 14px",
        border: "1px solid #d0d5dd",
        borderRadius: "10px",
        background: "#ffffff",
        color: "#344054",
        fontSize: "13px",
        fontWeight: 700,
        cursor: "pointer",
        transition: "all 0.2s ease",
        marginBottom: "18px",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background = "#f9fafb";
        e.currentTarget.style.transform = "translateX(-2px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background = "#ffffff";
        e.currentTarget.style.transform = "translateX(0)";
      }}
    >
      <ArrowLeft size={16} />
      {label}
    </button>
  );
}