# Book-open opener (Remotion)

Renders `book-open.mp4` — the storybook opening animation for the plans hub.

**Status:** shelved. The two-cover fold reads wrong physically (real books don't unfold
both covers flat outward from the spine). The live opener currently uses the Veo clip
(`../assets/book-open-veo-backup.mp4`). Revisit the page-flip physics here later.

## Assets (`public/`)
- `world-map.jpg` — the real map spread (farm | town), the resting frame.
- `cover.png` — leather front cover.
- `logo.png` — alpaca logo.

## Build
```
npm install
npx remotion render src/index.ts BookOpen out/book-open.mp4 --codec=h264 \
  --browser-executable="C:\Program Files\Google\Chrome\Application\chrome.exe"
```
The `--browser-executable` flag points at system Chrome because Remotion's bundled
Chrome-headless-shell download does not persist on this machine.

Then install the result:
```
cp out/book-open.mp4 ../assets/book-open.mp4
```

## Composition
`src/BookOpen.tsx` — 6s @ 30fps, 1280x720. Closed leather book on a desk; two covers
unfold from the centre spine (fading out past upright) to reveal the map spread beneath.
Timeline + geometry documented inline.
