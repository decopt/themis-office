import ThemisScene from "@/components/3d/ThemisScene";
import HUD from "@/components/HUD";
import AmbientMusic from "@/components/AmbientMusic";

const Index = () => {
  return (
    <div className="relative w-screen h-screen overflow-hidden bg-background">
      <ThemisScene />
      <HUD />
      <AmbientMusic />
    </div>
  );
};

export default Index;
