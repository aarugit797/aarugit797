# Terminal animation

The README embeds `assets/profile-hero.svg` directly. The SVG contains its own SMIL animations, so no JavaScript, browser runtime, external animation service, or API is required.

On a fresh image load, the terminal text is revealed from left to right, one line at a time. In parallel, the ASCII portrait is drawn row by row from the top down. Small blue cursors lead each portrait row, then the terminal prompt cursor blinks after the sequence finishes.

The animation is intended to play once as the SVG loads, then hold on the complete portrait and terminal details. The main logic is implemented through SVG `clipPath` rectangles and `<animate>` elements. GitHub profile READMEs can display self-contained SVG images with SMIL animation; the SVG must be embedded as an image, as this README does.

`assets/profile-hero-base.svg` preserves the fully drawn static art as a source copy. The previous `profile-hero.gif` is retained as a lightweight animated preview, but the README now uses the SVG for its row-by-row reveal.
