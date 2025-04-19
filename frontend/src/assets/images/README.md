# Application Image Assets

This directory contains image assets used by the application components and stylesheets.

## Naming Conventions

- Use lowercase letters, numbers, and hyphens only
- Follow the pattern: `[category]-[name]-[size].[extension]`
- Example: `icon-home-32.png`, `bg-header-large.jpg`, `logo-main-200.svg`

## Categories

- `icon-`: UI icons and action symbols
- `logo-`: Brand and partner logos
- `bg-`: Background images
- `banner-`: Banner images for headers and promotional areas
- `photo-`: Photographs and complex images
- `illus-`: Illustrations and diagrams

## Sizes (when applicable)

- `small`: For smaller viewports/mobile displays
- `medium`: For medium viewports/tablet displays
- `large`: For larger viewports/desktop displays
- Numeric values indicate dimensions (usually width) in pixels: `32`, `64`, `200`

## File Types

- Use `.svg` for vector graphics when possible
- Use `.png` for raster graphics requiring transparency
- Use `.jpg` or `.webp` for photographs and complex images
- Keep file sizes as small as possible while maintaining necessary quality

## Usage

Import and use these images in React components:

```jsx
import logoImg from '../assets/images/logo-main-200.svg';

function Header() {
  return (
    <header>
      <img src={logoImg} alt="Logo" />
    </header>
  );
}
```

Or reference them in CSS/SCSS files:

```css
.header {
  background-image: url('../assets/images/bg-header-large.jpg');
}
``` 