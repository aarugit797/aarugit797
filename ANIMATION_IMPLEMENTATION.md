# How the animated header works

The animation is not a hosted widget. `assets/profile-hero.svg` is a self-contained SVG image. The terminal text uses separate animated clipping rectangles, staggered by line. The portrait is already converted to ASCII characters, with one clipping rectangle for each visible row; each row wipes from left to right, with a blue cursor at the reveal edge. The final shell cursor blinks after the write-in sequence.

This technique is similar to public animated-terminal profile projects that use SVG SMIL `clipPath` wipes for ASCII portraits and staggered animations for information rows. Useful references:

- Abhishek's profile repository, including `header.svg` and `header-ascii.txt`: https://github.com/abhishek-pandey7/abhishek-pandey7
- A public implementation guide describing self-typing SVG portraits and animated information cards: https://www.avivashishta.com/blog/build-animated-github-profile-readme
- Open-source terminal profile template with animated ASCII portrait: https://github.com/Aiyzoxx/animated-terminal-profile

I could verify that Abhishek's README embeds his own `header.svg`, but I could not verify that he used any specific external generator. This version independently applies the documented SVG-animation approach to Aaradhya's own profile content and portrait.
