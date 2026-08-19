import cowLoginImage from "../assets/cow-login.jpg";

export function CowHero({ className }: { className?: string }) {
  return <img src={cowLoginImage} alt="Vaca del tambo" className={className} />;
}
