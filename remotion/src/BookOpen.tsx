import React from "react";
import {
  AbsoluteFill,
  Img,
  staticFile,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";

/**
 * Book-open opener rendered with Remotion.
 * A closed leather book sits on the desk; its TWO covers unfold outward from the centre
 * spine (left cover swings left, right cover swings right), revealing the map spread beneath.
 * Real CSS 3D, physically-correct fold. Ends held on the full open book (the live rest frame).
 * 6s @ 30fps.
 */

const DESK = "#2a1d12";

export const BookOpen: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const t = frame / fps;

  const pageH = height * 0.8;
  const pageW = pageH * (1600 / 2400); // one page
  const ease = Easing.bezier(0.4, 0, 0.2, 1);

  // both covers unfold 0 -> ±180 (flat open) between 0.8s and 2.8s
  const open = interpolate(t, [0.8, 2.8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
  // open covers only to ~105° (past upright) so they never lie back down over the pages,
  // then fade them out as they pass upright — the map spread is revealed cleanly beneath.
  const leftCoverRot = -105 * open; // swings left
  const rightCoverRot = 105 * open; // swings right
  const coverOpacity = interpolate(t, [1.9, 2.6], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // a thin settle + push-in of the whole book
  const bookScale = interpolate(t, [0, 0.8, 2.8, 6.0], [0.9, 0.93, 0.98, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });
  const bookTilt = interpolate(t, [0, 2.8], [8, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: ease,
  });

  // shadow the spread while the covers are still up (before they lie flat)
  const revealShade = interpolate(t, [0.8, 2.4], [0.55, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const coverFace = (side: "left" | "right"): React.CSSProperties => ({
    position: "absolute",
    inset: 0,
    backfaceVisibility: "hidden",
    borderRadius: 6,
    overflow: "hidden",
    boxShadow: "0 0 0 3px #43331f, 0 18px 40px rgba(0,0,0,.5)",
  });

  // the leather cover art is a full front; each half shows its side of that art
  const coverArt = (side: "left" | "right") => (
    <div style={{ width: "100%", height: "100%", overflow: "hidden", position: "relative" }}>
      <Img
        src={staticFile("cover.png")}
        style={{
          position: "absolute",
          top: 0,
          left: side === "left" ? 0 : `-${pageW}px`,
          width: pageW * 2,
          height: pageH,
          maxWidth: "none",
          objectFit: "cover",
        }}
      />
    </div>
  );

  return (
    <AbsoluteFill style={{ background: `radial-gradient(120% 100% at 50% 42%, #3a2817 0%, ${DESK} 68%, #1b120a 100%)` }}>
      <AbsoluteFill style={{ opacity: 0.1, backgroundImage: "repeating-linear-gradient(92deg, rgba(0,0,0,.4) 0 2px, transparent 2px 7px)" }} />

      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", perspective: 2600 }}>
        <div
          style={{
            position: "relative",
            width: pageW * 2,
            height: pageH,
            transformStyle: "preserve-3d",
            transform: `rotateX(${bookTilt}deg) scale(${bookScale})`,
            filter: "drop-shadow(0 42px 62px rgba(0,0,0,.62))",
          }}
        >
          {/* the OPEN map spread beneath: left = farm, right = town */}
          <div style={{ position: "absolute", inset: 0, display: "flex", borderRadius: 6, overflow: "hidden",
            boxShadow: "0 0 0 2px #efe6d2,0 0 0 5px #e0d4b8,0 0 0 9px #b58a52,0 0 0 13px #6e5230,0 0 0 15px #43331f" }}>
            <div style={{ width: pageW, height: pageH, overflow: "hidden" }}>
              <Img src={staticFile("world-map.jpg")} style={{ width: pageW * 2, height: pageH, maxWidth: "none", display: "block" }} />
            </div>
            <div style={{ width: pageW, height: pageH, overflow: "hidden" }}>
              <Img src={staticFile("world-map.jpg")} style={{ width: pageW * 2, height: pageH, maxWidth: "none", marginLeft: -pageW, display: "block" }} />
            </div>
            <div style={{ position: "absolute", left: "50%", top: 0, width: 64, height: "100%", transform: "translateX(-50%)",
              background: "linear-gradient(90deg,transparent,rgba(60,40,20,.42) 46%,rgba(60,40,20,.5) 50%,rgba(60,40,20,.42) 54%,transparent)" }} />
            {/* darken the spread while covers are up */}
            <div style={{ position: "absolute", inset: 0, background: `rgba(15,9,3,${revealShade})` }} />
          </div>

          {/* LEFT cover: hinged at the centre spine, swings LEFT */}
          <div style={{ position: "absolute", left: 0, top: -pageH * 0.02, width: pageW, height: pageH * 1.04, opacity: coverOpacity,
            transformOrigin: "right center", transform: `rotateY(${leftCoverRot}deg)`, transformStyle: "preserve-3d", zIndex: 40 }}>
            <div style={coverFace("left")}>{coverArt("left")}</div>
            <div style={{ position: "absolute", inset: 0, backfaceVisibility: "hidden", transform: "rotateY(180deg)", borderRadius: 6,
              background: "linear-gradient(135deg,#e9dcc0,#d8c8a4)", boxShadow: "inset 0 0 70px rgba(120,90,50,.3)" }} />
          </div>

          {/* RIGHT cover: hinged at the centre spine, swings RIGHT */}
          <div style={{ position: "absolute", left: pageW, top: -pageH * 0.02, width: pageW, height: pageH * 1.04, opacity: coverOpacity,
            transformOrigin: "left center", transform: `rotateY(${rightCoverRot}deg)`, transformStyle: "preserve-3d", zIndex: 40 }}>
            <div style={coverFace("right")}>{coverArt("right")}</div>
            <div style={{ position: "absolute", inset: 0, backfaceVisibility: "hidden", transform: "rotateY(180deg)", borderRadius: 6,
              background: "linear-gradient(135deg,#e9dcc0,#d8c8a4)", boxShadow: "inset 0 0 70px rgba(120,90,50,.3)" }} />
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
