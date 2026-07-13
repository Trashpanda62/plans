import React from "react";
import { Composition } from "remotion";
import { BookOpen } from "./BookOpen";

const FPS = 30;
const DURATION = 6.0; // seconds

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="BookOpen"
      component={BookOpen}
      durationInFrames={Math.round(DURATION * FPS)}
      fps={FPS}
      width={1280}
      height={720}
    />
  );
};
