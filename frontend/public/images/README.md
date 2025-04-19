# Public Image Assets

This directory contains static image assets that are publicly accessible and used across the application.

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

Reference these images in HTML using:
```html
<img src="/images/icon-example-32.png" alt="Example icon">
```

Or in CSS using:
```css
.element {
    background-image: url('/images/bg-header-large.jpg');
}
``` 