import cowNavbarImage from "../assets/cow-navbar.jpg";

interface CowHeadIconProps {
  size?: number;
  className?: string;
}

export function CowHeadIcon({ size = 32, className }: CowHeadIconProps) {
  return (
    <img
      src={cowNavbarImage}
      alt="Logo vaca"
      className={className}
      style={{ width: size, height: size, objectFit: "cover", borderRadius: "50%" }}
    />
  );
}
